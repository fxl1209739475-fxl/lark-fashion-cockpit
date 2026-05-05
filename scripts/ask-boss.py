"""老板分身查询 — RAG 检索 + persona_core 合成回答

流程：
  问题 → 26_老板语料库 关键词检索 top-5 → 拼 prompt（persona_core + few-shot QA + 新问题）
  → deepseek V4 Pro → 输出老板分身回答 → 可选发飞书卡片

用法：
  python scripts/ask-boss.py -q "这款连衣裙备 500 还是 1000？"
  python scripts/ask-boss.py -q "..." --reply-chat-id oc_221a68cb4ab...
"""

import subprocess, json, os, sys, argparse, re
from openai import OpenAI

BASE = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
TABLE = "tblroqP4Kuz8a1yq"
LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
PROJECT_ROOT = r"C:\Users\冯兴龙\lark-fashion-cockpit"
PERSONA_PATH = os.path.join(PROJECT_ROOT, "personas", "boss-persona.md")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"


def fetch_qa():
    """拉 26 表全部记录"""
    result = subprocess.run(
        [LARK_CLI, "base", "+record-list", "--base-token", BASE, "--table-id", TABLE,
         "--limit", "200", "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"record-list failed: {result.stderr[:300]}")
    data = json.loads(result.stdout)
    fields = data["data"]["fields"]
    rows = data["data"]["data"]
    qas = []
    for row in rows:
        rec = dict(zip(fields, row))
        def unwrap(v):
            if isinstance(v, list) and len(v) == 1:
                return v[0]
            return v
        qas.append({k: unwrap(v) for k, v in rec.items()})
    return qas


def char_bigrams(s):
    """字符 bigram 集合 — 中文检索的简易方法"""
    s = re.sub(r"\s+", "", s or "")
    return set(s[i:i+2] for i in range(len(s)-1)) if len(s) >= 2 else set([s])


def score_qa(query, qa):
    """关键词重合度：query 与 题目+回答 的 bigram Jaccard"""
    q_grams = char_bigrams(query)
    text = (qa.get("题目", "") or "") + " " + (qa.get("老板回答", "") or "")
    t_grams = char_bigrams(text)
    if not q_grams or not t_grams:
        return 0
    return len(q_grams & t_grams) / max(len(q_grams), 1)


def top_k_qa(query, qas, k=5):
    answered = [q for q in qas if q.get("状态") == "已答" and (q.get("老板回答") or "").strip()]
    scored = [(score_qa(query, qa), qa) for qa in answered]
    scored.sort(key=lambda x: -x[0])
    return [qa for s, qa in scored[:k] if s > 0]


def load_persona():
    if os.path.exists(PERSONA_PATH):
        with open(PERSONA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return None


def build_prompt(persona, top_qa, question):
    qa_block = ""
    if top_qa:
        qa_block = "\n以下是几个相关的真实 Q&A few-shot（学习老板娘的语气和判断逻辑）：\n\n"
        for i, qa in enumerate(top_qa, 1):
            qa_block += f"【参考 {i}】\n问：{qa.get('题目','')}\n答：{qa.get('老板回答','')}\n\n"

    persona_block = ""
    if persona:
        persona_block = f"\n以下是老板娘的人格档案（你需要扮演她）：\n\n{persona}\n\n"

    return f"""你现在扮演一位女装店老板娘的 AI 分身。
{persona_block}
{qa_block}
===

现在团队成员/客户来问你新问题：

> {question}

请用老板娘本人的语气和判断逻辑回答。要求：
- 先给结论（一句话），再 1-3 句简短理由
- 直接、有立场，不要打太极
- 如果是"破例 / 边界 / 极端"类问题，要清晰说出红线
- 如果信息不足，说出你需要什么再判断（不要瞎编）
- 不要说"作为 AI"或"我是分身"，就以她本人语气回答"""


def call_deepseek(prompt):
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "你是一位精明、决策果断的女装店老板娘的 AI 分身。回答要简洁、直接、有立场。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=600,
    )
    return resp.choices[0].message.content


def send_card(chat_id, question, answer, refs):
    """把分身回答发成飞书交互卡片"""
    ref_text = ""
    if refs:
        ref_text = "\n\n---\n**参考的历史回答：**\n"
        for i, qa in enumerate(refs[:3], 1):
            ref_text += f"{i}. {qa.get('题目','')[:30]}...\n"

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "👑 老板分身的判断"},
            "template": "purple",
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md",
                "content": f"**问题：** {question}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md",
                "content": f"**老板分身回答：**\n\n{answer}{ref_text}"}},
            {"tag": "note", "elements": [{"tag": "plain_text",
                "content": "基于 26_老板语料库 + deepseek-v4-pro 实时蒸馏。回答仅供参考，重大决策建议找真人复核。"}]},
        ]
    }
    card_json = json.dumps(card, ensure_ascii=False, separators=(',', ':'))
    subprocess.run(
        [LARK_CLI, "im", "+messages-send",
         "--chat-id", chat_id, "--msg-type", "interactive",
         "--content", card_json],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--question", required=True, help="问老板的问题")
    ap.add_argument("--reply-chat-id", default=None, help="飞书 chat_id；给了就发卡片，不给就 stdout")
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    qas = fetch_qa()
    answered = [q for q in qas if q.get("状态") == "已答" and (q.get("老板回答") or "").strip()]

    if not answered:
        msg = "⚠ 老板娘还没开始答题，分身暂时还没办法回答。请先去 26_老板语料库 答几道题再来。"
        if args.reply_chat_id:
            send_card(args.reply_chat_id, args.question, msg, [])
        print(msg)
        return

    top = top_k_qa(args.question, qas, args.top_k)
    persona = load_persona()
    prompt = build_prompt(persona, top, args.question)
    answer = call_deepseek(prompt)

    print(f"\n【老板分身回答】\n{answer}\n")
    if top:
        print(f"\n参考的 top-{len(top)} 历史 QA：")
        for i, qa in enumerate(top, 1):
            print(f"  {i}. [{qa.get('维度','')}] {qa.get('题目','')[:40]}...")

    if args.reply_chat_id:
        send_card(args.reply_chat_id, args.question, answer, top)


if __name__ == "__main__":
    main()
