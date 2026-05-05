"""开源雷达 — 每日扫 GitHub + AI 评估和女装电商相关度 + 写飞书知识库 + 发汇报卡片

用法：
  python scripts/scan-github.py                    # 全扫
  python scripts/scan-github.py --keyword "ai"     # 单关键词
  python scripts/scan-github.py --min-score 7      # 调高门槛
  python scripts/scan-github.py --no-card          # 不发卡片只更新表

环境变量：
  DEEPSEEK_API_KEY    - DeepSeek API key
  GITHUB_TOKEN        - 可选，限流 60→5000/h
  LARK_FASHION_COCKPIT_BASE_TOKEN  - 飞书 base
  LARK_FASHION_COCKPIT_BOSS_CHAT   - 老板群 chat_id
"""

import subprocess, json, os, argparse, sys, time
from datetime import datetime, timedelta
import httpx
from openai import OpenAI

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
GITHUB_API = "https://api.github.com"
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 关键词（每天会扫这些 keyword 的最新项目）
KEYWORDS = [
    "ecommerce", "fashion", "retail", "shopify",
    "inventory management", "order management",
    "AI agent", "automation", "workflow",
    "livestream", "douyin", "tiktok",
    "operations dashboard", "BI tool",
    "customer service", "chatbot",
]

DEEPSEEK_PROMPT = """你是一位资深 AI/开源专家，专门为女装电商品牌主筛选 GitHub 项目。

【项目信息】
名称：{repo_name}
URL：{html_url}
描述：{description}
star 数：{stars}
语言：{language}
最近更新：{updated_at}

【组织背景】
本组织是一家女装电商品牌（lark-fashion-cockpit），核心业务：
- 4 平台运营（淘宝/抖音/小红书/视频号）
- 直播带货 / 短视频内容
- 团队协作（设计师 / 工厂 / 主播 / 客服 / 老板娘）
- 已有飞书 base 25 张表 + 32 个 sub-skill

【请输出 JSON（不要 markdown 代码块包裹）】
{{
  "中文摘要": "1-2 句中文",
  "相关度评分": 1-10 整数,
  "应用场景": "女装直接用 | 电商通用 | 管理工具 | AI 基础设施 | 不相关",
  "改造思路": "具体到改哪几个字段/接哪几个 API/替换什么逻辑/联动哪个 cockpit skill",
  "工时预估小时": 整数,
  "判断理由": "1-2 句"
}}

严格打分，不相关给 1-2 分。"""


def github_request(path, params=None):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{GITHUB_API}{path}"
    r = httpx.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_trending(language="", since="daily"):
    """GitHub 没官方 trending API，用 search 模拟（按近 7 天创建+star 排序）"""
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    q = f"created:>{cutoff}"
    if language:
        q += f" language:{language}"
    res = github_request("/search/repositories", {"q": q, "sort": "stars", "order": "desc", "per_page": 25})
    return res.get("items", [])


def fetch_keyword_results(keyword, days=3, top=10):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    q = f"{keyword} pushed:>{cutoff}"
    res = github_request("/search/repositories", {"q": q, "sort": "stars", "order": "desc", "per_page": top})
    return res.get("items", [])


def evaluate_with_deepseek(repo):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("缺 DEEPSEEK_API_KEY")
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    prompt = DEEPSEEK_PROMPT.format(
        repo_name=repo.get("full_name", ""),
        html_url=repo.get("html_url", ""),
        description=repo.get("description") or "无描述",
        stars=repo.get("stargazers_count", 0),
        language=repo.get("language") or "未知",
        updated_at=repo.get("updated_at", ""),
    )
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def write_to_base(repo, eval_result):
    base = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN")
    table = os.environ.get("TABLE_OPENSOURCE_RADAR")
    if not base or not table:
        print(f"  [skip base] 未配 LARK_FASHION_COCKPIT_BASE_TOKEN / TABLE_OPENSOURCE_RADAR")
        return
    fields = {
        "项目名": repo["full_name"],
        "GitHub URL": repo["html_url"],
        "star 数": repo.get("stargazers_count", 0),
        "最近更新": repo.get("updated_at", ""),
        "英文描述": repo.get("description") or "",
        "中文摘要": eval_result.get("中文摘要", ""),
        "相关度评分": eval_result.get("相关度评分", 0),
        "应用场景": eval_result.get("应用场景", ""),
        "改造思路": eval_result.get("改造思路", ""),
        "工时预估": eval_result.get("工时预估小时", 0),
        "判断理由": eval_result.get("判断理由", ""),
        "状态": "待评估",
        "扫描时间": int(time.time() * 1000),
    }
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "radar.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False)
    subprocess.run(
        [LARK_CLI, "base", "+record-upsert",
         "--base-token", base, "--table-id", table,
         "--json", "@./radar.json"],
        cwd=os.path.dirname(tmp), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )


