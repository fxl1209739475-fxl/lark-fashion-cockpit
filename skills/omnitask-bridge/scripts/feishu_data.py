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
TABLE_PRODUCT_LIBRARY = os.environ.get("TABLE_PRODUCT_LIBRARY", "")
TABLE_SALES = os.environ.get("TABLE_SALES_4PLATFORMS", "")
TABLE_STOCK = os.environ.get("TABLE_STOCK_ALERT", "")
TABLE_BLOGGERS = os.environ.get("TABLE_BLOGGER_VIDEOS", "")
TABLE_TASKS = os.environ.get("TABLE_TASKS", "")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def lark_run(args: list, timeout: int = 15) -> dict:
    """执行 lark-cli 并返回 JSON。

    注意：lark-cli 默认输出 markdown 表格而非 JSON，必须显式带 --format json。
    本函数会自动确保 --format json 存在，免得 caller 漏掉。
    """
    args = list(args)
    if "--format" not in args:
        args += ["--format", "json"]
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

    def unwrap(v):
        if isinstance(v, list) and v:
            v = v[0]
        if isinstance(v, dict):
            return v.get("text") or v.get("name") or str(v)
        return v if v is not None else ""

    red = []
    yellow = []
    for row in rows:
        rec = {f: unwrap(v) for f, v in zip(fields, row)}
        level = str(rec.get("紧急度", "") or rec.get("预警级别", ""))
        sku = rec.get("SKU", "") or rec.get("款号", "")
        stock = rec.get("当前库存", 0) or rec.get("库存", 0)
        safety_line = rec.get("安全线", "")
        suggest = rec.get("建议补货量", "")
        days = rec.get("可售天数", "")

        item = {"sku": sku, "stock": stock, "safety_line": safety_line,
                "suggest_replenish": suggest, "days": days, "level": level}

        if "紧急" in level or "red" in level.lower() or "红" in level:
            red.append(item)
        elif "中" in level or "yellow" in level.lower() or "黄" in level or "警" in level:
            yellow.append(item)

    return {"red_count": len(red), "yellow_count": len(yellow),
            "red": red[:10], "yellow": yellow[:10]}


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


def query_product_analysis(question: str) -> dict:
    """拉飞书 01_产品库 实时数据 → DEEPSEEK 基于实际数据回答用户问题"""
    if not BASE_TOKEN or not TABLE_PRODUCT_LIBRARY:
        return {"_error": "缺 LARK_FASHION_COCKPIT_BASE_TOKEN 或 TABLE_PRODUCT_LIBRARY"}
    if not question:
        return {"_error": "需要具体问题（产品库分析）"}
    if not DEEPSEEK_API_KEY:
        return {"_error": "缺 DEEPSEEK_API_KEY"}

    res = lark_run([
        "base", "+record-list",
        "--base-token", BASE_TOKEN,
        "--table-id", TABLE_PRODUCT_LIBRARY,
        "--limit", "200", "--format", "json",
    ], timeout=20)
    if "_error" in res:
        return res

    rows = res.get("data", {}).get("data", [])
    fields = res.get("data", {}).get("fields", [])
    if not rows:
        return {"_error": "产品库为空"}

    # 字段级取值，限制最多 80 条防 token 爆
    products = []
    for row in rows[:80]:
        products.append(dict(zip(fields, row)))

    from openai import OpenAI
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    prompt = f"""你是女装电商运营分析助手。下面是「01_产品库」当前实时数据（共 {len(products)} 个 SKU），用户的问题：

「{question}」

请基于数据给出分析，输出**纯文字**（不要 markdown 代码块），结构如下：

【结论】1-2 句直接回答

【数据支撑】列出关键 SKU + 数字（最多 5 条）
- SKU XXX：售罄率 XX%，剩余库存 XXX 件
- ...

【建议】3 条可执行行动

# 产品库实时数据
{json.dumps(products, ensure_ascii=False, indent=1)[:9000]}
"""

    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    text = resp.choices[0].message.content.strip()

    return {
        "ok": True,
        "question": question,
        "products_count": len(products),
        "analysis": text,
    }


