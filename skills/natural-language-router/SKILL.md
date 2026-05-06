---
name: lark-fashion-cockpit-natural-language-router
version: 1.0.0
description: "自然语言路由 Skill — 让飞书机器人听懂人话，把员工口语自动路由到 35 个 sub-skill 并提取参数。员工不用记关键词，直接说人话："今天卖得咋样" → morning-report，"DRS-0429 配什么" → product-matching，"拆这个抖音 URL" → blogger-monitor。让公司全员（含技术小白和年龄大的）都能在飞书移动端用 cockpit。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 自然语言路由 — 让全公司 70 人都能用飞书 cockpit

> **🎯 痛点：** 现在员工要在飞书发"巡检任务"/"问老板"/"拆 NO.001"等**固定关键词**才能触发 skill。70 人记不住 + 不愿意记。

> **核心价值：** 员工说人话 → DeepSeek 识别意图 → 自动路由到 35 个 sub-skill 之一 + 提取参数。**0 学习成本，移动端通用**。

---

## 一、升级前 vs 升级后

| 员工真实说的话 | 升级前（关键词路由）| 升级后（自然语言路由）|
|---|---|---|
| "今天卖得咋样" | ❌ 无关键词命中 | ✅ → morning-report |
| "看下任务情况" | ✅（巧合）| ✅ |
| "DRS-0429 配什么款好" | ❌ | ✅ → product-matching, product_id=DRS-0429 |
| "拆这条抖音 [URL]" | ❌（要写"拆 [URL]"）| ✅ → blogger-monitor, url=URL |
| "马萍蔓任务到点没" | ❌ | ✅ → task-tracker, filter owner=马萍蔓 |
| "新品 KNT-0501 该备多少件" | ❌ | ✅ → launch-decision, product_id=KNT-0501 |
| "老板会怎么决定这事" | ✅（碰巧命中）| ✅ → boss-clone-aily |
| "工厂申丽媛今天交了几单" | ❌ | ✅ → production-supplier, supplier=申丽媛 |

---

## 二、技术实现（覆盖到 event-listener.py 现有路由前）

```python
# scripts/intent-router.py
from openai import OpenAI

# 35 个 skill 注册表（id + 触发关键词 + 参数 schema）
SKILLS = [
    {"id": "morning-report",
     "desc": "查看今日销售/库存/直播 综合数据",
     "trigger_examples": ["今天卖得怎么样", "今日数据", "经营晨报"],
     "params": []},
    {"id": "task-tracker",
     "desc": "巡检任务进度+逾期升级",
     "trigger_examples": ["看下任务", "巡检任务", "马萍蔓任务咋样"],
     "params": [{"name": "owner", "type": "string", "optional": true}]},
    {"id": "product-matching",
     "desc": "给产品配搭配款",
     "trigger_examples": ["DRS-XXX 配什么", "搭配推荐"],
     "params": [{"name": "product_id", "required": true}]},
    {"id": "blogger-monitor",
     "desc": "拆解抖音/快手视频脚本",
     "trigger_examples": ["拆这个视频", "分析这条视频"],
     "params": [{"name": "url", "required": true}]},
    {"id": "launch-decision",
     "desc": "新品下单决策建议",
     "trigger_examples": ["这款下多少件", "翻单几件", "备货建议"],
     "params": [{"name": "product_id", "required": true}]},
    {"id": "boss-clone-aily",
     "desc": "问老板娘 AI 分身",
     "trigger_examples": ["问老板", "老板会怎么说"],
     "params": [{"name": "question", "required": true}]},
    {"id": "blogger-monitor",
     "desc": "对标博主每日监控+TOP N",
     "trigger_examples": ["看竞品博主", "今日同行 TOP"],
     "params": []},
    # ... 其余 28 个 skill 同样注册
]

ROUTER_PROMPT = """你是飞书 cockpit 的意图识别助手。

【可用 skill 清单】
{skills_json}

【用户消息】
{user_message}

请输出 JSON：
{{
  "skill_id": "最匹配的 skill id（不匹配则返回 null）",
  "params": {{ 解析出来的参数 }},
  "confidence": 0-1 浮点数,
  "fallback_message": "如果不匹配，给用户的友好提示"
}}

注意：
- 员工说话很口语化，要宽容理解（"卖咋样" = "查销售"）
- 提取参数（产品 ID / URL / 人名）要精确
- 不匹配时不要瞎猜，confidence 低于 0.5 就返回 null
"""

def route_intent(user_message: str):
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], 
                    base_url=os.environ["DEEPSEEK_BASE_URL"])
    resp = client.chat.completions.create(
        model="deepseek-v4-flash",  # 用 Flash 省 token
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(
            skills_json=json.dumps(SKILLS, ensure_ascii=False),
            user_message=user_message,
        )}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)
```

