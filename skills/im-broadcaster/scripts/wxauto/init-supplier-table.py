"""一键建 28_供应商档案 表 + 灌示例数据

用法：
  python init-supplier-table.py
"""

import os, sys, json, subprocess

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
TMP = r"C:\Users\冯兴龙\AppData\Local\Temp"

FIELDS = [
    {"name": "供应商名", "type": "text"},
    {"name": "微信备注名", "type": "text"},
    {"name": "类别", "type": "select", "options": [
        {"name": "面料商"}, {"name": "辅料商"}, {"name": "成衣工厂"},
        {"name": "印花厂"}, {"name": "物流"},
    ]},
    {"name": "联系状态", "type": "select", "options": [
        {"name": "活跃"}, {"name": "备选"}, {"name": "黑名单"},
    ]},
    {"name": "备注", "type": "text"},
    {"name": "上次沟通", "type": "datetime"},
    {"name": "累计消息数", "type": "number"},
]

# 示例数据（mock，老板娘换成真供应商）
SAMPLE_DATA = [
    ("ZC 工厂", "浙江老张", "成衣工厂", "活跃", "合作 5 年，工艺稳，准时率 95%"),
    ("GS 工厂", "广州小李", "成衣工厂", "活跃", "版型新颖但交期慢一周"),
    ("HF 工厂", "广东老王", "成衣工厂", "黑名单", "⚠ 曾跑路，2026 年 3 月已拉黑"),
    ("杭州面料商A", "面料杭州张姐", "面料商", "活跃", "雪纺 / 真丝 / 醋酸混纺，价格中等"),
    ("绍兴面料商B", "绍兴王哥-面料", "面料商", "活跃", "针织面料专精，价格便宜"),
    ("辅料商小郑", "辅料郑哥", "辅料商", "活跃", "扣子 / 拉链 / 吊牌齐全"),
    ("印花厂老李", "印花老李", "印花厂", "活跃", "数码印花 + 烫钻"),
    ("物流-顺丰对接", "顺丰王经理", "物流", "活跃", "对接专员，问折扣率"),
]


def main():
    base = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
    if not base:
        print("⚠ 缺 LARK_FASHION_COCKPIT_BASE_TOKEN")
        sys.exit(1)

    print(f"=== 建 28_供应商档案 表 ===")

    # 1. 建表
    r = subprocess.run(
        [LARK_CLI, "base", "+table-create",
         "--base-token", base, "--name", "28_供应商档案"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if r.returncode != 0:
        print(f"⚠ 建表可能已存在或失败：{r.stderr[:200]}")
        # 尝试找已存在的同名表
        r2 = subprocess.run(
            [LARK_CLI, "base", "+table-list", "--base-token", base, "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        if r2.returncode == 0:
            try:
                tables = json.loads(r2.stdout)["data"]["items"]
                for t in tables:
                    if t.get("name") == "28_供应商档案":
                        table_id = t["table_id"]
                        print(f"✓ 用已有表: {table_id}")
                        break
                else:
                    print(f"❌ 找不到已建好的 28 表")
                    sys.exit(1)
            except Exception:
                sys.exit(1)
    else:
        try:
            table_id = json.loads(r.stdout)["data"]["table"]["table_id"]
            print(f"✓ 新建表: {table_id}")
        except Exception:
            print(f"❌ 解析建表响应失败")
            sys.exit(1)

    # 2. 加字段
    print(f"\n=== 加字段 ===")
    for f in FIELDS:
        r = subprocess.run(
            [LARK_CLI, "base", "+field-create",
             "--base-token", base, "--table-id", table_id,
             "--json", json.dumps(f, ensure_ascii=False)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
        print(f"  {'✓' if r.returncode == 0 else '✗'} {f['name']}")

    # 3. 灌示例数据
    print(f"\n=== 灌示例数据 ===")
    field_order = ["供应商名", "微信备注名", "类别", "联系状态", "备注"]
    rows = [list(s) for s in SAMPLE_DATA]
    payload = {"fields": field_order, "rows": rows}
    p = os.path.join(TMP, "suppliers-batch.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    r = subprocess.run(
        [LARK_CLI, "base", "+record-batch-create",
         "--base-token", base, "--table-id", table_id,
         "--json", "@./suppliers-batch.json"],
        cwd=TMP, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(f"  {'✓ 灌入 8 条示例' if r.returncode == 0 else '✗ 灌入失败: ' + (r.stderr or '')[:200]}")

    print(f"\n🎉 完成。请：")
    print(f"  1. 把以下加进 .env：TABLE_SUPPLIERS={table_id}")
    print(f"  2. 在飞书 28_供应商档案 表里把示例数据替换成你真实的供应商")
    print(f"  3. 微信里给每个供应商打好备注名（要跟「微信备注名」字段一致）")


if __name__ == "__main__":
    main()
