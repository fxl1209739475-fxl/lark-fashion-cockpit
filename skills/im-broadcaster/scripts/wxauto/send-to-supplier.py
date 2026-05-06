"""飞书 → 微信桥 · 给指定供应商发消息

依赖：
  pip install wxauto

前置：
  1. PC 微信 4.0+ 客户端开着 + 已登录
  2. 该供应商已加你微信好友 + 你已在通讯录备注好（备注名要跟 28 表登记的一致）

用法：
  python send-to-supplier.py --supplier "ZC工厂" --message "问下 DRS-0429 同款雪纺..."
  python send-to-supplier.py --supplier "ZC工厂" --message "..." --dry-run  # 草稿不真发
"""

import os, sys, json, argparse, subprocess, time
from datetime import datetime

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
AUDIT_LOG = os.path.join(PROJECT_ROOT, "logs", "wxauto-audit.jsonl")

DAILY_LIMIT = 50          # 每日单账号上限（防风控）
PER_MINUTE_LIMIT = 5      # 每分钟最多 5 条
MESSAGE_PREFIX = "(老板娘 cockpit 自动消息)\n\n"  # 加前缀让供应商知道是机器代发，不会困惑


def fetch_supplier(supplier_name: str) -> dict:
    """从 28_供应商档案 表查供应商微信备注名 + 状态"""
    base = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
    table = os.environ.get("TABLE_SUPPLIERS", "")
    if not base or not table:
        raise RuntimeError("缺 LARK_FASHION_COCKPIT_BASE_TOKEN 或 TABLE_SUPPLIERS")

    r = subprocess.run(
        [LARK_CLI, "base", "+record-list",
         "--base-token", base, "--table-id", table,
         "--limit", "200", "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    if r.returncode != 0:
        raise RuntimeError(f"拉 28 表失败: {r.stderr[:200]}")
    d = json.loads(r.stdout)
    fields = d["data"]["fields"]
    rows = d["data"]["data"]

    # 模糊匹配供应商名
    for row in rows:
        rec = dict(zip(fields, row))
        def unwrap(v):
            if isinstance(v, list) and v: return v[0]
            return v
        rec = {k: unwrap(v) for k, v in rec.items()}
        if supplier_name in str(rec.get("供应商名", "")) or supplier_name in str(rec.get("微信备注名", "")):
            return rec
    return None


def check_audit_limits() -> tuple[bool, str]:
    """检查今日 / 当前分钟的发送次数是否超限"""
    if not os.path.exists(AUDIT_LOG):
        return True, "ok"

    today = datetime.now().strftime("%Y-%m-%d")
    minute = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_count = 0
    minute_count = 0

    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("ts", "").startswith(today):
                    today_count += 1
                if rec.get("ts", "").startswith(minute):
                    minute_count += 1
            except Exception:
                pass

    if today_count >= DAILY_LIMIT:
        return False, f"已达每日上限 {DAILY_LIMIT}，明天再用"
    if minute_count >= PER_MINUTE_LIMIT:
        return False, f"当前分钟已发 {minute_count}/{PER_MINUTE_LIMIT}，等下分钟再发"
    return True, "ok"


def write_audit(supplier: dict, message: str, status: str, dry_run: bool):
    """写审计 log"""
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    rec = {
        "ts": datetime.now().isoformat(),
        "supplier_name": supplier.get("供应商名", ""),
        "wechat_alias": supplier.get("微信备注名", ""),
        "category": supplier.get("类别", ""),
        "message": message[:500],
        "status": status,
        "dry_run": dry_run,
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def send_via_wxauto(wechat_alias: str, message: str) -> tuple[bool, str]:
    """调 wxauto 真发消息"""
    try:
        from wxauto import WeChat
    except ImportError:
        return False, "未装 wxauto。pip install wxauto"

    try:
        wx = WeChat()
        # 切到该联系人对话
        wx.ChatWith(wechat_alias)
        time.sleep(0.5)
        # 发消息
        wx.SendMsg(message)
        return True, "ok"
    except Exception as e:
        return False, f"wxauto 异常: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supplier", required=True, help="供应商名（28 表里登记的名字或微信备注名）")
    ap.add_argument("--message", required=True, help="要发的消息内容")
    ap.add_argument("--dry-run", action="store_true", help="草稿模式，不真发")
    ap.add_argument("--no-prefix", action="store_true", help="不加'cockpit 自动消息'前缀")
    args = ap.parse_args()

    print(f"=== 发送给供应商 ===")
    print(f"目标: {args.supplier}")
    print(f"模式: {'草稿（不真发）' if args.dry_run else '真发'}")

    # 1. 查供应商
    supplier = fetch_supplier(args.supplier)
    if not supplier:
        print(f"❌ 28_供应商档案 表里没找到「{args.supplier}」。请先在表里登记此供应商")
        sys.exit(1)
    print(f"✓ 找到: {supplier.get('供应商名')} → 微信备注「{supplier.get('微信备注名')}」")

    # 2. 状态校验
    status = supplier.get("联系状态", "")
    if status == "黑名单":
        print(f"❌ 该供应商已在黑名单（{supplier.get('备注', '')}），不发")
        sys.exit(1)
    if status not in ["活跃", "备选"]:
        print(f"⚠ 状态非活跃（当前: {status}），跳过")
        sys.exit(1)

    # 3. 频率限制
    ok, reason = check_audit_limits()
    if not ok:
        print(f"❌ 频率限制: {reason}")
        sys.exit(1)

    # 4. 拼消息
    msg = (MESSAGE_PREFIX if not args.no_prefix else "") + args.message
    print(f"\n消息内容（{len(msg)} 字）:")
    print(f"{'-' * 50}")
    print(msg)
    print(f"{'-' * 50}\n")

    # 5. 真发 or 草稿
    if args.dry_run:
        print("✓ 草稿模式：未真发。要真发去掉 --dry-run")
        write_audit(supplier, msg, "dry_run", True)
        return

    print(f"调 wxauto 发送中...")
    ok, info = send_via_wxauto(supplier["微信备注名"], msg)
    if ok:
        print(f"✅ 已发到「{supplier['微信备注名']}」")
        write_audit(supplier, msg, "sent", False)
    else:
        print(f"❌ 发送失败: {info}")
        write_audit(supplier, msg, f"failed: {info}", False)
        sys.exit(1)


if __name__ == "__main__":
    main()