# ============================================================
# 任务型 (task.*) / 文档型 (doc.*)
# ============================================================

_TEAM_CONFIG_PATH = Path(__file__).resolve().parents[3] / "lib" / "team-config.json"


def _load_name_to_open_id() -> dict:
    """从 team-config.json 加载 名字/角色 → open_id 映射"""
    mapping = {}
    if not _TEAM_CONFIG_PATH.exists():
        return mapping
    try:
        with open(_TEAM_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        return mapping
    boss = cfg.get("boss", {})
    if boss.get("name") and boss.get("open_id"):
        mapping[boss["name"]] = boss["open_id"]
    for role, m in (cfg.get("team_members") or {}).items():
        if m.get("name") and m.get("open_id"):
            mapping[m["name"]] = m["open_id"]
            mapping[role] = m["open_id"]   # 用角色名也能查（"设计师" / "生产主管"）
    return mapping


def task_create(title: str, assignee: str = "", due: str = "") -> dict:
    if not title:
        return {"_error": "标题必填"}

    # 1. 建任务（lark-cli 用 --summary 不是 --title）
    args = ["task", "+create", "--summary", title]
    if due:
        args += ["--due", due]
    res = lark_run(args)
    if "_error" in res:
        return res
    # lark-cli 的响应：data.guid 直接在 data 下（不像旧文档说的 data.task.guid）
    data = res.get("data") or {}
    guid = data.get("guid") or (data.get("task") or {}).get("guid", "")
    if not guid:
        return {"_error": "建任务返回未带 guid", "_raw": res}

    result = {"ok": True, "guid": guid, "title": title}

    # 2. 指派（必须分两步，--assignee 在 +create 里被静默忽略）
    if assignee:
        name_map = _load_name_to_open_id()
        open_id = name_map.get(assignee, "")
        if not open_id:
            result["assign_warning"] = f"找不到「{assignee}」对应的 open_id（team-config.json 未登记）"
        else:
            assign_res = lark_run(["task", "+assign", "--task-id", guid, "--add", open_id])
            if "_error" in assign_res:
                result["assign_warning"] = f"建任务成功但指派失败: {assign_res['_error']}"
            else:
                result["assigned_to"] = f"{assignee} ({open_id[:12]}...)"

    return result


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
    "product_analysis": lambda **k: query_product_analysis(k.get("question", "")),
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
    ap.add_argument("--question", default="")
    args = ap.parse_args()

    handler = QUERY_HANDLERS[args.query]
    result = handler(
        user_id=args.user_id,
        title=args.title,
        assignee=args.assignee,
        due=args.due,
        content=args.content,
        question=args.question,
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
        yellow = result.get("yellow", [])
        print(f"🚨 库存预警：{len(red)} 紧急 / {len(yellow)} 中度")
        if red:
            print("\n紧急（应立刻补货）:")
            for it in red[:8]:
                print(f"   • {it['sku']} | 库存 {it['stock']} (安全线 {it.get('safety_line','?')}) | 建议补 {it.get('suggest_replenish','?')}")
        if yellow:
            print("\n中度:")
            for it in yellow[:8]:
                print(f"   • {it['sku']} | 库存 {it['stock']} (安全线 {it.get('safety_line','?')})")
        if not red and not yellow:
            print("\n（暂无预警 SKU）")
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
            print(f"✓ 任务已创建：{result.get('title')}")
            if result.get("assigned_to"):
                print(f"   已指派给 {result['assigned_to']}")
            if result.get("assign_warning"):
                print(f"   ⚠ {result['assign_warning']}")
        else:
            print(f"⚠ {result}")
    elif args.query == "doc_create":
        d = result.get("data", {}) if isinstance(result, dict) else {}
        print(f"✓ 文档创建：{d.get('document', {}).get('title', '?')}")
        url = d.get("document", {}).get("url", "")
        if url:
            print(f"   {url}")
    elif args.query == "product_analysis":
        if result.get("ok"):
            print(f"📊 基于 {result.get('products_count', 0)} 条产品库数据：\n")
            print(result.get("analysis", ""))
        else:
            print(f"⚠ {result.get('_error','')}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\n__JSON__: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
