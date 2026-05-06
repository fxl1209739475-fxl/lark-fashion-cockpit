"""omnitask-bridge · 飞书数据查询封装

被 chat_router / skill_executor 调用，用 lark-cli 从飞书拉数据并返回结构化结果。

用法（被 subprocess 调用）：
  python feishu_data.py --query sales_today
  python feishu_data.py --query stock_alerts
  python feishu_data.py --query my_tasks --user-id ou_xxx
  python feishu_data.py --query bloggers_top
  python feishu_data.py --query calendar_today --user-id ou_xxx
  python feishu_data.py --query task_create --title "..." --assignee "马萍蔓"
  python feishu_data.py --query doc_create --title "..."

输出：JSON to stdout（最后一行）— skill_executor 会把整段 stdout 推给 chat_router
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass


LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE_TOKEN = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
BOSS_OPEN_ID = os.environ.get("LARK_FASHION_COCKPIT_BOSS_OPEN_ID", "")

# 表 id（与 .env / team-config.json 对齐）
TABLE_SALES = os.environ.get("TABLE_SALES_4PLATFORMS", "")
TABLE_STOCK = os.environ.get("TABLE_STOCK_ALERT", "")
TABLE_BLOGGERS = os.environ.get("TABLE_BLOGGER_VIDEOS", "")
TABLE_TASKS = os.environ.get("TABLE_TASKS", "")


def lark_run(args: list, timeout: int = 15) -> dict:
    """执行 lark-cli 并返回 JSON。失败时返回 {"_error": "..."}"""
    try:
        r = subprocess.run([LARK_CLI] + args,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as e:
        return {"_error": f"调用 lark-cli 异常: {e}"}
    if r.returncode != 0:
        return {"_error": f"lark-cli 失败: {(r.stderr or r.stdout)[:300]}"}
    try:
        return json.loads(r.stdout) if r.stdout.strip().startswith("{") else {"_raw": r.stdout}
    except Exception as e:
        return {"_error": f"JSON 解析失败: {e}", "_raw": r.stdout[:500]}


# ============================================================
# 查询型 (query.*)
# ============================================================

def query_sales_today() -> dict:
    if not BASE_TOKEN or not TABLE_SALES:
        return {"_error": "缺 LARK_FASHION_COCKPIT_BASE_TOKEN 或 TABLE_SALES_4PLATFORMS"}
    today = datetime.now().strftime("%Y-%m-%d")
    res = lark_run(["base", "+record-list",
                    "--base-token", BASE_TOKEN,
                    "--table-id", TABLE_SALES,
                    "--limit", "100", "--format", "json"])
    if "_error" in res:
        return res
    rows = res.get("data", {}).get("data", [])
    fields = res.get("data", {}).get("fields", [])
    # 过滤今日 + 聚合
    summary = {"date": today, "platforms": {}, "total_revenue": 0, "total_orders": 0, "top_skus": []}
    for row in rows:
        rec = dict(zip(fields, row))
        date = str(rec.get("日期", "")).split("T")[0]
        if date != today:
            continue
        plat = rec.get("平台", "")
        rev = float(rec.get("销售额", 0) or 0)
        ord_n = int(rec.get("订单数", 0) or 0)
        summary["platforms"][plat] = summary["platforms"].get(plat, 0) + rev
        summary["total_revenue"] += rev
        summary["total_orders"] += ord_n
    return summary


def query_stock_alerts() -> dict:
    if not BASE_TOKEN or not TABLE_STOCK:
        return {"_error": "缺 TABLE_STOCK_ALERT"}
    res = lark_run(["base", "+record-list",
                    "--base-token", BASE_TOKEN,
                    "--table-id", TABLE_STOCK,
                    "--limit", "100", "--format", "json"])
    if "_error" in res:
        return res
    rows = res.get("data", {}).get("data", [])
    fields = res.get("data", {}).get("fields", [])
    red = []
    yellow = []
    for row in rows:
        rec = dict(zip(fields, row))
        level = str(rec.get("预警级别", "")).lower()
        sku = rec.get("SKU", "")
        stock = rec.get("当前库存", 0)
        days = rec.get("可售天数", "")
        if "red" in level or "红" in level:
            red.append({"sku": sku, "stock": stock, "days": days})
        elif "yellow" in level or "黄" in level:
            yellow.append({"sku": sku, "stock": stock, "days": days})
    return {"red_count": len(red), "yellow_count": len(yellow),
            "red": red[:10], "yellow": yellow[:5]}


def query_my_tasks(user_id: str = None) -> dict:
    user_id = user_id or BOSS_OPEN_ID
    if not user_id:
        return {"_error": "缺 user_id"}
    res = lark_run(["task", "+get-my-tasks", "--limit", "50", "--format", "json"])
    if "_error" in res:
        return res
    return res.get("data", {})


def query_bloggers_top() -> dict:
    if not BASE_TOKEN or not TABLE_BLOGGERS:
        return {"_error": "缺 TABLE_BLOGGER_VIDEOS"}
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    res = lark_run(["base", "+record-list",
                    "--base-token", BASE_TOKEN,
                    "--table-id", TABLE_BLOGGERS,
                    "--limit", "100", "--format", "json"])
    if "_error" in res:
        return res
    rows = res.get("data", {}).get("data", [])
    fields = res.get("data", {}).get("fields", [])
    items = []
    for row in rows:
        rec = dict(zip(fields, row))
        date = str(rec.get("发布日期", "")).split("T")[0]
        if date < week_ago:
            continue
        items.append({
            "title": rec.get("标题", ""),
            "blogger": rec.get("博主", ""),
            "likes": rec.get("点赞数", 0),
            "score": rec.get("综合评分", 0),
            "url": rec.get("链接", ""),
        })
    items.sort(key=lambda x: -(x.get("likes") or 0))
    return {"top": items[:5], "total_in_week": len(items)}


def query_calendar_today(user_id: str = None) -> dict:
    user_id = user_id or BOSS_OPEN_ID
    res = lark_run(["calendar", "+agenda", "--days", "1", "--format", "json"])
    if "_error" in res:
        return res
    return res.get("data", {})


# ============================================================
# 任务型 (task.*) / 文档型 (doc.*)
# ============================================================

def task_create(title: str, assignee: str = "", due: str = "") -> dict:
    if not title:
        return {"_error": "标题必填"}
    args = ["task", "+create", "--title", title]
    res = lark_run(args)
    if "_error" in res:
        return res
    guid = res.get("data", {}).get("task", {}).get("guid", "")
    if assignee and guid:
        # +assign 需要 open_id —— 这里简化：用名字粗匹配，实际生产应该走 contact 解析
        # 留给 chat_router 在调用前解析名字 → open_id
        return {"_error": "建任务成功但 --assignee 需要 open_id（chat_router 应先解析）",
                "guid": guid}
    return {"ok": True, "guid": guid, "title": title}


def doc_create(title: str, content: str = "") -> dict:
    if not title:
        return {"_error": "标题必填"}
    args = ["docs", "+create", "--api-version", "v2", "--title", title]
    if content:
        args += ["--content", content]
    res = lark_run(args, timeout=30)
    return res


# ============================================================
# main
# ============================================================

QUERY_HANDLERS = {
    "sales_today": lambda **k: query_sales_today(),
    "stock_alerts": lambda **k: query_stock_alerts(),
    "my_tasks": lambda **k: query_my_tasks(k.get("user_id")),
    "bloggers_top": lambda **k: query_bloggers_top(),
    "calendar_today": lambda **k: query_calendar_today(k.get("user_id")),
    "task_create": lambda **k: task_create(k.get("title", ""), k.get("assignee", ""), k.get("due", "")),
    "doc_create": lambda **k: doc_create(k.get("title", ""), k.get("content", "")),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, choices=list(QUERY_HANDLERS.keys()))
    ap.add_argument("--user-id", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--assignee", default="")
    ap.add_argument("--due", default="")
    ap.add_argument("--content", default="")
    args = ap.parse_args()

    handler = QUERY_HANDLERS[args.query]
    result = handler(
        user_id=args.user_id,
        title=args.title,
        assignee=args.assignee,
        due=args.due,
        content=args.content,
    )

    # 简洁输出 + JSON 标记，方便 chat_router 解析
    print(f"[query={args.query}]")
    if isinstance(result, dict) and "_error" in result:
        print(f"❌ {result['_error']}")
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(2)

    # 渲染人类可读摘要 + 末尾打 JSON 行
    if args.query == "sales_today":
        print(f"📊 今日销售（{result.get('date','?')}）")
        print(f"   总销售额：¥{result.get('total_revenue', 0):,.0f}  ·  订单 {result.get('total_orders', 0)}")
        for plat, rev in (result.get("platforms") or {}).items():
            print(f"   • {plat}: ¥{rev:,.0f}")
    elif args.query == "stock_alerts":
        red = result.get("red", [])
        print(f"🚨 库存预警：{result.get('red_count', 0)} 红 / {result.get('yellow_count', 0)} 黄")
        for it in red[:8]:
            print(f"   • {it['sku']} 剩 {it['stock']} 件（约 {it.get('days','?')} 天）")
    elif args.query == "bloggers_top":
        top = result.get("top", [])
        print(f"📺 本周对标博主 Top 5（共 {result.get('total_in_week', 0)} 条）")
        for it in top:
            print(f"   • {it['title'][:30]}  ❤ {it['likes']}  ⭐ {it['score']}")
    elif args.query == "my_tasks":
        items = result.get("items", []) if isinstance(result, dict) else []
        print(f"✓ 你有 {len(items)} 条未完成任务")
        for t in items[:8]:
            print(f"   • {t.get('summary', '')}")
    elif args.query == "calendar_today":
        items = result.get("items", []) if isinstance(result, dict) else []
        print(f"📅 今天 {len(items)} 个日程")
        for ev in items[:6]:
            print(f"   • {ev.get('summary', '')}  {ev.get('start', '')}")
    elif args.query == "task_create":
        if result.get("ok"):
            print(f"✓ 任务已创建：{result.get('title')}  (guid={result.get('guid','')[:12]}...)")
        else:
            print(f"⚠ {result}")
    elif args.query == "doc_create":
        d = result.get("data", {}) if isinstance(result, dict) else {}
        print(f"✓ 文档创建：{d.get('document', {}).get('title', '?')}")
        url = d.get("document", {}).get("url", "")
        if url:
            print(f"   {url}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\n__JSON__: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
