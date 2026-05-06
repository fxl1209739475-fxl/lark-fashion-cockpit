"""omnitask-bridge · 自然语言 → skill 路由

工作流：
  1. 用户发消息（如 "查一下今天销售"）
  2. 优先关键词匹配 skills-registry（节省 AI 调用）
  3. 关键词没命中 → 调 DEEPSEEK 解析意图 + 提取参数
  4. 返回 (skill_id, params, confidence) 或 (None) = 闲聊
  5. 闲聊场景：DEEPSEEK 直接生成自然回复

被 server.py 的 WebSocket 端点 /ws/chat 调用。
"""

import os
import sys
import json
from pathlib import Path
from typing import AsyncIterator, Optional

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

from openai import AsyncOpenAI

# 同目录 import skill_executor
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
_spec = importlib.util.spec_from_file_location("skill_executor",
                                                os.path.join(os.path.dirname(__file__), "skill_executor.py"))
_se = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_se)


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def _build_skills_summary() -> str:
    """把 skills-registry 概要喂给 DEEPSEEK 让它选 skill"""
    reg = _se.load_registry()
    lines = []
    for s in reg.get("skills", []):
        lines.append(
            f"- id={s['id']} | label={s['label']} | category={s['category']} | "
            f"desc={s['description']} | params={list((s.get('params_schema') or {}).keys())}"
        )
    return "\n".join(lines)


async def classify_intent(text: str, user_role: str = "owner") -> dict:
    """调 DEEPSEEK 把 text 分类为 (skill_id, params) 或 casual

    返回 {
      "intent_class": "task|query|notify|content|doc|calendar|casual",
      "skill_id": "..." or null,
      "params": {...},
      "confidence": 0-1,
      "explanation": "...",
    }
    """
    if not DEEPSEEK_API_KEY:
        return {"intent_class": "casual", "skill_id": None, "params": {},
                "confidence": 0, "explanation": "缺 DEEPSEEK_API_KEY"}

    skills_summary = _build_skills_summary()
    prompt = f"""你是 omnitask-bridge 的意图分类器。把用户消息映射到一个具体的 skill 调用，或者判定为闲聊。

# 当前可用的 skill
{skills_summary}

# 用户角色
{user_role}（owner=老板/全权 / designer=设计师 / production=生产 / content=内容）

# 用户消息
"{text}"

# 任务
1. 判断意图类别：task/query/notify/content/doc/calendar/casual
2. 如果不是 casual，从 skill 列表里挑最匹配的 id
3. 提取 skill 需要的参数（params_schema 给出的字段）
4. 给出 0-1 之间的置信度

严格输出 JSON（不要 markdown 代码块）：
{{
  "intent_class": "task|query|notify|content|doc|calendar|casual",
  "skill_id": "skill 的 id，casual 时填 null",
  "params": {{ "key": "value", ... }},
  "confidence": 0.85,
  "explanation": "1 句话解释为什么这么分"
}}"""

    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent_class": "casual", "skill_id": None, "params": {},
                "confidence": 0, "explanation": f"AI 返回非 JSON: {raw[:100]}"}


async def casual_reply(text: str, context: list = None) -> str:
    """闲聊场景调 DEEPSEEK 生成回复"""
    if not DEEPSEEK_API_KEY:
        return "（聊天后端未配置 DEEPSEEK_API_KEY）"

    sys_prompt = """你是 cockpit 系统里的工作助手。用户在驾驶舱聊天窗口跟你说话。
- 简洁直接，不要冗长
- 中文回复
- 如果用户问的是工作相关数据/任务，提示他用更明确的描述（比如"今天销售如何"、"通知 ZC 工厂..."）
- 闲聊就正常聊，不强行扯回工作"""

    msgs = [{"role": "system", "content": sys_prompt}]
    if context:
        msgs.extend(context[-6:])
    msgs.append({"role": "user", "content": text})

    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=msgs,
        temperature=0.5,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()


