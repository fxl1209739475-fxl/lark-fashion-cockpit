"""一键初始化飞书 base — 建 27 张多维表 schema + 灌入 mock 演示数据

装 skill 后跑这个，自动给你的飞书 base 建好 lark-fashion-cockpit 用的 27 张表 +
字段定义 + 演示数据，然后机器人才能完整跑起来。

用法：
  cp .env.example .env       # 先填好 LARK_FASHION_COCKPIT_BASE_TOKEN
  python scripts/init-cockpit.py
  python scripts/init-cockpit.py --dry-run   # 只看要建什么不真建
  python scripts/init-cockpit.py --skip-mock # 不灌示例数据

# 前置：你需要先在飞书自己建一个 base，然后把 token 填到 .env
# Base 创建：lark-cli base +base-create --name "lark-fashion-cockpit"
"""

import os, sys, json, subprocess, argparse
from pathlib import Path

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
PROJECT_ROOT = Path(__file__).parent.parent

# 27 张表的 schema 定义（精简版 — 完整版在 lib/base-schema/tables.json）
TABLES = [
    {"id": "01_产品库", "key": "TABLE_PRODUCT_LIBRARY",
     "fields": [
         ("款号", "text"), ("产品名称", "text"), ("品类", "select"),
         ("元素标签", "multi_select"), ("状态", "select"),
         ("库存", "number"), ("已实销", "number"), ("成本", "number"), ("吊牌价", "number"),
     ]},
    {"id": "02_4平台销售", "key": "TABLE_SALES_4PLATFORMS",
     "fields": [("日期", "datetime"), ("平台", "select"), ("GMV", "number"),
                ("订单数", "number"), ("访客", "number"), ("转化率", "number")]},
    {"id": "03_库存预警", "key": "TABLE_STOCK_ALERT",
     "fields": [("款号", "text"), ("当前库存", "number"), ("日均销量", "number"),
                ("预计售完天数", "number"), ("预警等级", "select")]},
    {"id": "04_上新波段", "key": "TABLE_LAUNCH_WAVES",
     "fields": [("波段", "text"), ("上线日期", "datetime"), ("款数", "number"), ("状态", "select")]},
    {"id": "05_任务清单", "key": "TABLE_TASKS",
     "fields": [("任务标题", "text"), ("角色", "multi_select"), ("优先级", "select"),
                ("状态", "select"), ("截止日期", "datetime"), ("追踪状态", "select")]},
    {"id": "06_选题池", "key": "TABLE_TOPICS",
     "fields": [("选题", "text"), ("平台", "multi_select"), ("状态", "select"), ("评分", "number")]},
    {"id": "07_文案库", "key": "TABLE_COPY",
     "fields": [("标题", "text"), ("正文", "text"), ("版本", "number"), ("发布日期", "datetime")]},
    {"id": "08_直播排期", "key": "TABLE_LIVESTREAM_SCHEDULE",
     "fields": [("场次", "text"), ("时间", "datetime"), ("主播", "text"), ("重点款", "multi_select")]},
    {"id": "09_生产档案", "key": "TABLE_PRODUCTION",
     "fields": [("款号", "text"), ("工厂", "select"), ("交期", "datetime"), ("状态", "select")]},
    {"id": "10_客户分层", "key": "TABLE_CUSTOMERS",
     "fields": [("客户名", "text"), ("分层", "select"), ("累计消费", "number"), ("最近购买", "datetime")]},
    {"id": "11_退货反馈", "key": "TABLE_RETURNS",
     "fields": [("退货单号", "text"), ("款号", "text"), ("原因", "select"), ("处理状态", "select")]},
    {"id": "12_竞品博主库", "key": "TABLE_COMPETITOR_BLOGGERS",
     "fields": [("博主名", "text"), ("平台", "select"), ("粉丝数", "number"), ("监控状态", "select")]},
    {"id": "13_OKR", "key": "TABLE_OKR",
     "fields": [("周期", "select"), ("目标", "text"), ("KR", "text"), ("进度", "number")]},
    {"id": "14_审批记录", "key": "TABLE_APPROVALS",
     "fields": [("申请", "text"), ("申请人", "text"), ("金额", "number"), ("状态", "select")]},
    {"id": "15_市场内容监控", "key": "TABLE_MARKET_CONTENT",
     "fields": [("视频标题", "text"), ("博主", "text"), ("点赞", "number"), ("发布时间", "datetime")]},
    {"id": "16_竞品产品监控", "key": "TABLE_COMPETITOR_PRODUCTS",
     "fields": [("竞品款号", "text"), ("竞品品牌", "text"), ("价格", "number"), ("销量", "number")]},
    {"id": "17_产品搭配组", "key": "TABLE_OUTFIT_PAIRS",
     "fields": [("主推款", "link"), ("搭配款", "link"), ("使用次数", "number"), ("AI 评分", "number")]},
    {"id": "24_直播记录", "key": "TABLE_LIVESTREAM_RECORDS",
     "fields": [("直播标题", "text"), ("日期", "datetime"), ("3 平台 URL", "text"),
                ("实销 GMV", "number"), ("库存 GMV", "number"), ("库存占比", "number"), ("抓取状态", "select")]},
    {"id": "25_未完成事项", "key": "TABLE_TODOS",
     "fields": [("待办标题", "text"), ("类别", "multi_select"), ("优先级", "multi_select"),
                ("状态", "multi_select"), ("阻塞原因", "text"), ("解决路径", "text")]},
    {"id": "26_老板语料库", "key": "TABLE_BOSS_QA",
     "fields": [("题号", "number"), ("维度", "select"), ("题型", "select"),
                ("题目", "text"), ("老板回答", "text"), ("状态", "select")]},
    {"id": "27_对标博主视频监控", "key": "TABLE_BLOGGER_VIDEOS",
     "fields": [("博主名称", "text"), ("视频标题", "text"), ("视频链接", "url"),
                ("点赞数", "number"), ("收藏率", "number"), ("爆款指数", "number"),
                ("AI 评分", "number"), ("口播文案", "text"), ("视频拆解", "text"), ("状态", "select")]},
    {"id": "28_开源雷达", "key": "TABLE_OPENSOURCE_RADAR",
     "fields": [("项目名", "text"), ("GitHub URL", "url"), ("star 数", "number"),
                ("中文摘要", "text"), ("相关度评分", "number"), ("改造思路", "text"), ("状态", "select")]},
    # 待加：18_角色档案 / 19_客服档案 / 20_工厂黑白名单 / 21_主播档案 / 22_社交媒体KPI / 23_利润表
]