---

## 三、集成到 event-listener.py

```python
# 在 handle_message() 里，关键词路由前先跑自然语言路由
def handle_message(event, simulate=False):
    text = extract_text(event["content"])

    # ① 先跑自然语言路由（DeepSeek 识别意图）
    intent = route_intent(text)
    if intent and intent.get("confidence", 0) >= 0.7:
        skill_id = intent["skill_id"]
        params = intent.get("params", {})
        # 转发到对应 skill 的执行器
        execute_skill(skill_id, params, chat_id, message_id)
        return

    # ② confidence < 0.7 时回退到原有关键词路由
    matched = route(text)  # 原有关键词路由
    ...

    # ③ 都没命中，给用户友好提示
    if intent and intent.get("fallback_message"):
        send_card(chat_id, "🤔 没听懂", intent["fallback_message"], "yellow")
```

---

## 四、典型对话示例

```
设计师小王（首次用，啥都不知道）
→ 飞书群里随便问："给我看下今天的销售情况吧"

natural-language-router 识别：
  skill_id = "morning-report"
  params = {}
  confidence = 0.92

→ 自动调 morning-report.ps1
→ 1 秒后回复完整经营晨报卡片
→ 员工愣住："这玩意听得懂人话！"
```

```
工厂主管申丽媛（移动端飞书 app）
→ "DRS-0429 这款今天能下单不"

natural-language-router 识别：
  skill_id = "launch-decision"
  params = {"product_id": "DRS-0429"}
  confidence = 0.88

→ 自动调 launch-decision skill
→ 4 维信号分析 + 老板分身复审
→ 给出"建议下 800 件 / 尺码占比 / 风险提示"
```

```
新员工小张（不知道 cockpit 有啥能力）
→ "我能用你做啥"

natural-language-router 识别：
  skill_id = null
  confidence = 0.3
  fallback_message = "你可以问我：今天数据 / 任务进度 / 产品搭配 / 拆视频 / ..."

→ 给小张一份能力清单
```

---

## 五、性能 + 成本

- **DeepSeek V4 Flash**：每次路由约 1.5K input + 200 output token = **¥0.0003/次**
- **响应延迟**：约 1-2 秒（员工感知不到）
- 一天 70 人 × 平均 10 次 = 700 次/天 = **¥0.21/天**
- 一年 ¥80（基本免费）

**对照**：每个员工每个月省 30 分钟"记关键词" = 70 × 30min × 12 = **252 工时/年**。投产比 ROI 极高。

---

## 六、与其他 skill 联动

- 是 35 个 sub-skill 的"前置网关" — 改 1 个 skill 这里也要改注册表
- 联动 [`event-router`](../event-router/SKILL.md)（升级版）

---

## 七、覆盖到的"移动端 + 全员"场景

| 谁 | 场景 | 方式 |
|---|---|---|
| 老板娘（移动端飞书）| 在出差路上问"今天卖得咋样" | 飞书机器人 → 自然语言路由 → morning-report |
| 工厂申丽媛 | "今天我交了几单货"| 路由 → production-supplier |
| 主播小马 | "下场直播该带什么货"| 路由 → live-streaming + product-matching |
| 客服小红 | "客户赵姐之前买过啥"| 路由 → private-domain |
| 老板娘老公（不懂 IT）| "我们家店今天赚多少"| 路由 → profit-analysis |

---

## 八、参考

- 主路由脚本：[`scripts/intent-router.py`](./scripts/intent-router.py)
- 35 skill 注册表：[`references/skills-registry.json`](./references/skills-registry.json)
- 集成 event-listener 改造点：[`references/event-listener-patch.md`](./references/event-listener-patch.md)
- 典型对话集（用于优化 prompt）：[`examples/conversation-cases.md`](./examples/conversation-cases.md)