async def route(text: str, user_role: str = "owner", on_event=None) -> dict:
    """统一入口。on_event 是回调（同步函数），用于推送中间状态。

    返回 {"intent_class", "skill_id", "skill_result"|None, "casual_reply"|None}
    """
    on_event = on_event or (lambda *a, **k: None)

    # 1. 关键词快速匹配
    matched = _se.keyword_match(text)
    if matched:
        intent = {
            "intent_class": matched["category"],
            "skill_id": matched["id"],
            "params": {},
            "confidence": 0.95,
            "explanation": f"关键词命中 {matched['trigger_keywords'][0]}",
            "_via": "keyword",
        }
        on_event({"type": "intent", **intent})
        schema = matched.get("params_schema") or {}
        # 关键词路由的 params 可能不全，让 AI 补一下
        if schema:
            ai_intent = await classify_intent(text, user_role=user_role)
            if ai_intent.get("skill_id") == matched["id"]:
                intent["params"] = ai_intent.get("params", {}) or {}
        # 兜底：如果 schema 里要 question 但还是空，直接用用户原文
        if "question" in schema and not (intent["params"].get("question") or "").strip():
            intent["params"]["question"] = text
        # 同理 message 字段（通知类）也兜底
        if "message" in schema and not (intent["params"].get("message") or "").strip():
            intent["params"]["message"] = text
        result = await _se.execute(matched["id"], intent.get("params", {}), on_event)
        # 用户问题是"分析"类的，把 skill 输出整体当作回复推回（不需要再翻译，已经是自然语言）
        if matched["id"] == "query.product_analysis" and result.get("ok"):
            on_event({"type": "assistant_done", "text": result.get("stdout_tail", "")[:3000]})
        return {"intent": intent, "skill_result": result, "casual_reply": None}

    # 2. AI 分类
    intent = await classify_intent(text, user_role=user_role)
    intent["_via"] = "ai"
    on_event({"type": "intent", **intent})

    if intent["intent_class"] == "casual" or not intent.get("skill_id"):
        reply = await casual_reply(text)
        on_event({"type": "assistant_done", "text": reply,
                  "meta": "（闲聊，未触发 skill）"})
        return {"intent": intent, "skill_result": None, "casual_reply": reply}

    # 3. 执行 skill
    result = await _se.execute(intent["skill_id"], intent.get("params") or {}, on_event)

    # 4. 让 AI 把执行结果翻译成给用户看的自然语言
    if result.get("ok") and result.get("stdout_tail"):
        polished = await polish_skill_output(text, intent, result)
        on_event({"type": "assistant_done", "text": polished})
    else:
        on_event({"type": "assistant_done",
                  "text": f"（{intent['skill_id']} 已执行：{result.get('summary','')}）"})

    return {"intent": intent, "skill_result": result, "casual_reply": None}


async def polish_skill_output(user_text: str, intent: dict, skill_result: dict) -> str:
    """把 skill 的结构化输出翻译成给用户看的自然语言"""
    if not DEEPSEEK_API_KEY:
        return skill_result.get("stdout_tail", "")[:300]

    prompt = f"""用户问："{user_text}"

我已经调了 skill `{intent.get('skill_id')}`，它的输出是：

```
{skill_result.get('stdout_tail', '')[:1500]}
```

请用中文回答用户的问题，保持简洁（3-5 句话），重点突出。如果数字多就用数字，不要展开成段落。
不要 markdown 代码块。"""

    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


# CLI 自检
async def _selftest():
    print("=== chat_router 自检 ===\n")
    cases = [
        "今天销售多少？",
        "有库存预警吗？",
        "通知 ZC 工厂下周一交货",
        "建一个任务给马萍蔓让她出 5 个方案",
        "你叫什么名字？",
    ]
    for t in cases:
        print(f"\n>>> {t}")
        events = []
        result = await route(t, on_event=events.append)
        print(f"  intent: {result['intent'].get('skill_id')} ({result['intent'].get('intent_class')}) "
              f"via={result['intent'].get('_via')} conf={result['intent'].get('confidence')}")
        if result.get("casual_reply"):
            print(f"  reply: {result['casual_reply'][:100]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_selftest())