def lark_api(method, path, data=None, params=None):
    cmd = [LARK_CLI, "api", method, path]
    if data: cmd += ["--data", json.dumps(data, ensure_ascii=False)]
    if params: cmd += ["--params", json.dumps(params, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    return r


def create_table(base_token, name):
    """建一张空表（字段单独建）"""
    res = subprocess.run(
        [LARK_CLI, "base", "+table-create", "--base-token", base_token, "--name", name],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if res.returncode != 0:
        print(f"  ✗ 建表失败 {name}: {(res.stderr or '')[:150]}")
        return None
    try:
        return json.loads(res.stdout)["data"]["table"]["table_id"]
    except Exception:
        return None


def add_field(base_token, table_id, name, ftype):
    """给表加一个字段"""
    field = {"name": name, "type": ftype}
    if ftype == "select":
        field["options"] = [{"name": "选项1"}, {"name": "选项2"}]
    elif ftype == "multi_select":
        field["type"] = "select"
        field["options"] = [{"name": "标签1"}, {"name": "标签2"}]
    res = subprocess.run(
        [LARK_CLI, "base", "+field-create",
         "--base-token", base_token, "--table-id", table_id,
         "--json", json.dumps(field, ensure_ascii=False)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
    )
    return res.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只列出要建啥不真建")
    ap.add_argument("--skip-mock", action="store_true")
    args = ap.parse_args()

    base_token = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
    if not base_token:
        print("⚠ 缺 LARK_FASHION_COCKPIT_BASE_TOKEN 环境变量")
        print("  先：cp .env.example .env  → 填好 base token")
        print("  或者建一个 base：lark-cli base +base-create --name \"lark-fashion-cockpit\"")
        sys.exit(1)

    print(f"=== lark-fashion-cockpit base 初始化 ===")
    print(f"Base token: {base_token[:12]}...")
    print(f"将建表: {len(TABLES)} 张")
    print(f"模式: {'dry-run（只列）' if args.dry_run else '真建'}")
    print()

    if args.dry_run:
        for t in TABLES:
            print(f"  [{t['id']}] {len(t['fields'])} 字段：{', '.join(n for n,_ in t['fields'])}")
        return

    # 先检查已存在的表（避免重复建）
    existing = []
    r = subprocess.run(
        [LARK_CLI, "base", "+table-list", "--base-token", base_token, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if r.returncode == 0:
        try:
            existing = [t["name"] for t in json.loads(r.stdout)["data"]["items"]]
        except Exception:
            pass

    table_ids = {}
    for t in TABLES:
        if t["id"] in existing:
            print(f"⏭ 已存在跳过：{t['id']}")
            continue
        print(f"📝 建表：{t['id']}")
        tid = create_table(base_token, t["id"])
        if not tid:
            continue
        table_ids[t["key"]] = tid
        for fname, ftype in t["fields"]:
            ok = add_field(base_token, tid, fname, ftype)
            print(f"   {'✓' if ok else '✗'} {fname} ({ftype})")

    print(f"\n✓ 27 张表初始化完成")
    print(f"\n下一步：把以下 table_id 加进 .env 文件：")
    for k, v in table_ids.items():
        print(f"  {k}={v}")

    if not args.skip_mock:
        print(f"\n📦 灌 mock 演示数据...")
        # 跑各 mock 灌入脚本
        mock_scripts = [
            "scripts/seed-todos.ps1",
            "skills/blogger-monitor/scripts/seed-mock-bloggers.py",
            "skills/boss-clone-aily/scripts/seed-boss-qa.py",
            "scripts/seed-livestream-811.ps1",
            "scripts/seed-task-lifecycle-mock.ps1",
        ]
        for s in mock_scripts:
            full = PROJECT_ROOT / s
            if not full.exists():
                continue
            print(f"  → {s}")
            if s.endswith(".ps1"):
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(full)],
                               capture_output=True, timeout=60)
            else:
                subprocess.run(["python", "-u", str(full)],
                               capture_output=True, timeout=60,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    print(f"\n🎉 lark-fashion-cockpit 初始化完成！")
    print(f"\n下一步：")
    print(f"  1. python scripts/event-listener.py    # 启动 IM 机器人")
    print(f"  2. python skills/auto-scheduler/scripts/cockpit-scheduler.py    # 启动定时任务调度")
    print(f"  3. 飞书私聊机器人发：'巡检任务'  /  '今天卖得咋样'")


if __name__ == "__main__":
    main()
