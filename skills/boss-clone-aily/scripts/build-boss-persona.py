"""老板分身核心 persona 编译器

从 26_老板语料库 表拉所有"已答"记录 → 调 deepseek V4 Pro 提炼成
四层人格档案（OpenPersona 架构：Soul / Body / Faculty / Skill）
→ 写入 personas/boss-persona.md，供 ask-boss.py 调用。

用法：
  python scripts/build-boss-persona.py
  python scripts/build-boss-persona.py --min-answered 30  # 至少答了 30 题才编译
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
    """拉 26 表全部记录，转成 list of dict"""
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
        # 单选字段在 lark 里返回 list（["A 风险偏好"]），取 [0]
        def unwrap(v):
            if isinstance(v, list) and len(v) == 1:
                return v[0]
            return v
        qas.append({k: unwrap(v) for k, v in rec.items()})
    return qas


def build_prompt(qas_answered):
    """按维度组织已答 QA，拼成 deepseek 输入"""
    by_dim = {}
    for qa in qas_answered:
        dim = qa.get("维度", "其他")
        by_dim.setdefault(dim, []).append(qa)

    sections = []
    for dim in sorted(by_dim.keys()):
        sections.append(f"\n## {dim}\n")
        for qa in by_dim[dim]:
            题型 = qa.get("题型", "")
            题目 = qa.get("题目", "")
            答 = qa.get("老板回答", "")
            sections.append(f"- 【{题型}】{题目}\n  → {答}")

    qa_block = "\n".join(sections)

    return f"""你的任务：基于一位女装店老板娘的真实问答记录，提炼出她的人格核心档案。

档案分为四层（OpenPersona 架构）：
1. **Soul（价值观）**—— 她最看重什么、绝不做什么、做女装的初心、红线在哪
2. **Body（表达风格）**—— 她说话的语气、常用句式、口头禅、用词偏好（直接/委婉，简短/详细）
3. **Faculty（判断框架）**—— 她做决策的核心逻辑、风险偏好、典型思考路径
4. **Skill（具体经验）**—— 她在选款、备货、客户、团队、危机这些场景的具体 know-how 和判断模式

以下是她的真实问答记录（按维度组织）：

{qa_block}

请基于以上语料，输出一份 markdown 格式的人格档案。要求：
- 用第一人称（"我"）描述她，让 AI 在使用这份档案时能切换成"她"的视角
- 每层 200-400 字，提炼她语言里的高密度信号，避免空话套话
- 在 Faculty 章节给出 3-5 条她做决策时的"启发式规则"（heuristics）
- 在 Skill 章节按具体场景（选款/备货/客户/团队/危机）分小标题
- 整体风格要让读者觉得"这就是她本人"

直接输出 markdown 内容，不要任何前缀解释。"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-answered", type=int, default=10, help="最少答题数才编译")
    args = ap.parse_args()

    print("[1/3] 拉 26_老板语料库 ...")
    qas = fetch_qa()
    answered = [q for q in qas if q.get("状态") == "已答" and (q.get("老板回答") or "").strip()]
    print(f"  共 {len(qas)} 题，已答 {len(answered)} 题")

    if len(answered) < args.min_answered:
        print(f"\n⚠ 已答题数 {len(answered)} < {args.min_answered}，暂不编译。")
        print(f"   建议老板娘先答完 {args.min_answered} 题（A 风险偏好 30 题最关键），再跑此脚本。")
        # 写一个占位 persona
        os.makedirs(os.path.dirname(PERSONA_PATH), exist_ok=True)
        with open(PERSONA_PATH, "w", encoding="utf-8") as f:
            f.write(f"# 老板娘人格档案（初始化中）\n\n"
                    f"当前已答 {len(answered)}/{len(qas)} 题。\n\n"
                    f"等老板娘答完更多题（推荐至少 {args.min_answered} 题）后，\n"
                    f"再次运行 `python scripts/build-boss-persona.py` 自动重建。\n")
        return

    print(f"[2/3] 调 deepseek V4 Pro 编译人格档案 ...")
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    prompt = build_prompt(answered)
    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "你是一位资深 AI persona 工程师，擅长从问答语料中提炼一个人的人格核心。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=4000,
    )
    persona = resp.choices[0].message.content

    print(f"[3/3] 写入 {PERSONA_PATH}")
    os.makedirs(os.path.dirname(PERSONA_PATH), exist_ok=True)
    header = (f"# 老板娘人格档案\n\n"
              f"_自动编译自 26_老板语料库 表 / 基于 {len(answered)} 道已答题 / "
              f"deepseek-v4-pro 提炼_\n\n---\n\n")
    with open(PERSONA_PATH, "w", encoding="utf-8") as f:
        f.write(header + persona)
    print(f"\n✓ 完成。已基于 {len(answered)} 题语料编译出老板娘人格档案。")
    print(f"  现在可以用 ask-boss.py 调用分身了。")


if __name__ == "__main__":
    main()
