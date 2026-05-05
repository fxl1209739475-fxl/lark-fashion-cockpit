"""个人 AI 镜子 — 每晚 22:00 自动给员工生成"今日成长复盘 + SOP 沉淀建议"

数据源：飞书 IM / 妙记 / 任务 / 审批 / 文档 / 日历 — 员工今日所有留痕
分析模型：DeepSeek V4 Pro
输出：① 飞书私聊员工本人成长卡片 ② 自动写员工个人飞书文档 ③ 沉淀 SOP 候选到个人 wiki

用法：
  # 单个员工
  python scripts/personal-mirror.py --user-open-id ou_xxx --date 2026-05-05

  # 批量（cron 每晚 22:00 触发所有注册员工）
  python scripts/personal-mirror.py --all
"""

import subprocess, json, os, argparse, sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from openai import OpenAI

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
ROLE_REGISTRY_PATH = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\multi-user-private-channels\scripts\role-registry.json"

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")

PROMPT = """你是员工的 AI 镜子，给 {name}（{role}）生成今日成长复盘。

【今日数据】
- IM 聊天摘要：{im_summary}
- 参加会议：{meetings}
- 完成任务：{tasks_done}
- 创建任务：{tasks_created}
- 编辑文档：{docs}
- 发起审批：{approvals}

【近 7 天历史模式】（用于"反复出现"检测）
{recent_patterns}

请输出 JSON：
{{
  "today_summary": "今日做了什么的 5 条要点（每条 30 字内）",
  "highlights": ["做得好的 1-3 条，含'为什么好'"],
  "improvements": ["待改进的 1-3 条，含'怎么改'"],
  "todos_short": ["短期待办（明天/本周）3-5 条"],
  "todos_long": [{{"goal": "长期目标", "progress": "X/Y", "trend": "向好/正常/堪忧"}}],
  "sop_triggers": [
    {{
      "type": "重复请求 | 反复配合 | 历史相似",
      "topic": "什么主题",
      "frequency": 数字,
      "draft_title": "建议沉淀的 SOP 标题",
      "draft_content": "100 字内 SOP 草稿",
      "time_saved": "下次省多少分钟"
    }}
  ]
}}

判断 sop_triggers 的标准（严格）：
- 同关键词出现 ≥ 3 次（含今日 + 近 7 天）
- 同事反复来配合 ≥ 3 次
- 不到阈值 sop_triggers 返回 []，不要瞎编"""


def fetch_today_data(user_open_id: str, date_str: str) -> dict:
    """拉员工今天的飞书全留痕（mock 版 — 真生产要接 lark-cli api）"""
    # TODO: 实际生产需要调：
    # 1. lark-cli im messages list（按 sender 过滤）
    # 2. lark-cli vc +notes
    # 3. lark-cli task +get-my-tasks
    # 4. lark-cli docs / base history
    # 5. lark-cli calendar +agenda
    # 这里返回 mock 结构演示
    return {
        "im_summary": "今日发了 38 条消息：跟工厂申丽媛 8 条（讨论 KNT-0402 色卡），群里 15 条，跟内容编辑 10 条（改图反馈），其他 5 条",
        "meetings": [{"title": "上新企划会", "duration_min": 23, "summary": "讨论 5 月第 2 周新品排期"}],
        "tasks_done": ["DRS-0429-FL 主图设计（提前 14m）"],
        "tasks_created": ["DRS-0501 草稿"],
        "docs": ["编辑「2026-Q2 设计 SOP」3 次"],
        "approvals": [],
        "recent_patterns": {
            "重复关键词": [{"keyword": "色卡", "freq_7d": 5}, {"keyword": "DRS-0429", "freq_7d": 8}],
            "重复请求方": [{"from": "申丽媛", "topic": "色卡对接", "times_7d": 5}],
        },
    }