def send_card(top_results):
    chat = os.environ.get("LARK_FASHION_COCKPIT_BOSS_CHAT")
    if not chat:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    elements = [{"tag": "div", "text": {"tag": "lark_md",
        "content": f"📊 今日扫描：{len(top_results)} 个高相关项目"}}]
    for i, (repo, ev) in enumerate(top_results[:5], 1):
        elements.append({"tag": "hr"})
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"**[{i}] {repo['full_name']}** · 相关度 {ev['相关度评分']}/10 · ⭐ {repo.get('stargazers_count',0)}\n"
                       f"{ev['中文摘要']}\n"
                       f"📋 工时 {ev.get('工时预估小时',0)}h | 场景: {ev.get('应用场景','')}"}})
        elements.append({"tag": "action", "actions": [
            {"tag": "button", "text": {"tag": "plain_text", "content": "▶ 看 GitHub"},
             "type": "default", "url": repo["html_url"]},
        ]})
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"🛰 开源雷达 · {today} 早报"},
                   "template": "blue"},
        "elements": elements,
    }
    cmd = [LARK_CLI, "im", "+messages-send",
           "--chat-id", chat, "--msg-type", "interactive",
           "--content", json.dumps(card, ensure_ascii=False, separators=(',', ':'))]
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", default=None)
    ap.add_argument("--min-score", type=int, default=6)
    ap.add_argument("--no-card", action="store_true")
    ap.add_argument("--limit", type=int, default=30, help="评估上限（控成本）")
    args = ap.parse_args()

    print(f"[1/5] 拉 GitHub 项目 ...")
    repos = []
    if args.keyword:
        repos = fetch_keyword_results(args.keyword, days=7, top=args.limit)
    else:
        # trending（最近 7 天创建 + star 高的）
        repos.extend(fetch_trending())
        # 关键词扫
        for kw in KEYWORDS[:5]:  # 控量
            try:
                repos.extend(fetch_keyword_results(kw, days=3, top=5))
            except Exception as e:
                print(f"  [warn] keyword '{kw}' failed: {e}")

    # 去重
    seen = set()
    uniq = []
    for r in repos:
        if r["html_url"] not in seen:
            seen.add(r["html_url"])
            uniq.append(r)
    print(f"  → {len(uniq)} 个独立项目")

    # 限制评估数量（控 DeepSeek 成本）
    uniq = uniq[:args.limit]

    print(f"[2/5] DeepSeek 评估 {len(uniq)} 个项目 ...")
    results = []
    for i, repo in enumerate(uniq, 1):
        try:
            ev = evaluate_with_deepseek(repo)
            score = ev.get("相关度评分", 0)
            print(f"  [{i}/{len(uniq)}] {repo['full_name'][:40]} → {score}/10")
            if score >= args.min_score:
                results.append((repo, ev))
        except Exception as e:
            print(f"  [{i}] {repo['full_name'][:30]} 评估失败: {e}")

    print(f"[3/5] 写入 28 表 + 知识库（{len(results)} 个高分项目）...")
    for repo, ev in results:
        try:
            write_to_base(repo, ev)
        except Exception as e:
            print(f"  [warn] 写表失败: {e}")

    # 按相关度排序
    results.sort(key=lambda x: -x[1].get("相关度评分", 0))

    print(f"[4/5] TOP {min(5, len(results))} 改造建议：")
    for i, (repo, ev) in enumerate(results[:5], 1):
        print(f"  [{i}] {repo['full_name']} · {ev['相关度评分']}/10 · 工时 {ev.get('工时预估小时',0)}h")
        print(f"      {ev.get('改造思路', '')[:100]}")

    if not args.no_card and results:
        print(f"[5/5] 发飞书汇报卡片 ...")
        send_card(results)
        print(f"  ✓ 已发卡片")
    else:
        print(f"[5/5] 跳过卡片")


if __name__ == "__main__":
    main()
