"""群发 N 个同类供应商 — 严格限流 12 秒间隔，避免风控

用法：
  python broadcast-to-suppliers.py --category 面料商 --message "DRS-0429 雪纺 5 月底能到货回我"
  python broadcast-to-suppliers.py --category 面料商 --message "..." --dry-run
"""

import os, sys, json, argparse, subprocess, time
from datetime import datetime

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SEND_SCRIPT = os.path.join(PROJECT_ROOT, "skills", "wxauto-supplier-bridge", "scripts", "send-to-supplier.py")

INTERVAL_SECONDS = 12       # 间隔 12 秒（5 条/分钟）
MAX_BROADCAST = 20          # 单次群发最多 20 个


def fetch_suppliers_by_category(category: str) -> list:
    base = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
    table = os.environ.get("TABLE_SUPPLIERS", "")
    r = subprocess.run(
        [LARK_CLI, "base", "+record-list",
         "--base-token", base, "--table-id", table,
         "--limit", "200", "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    if r.returncode != 0:
        raise RuntimeError(f"拉表失败: {r.stderr[:200]}")
    d = json.loads(r.stdout)
    fields = d["data"]["fields"]
    rows = d["data"]["data"]

    matches = []
    for row in rows:
        rec = dict(zip(fields, row))
        def unwrap(v):
            if isinstance(v, list) and v: return v[0]
            return v
        rec = {k: unwrap(v) for k, v in rec.items()}
        cat = str(rec.get("类别", ""))
        status = str(rec.get("联系状态", ""))
        if category in cat and status == "活跃":
            matches.append(rec)
    return matches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, help="供应商类别（面料商/辅料商/成衣工厂/印花厂/物流）")
    ap.add_argument("--message", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print(f"=== 群发 {args.category} ===")
    suppliers = fetch_suppliers_by_category(args.category)
    if not suppliers:
        print(f"❌ 没找到活跃的「{args.category}」类供应商")
        sys.exit(1)

    if len(suppliers) > MAX_BROADCAST:
        print(f"⚠ 找到 {len(suppliers)} 个，超过单次群发上限 {MAX_BROADCAST}，截取前 {MAX_BROADCAST} 个")
        suppliers = suppliers[:MAX_BROADCAST]

    print(f"找到 {len(suppliers)} 个供应商，预计耗时 {len(suppliers) * INTERVAL_SECONDS} 秒")
    for s in suppliers:
        print(f"  • {s.get('供应商名')} → {s.get('微信备注名')}")

    if args.dry_run:
        print(f"\n草稿模式，不真发")
        return

    sent_count = 0
    failed_count = 0
    for i, s in enumerate(suppliers, 1):
        print(f"\n[{i}/{len(suppliers)}] 发给 {s.get('供应商名')} ...")
        cmd = ["python", "-u", SEND_SCRIPT,
               "--supplier", s.get("供应商名", ""),
               "--message", args.message]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if r.returncode == 0:
            sent_count += 1
            print(f"  ✓ 发送成功")
        else:
            failed_count += 1
            print(f"  ✗ 发送失败")
            print(f"    {(r.stderr or r.stdout)[:200]}")

        # 限流 12 秒（除了最后一条）
        if i < len(suppliers):
            print(f"  ⏱ 等待 {INTERVAL_SECONDS} 秒（限流防风控）...")
            time.sleep(INTERVAL_SECONDS)

    print(f"\n=== 完成 ===")
    print(f"✅ 成功 {sent_count} / 失败 {failed_count}")


if __name__ == "__main__":
    main()