def analyze_with_deepseek(user_config: dict, data: dict) -> dict:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("缺 DEEPSEEK_API_KEY")
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    prompt = PROMPT.format(
        name=user_config.get("name", ""),
        role=user_config.get("role", ""),
        im_summary=data["im_summary"],
        meetings=json.dumps(data["meetings"], ensure_ascii=False),
        tasks_done="; ".join(data["tasks_done"]),
        tasks_created="; ".join(data["tasks_created"]),
        docs="; ".join(data["docs"]),
        approvals=json.dumps(data["approvals"], ensure_ascii=False),
        recent_patterns=json.dumps(data["recent_patterns"], ensure_ascii=False),
    )
    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def build_card(user_config: dict, analysis: dict, date_str: str) -> dict:
    """构建发给员工本人的成长卡片"""
    name = user_config.get("name", "")
    addr = name[1:] + "姐" if len(name) >= 3 else name

    elements = [
        {"tag": "div", "text": {"tag": "lark_md",
            "content": f"📊 今日复盘 · {date_str}"}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content":
            "**✅ 今日做了什么**\n" + "\n".join(f"• {x}" for x in analysis["today_summary"])}},
        {"tag": "div", "text": {"tag": "lark_md", "content":
            "**🌟 做得好**\n" + "\n".join(f"• {x}" for x in analysis["highlights"])}},
        {"tag": "div", "text": {"tag": "lark_md", "content":
            "**⚠️ 待改进**\n" + "\n".join(f"• {x}" for x in analysis["improvements"])}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content":
            "**📋 短期待办**\n" + "\n".join(f"- [ ] {x}" for x in analysis["todos_short"])}},
        {"tag": "div", "text": {"tag": "lark_md", "content":
            "**🎯 长期目标进度**\n" + "\n".join(
                f"• {g['goal']}：{g['progress']}（{g['trend']}）"
                for g in analysis["todos_long"])}},
    ]

    # SOP 沉淀触发部分
    if analysis.get("sop_triggers"):
        elements.append({"tag": "hr"})
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content":
            "🚨 **SOP 沉淀建议** — 这是该写下来的事！"}})
        for s in analysis["sop_triggers"]:
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content":
                f"**{s['draft_title']}**\n"
                f"触发原因：{s['type']} · 「{s['topic']}」 出现 {s['frequency']} 次\n"
                f"草稿：{s['draft_content']}\n"
                f"💰 沉淀后预计省 {s['time_saved']}/月"}})
            elements.append({"tag": "action", "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "✅ 确认沉淀到我的 SOP 库"},
                 "type": "primary", "value": {"action": "confirm_sop", "title": s["draft_title"]}},
                {"tag": "button", "text": {"tag": "plain_text", "content": "❌ 不沉淀"},
                 "type": "default", "value": {"action": "dismiss_sop"}},
            ]})

    elements.append({"tag": "hr"})
    elements.append({"tag": "note", "elements": [{"tag": "plain_text",
        "content": "私密复盘，不发群、不抄老板。每晚 22:00 自动生成。"}]})

    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text",
                              "content": f"🪞 {addr} · {date_str} 成长复盘"},
                   "template": "purple"},
        "elements": elements,
    }


def send_to_user_p2p(user_open_id: str, card: dict):
    """飞书私聊发给员工本人（不发群）"""
    card_json = json.dumps(card, ensure_ascii=False, separators=(',', ':'))
    cmd = [LARK_CLI, "im", "+messages-send",
           "--user-id", user_open_id, "--msg-type", "interactive",
           "--content", card_json]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
    return r.returncode == 0


def write_to_personal_doc(user_config: dict, analysis: dict, date_str: str):
    """追加到员工个人成长档案文档"""
    # TODO: 真生产用 lark-cli docs +update 追加 block
    print(f"  → 追加到员工 {user_config['name']} 的成长档案文档")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user-open-id", help="单个员工 open_id")
    ap.add_argument("--all", action="store_true", help="批量跑所有注册员工")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = ap.parse_args()

    with open(ROLE_REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    if args.all:
        users = list(registry["users"].items())
    elif args.user_open_id:
        cfg = registry["users"].get(args.user_open_id)
        if not cfg:
            print(f"⚠ 用户未注册: {args.user_open_id}")
            sys.exit(1)
        users = [(args.user_open_id, cfg)]
    else:
        print("--user-open-id 或 --all 二选一")
        sys.exit(1)

    for open_id, cfg in users:
        user_config = {
            "open_id": open_id,
            "name": cfg.get("name"),
            "role": cfg.get("role"),
        }
        print(f"\n========== {user_config['name']} ({user_config['role']}) ==========")
        print(f"[1/4] 拉今日飞书全留痕 ...")
        data = fetch_today_data(open_id, args.date)
        print(f"[2/4] DeepSeek 分析 ...")
        analysis = analyze_with_deepseek(user_config, data)
        print(f"  → {len(analysis.get('sop_triggers', []))} 个 SOP 沉淀建议")
        print(f"[3/4] 构建卡片 ...")
        card = build_card(user_config, analysis, args.date)
        print(f"[4/4] 私聊员工 ...")
        ok = send_to_user_p2p(open_id, card)
        print(f"  {'✓' if ok else '✗'} 发送")
        write_to_personal_doc(user_config, analysis, args.date)


if __name__ == "__main__":
    main()
