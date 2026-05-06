"""自然语言意图路由 — 把员工口语映射到 35 个 sub-skill 之一

用法（独立测试）：
  python scripts/intent-router.py "今天卖得咋样"
  python scripts/intent-router.py "DRS-0429 配什么款"

集成到 event-listener.py：
  from intent_router import route_intent
  intent = route_intent(user_text)
  if intent["skill_id"] and intent["confidence"] >= 0.7:
      execute_skill(intent["skill_id"], intent["params"], ...)
"""

import os, json, sys
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL_FAST = os.environ.get("DEEPSEEK_MODEL_FAST", "deepseek-v4-flash")

# 35 个 skill 注册表
SKILLS_REGISTRY = [
    # 公司经营
    {"id": "morning-report", "desc": "今日 4 平台销售/库存/直播综合数据 + AI 分析",
     "examples": ["今天卖得怎么样", "今日数据", "经营晨报", "店铺今天咋样"]},
    {"id": "profit-analysis", "desc": "利润分析单品/平台双维拆解",
     "examples": ["哪些款赚钱", "利润分析", "净利率", "店赚多少"]},
    {"id": "task-collaboration", "desc": "任务协作派工",
     "examples": ["分配任务", "派工", "建任务"]},

    # 商品中心
    {"id": "product-library", "desc": "产品库元素标签",
     "examples": ["产品库", "查产品"]},
    {"id": "new-launch-planning", "desc": "上新企划波段排期",
     "examples": ["上新计划", "下波段什么时候上"]},
    {"id": "stock-replenishment", "desc": "库存补货预警",
     "examples": ["库存", "补货", "DRS-XXX 还有几件"]},
    {"id": "feedback-returns", "desc": "退货反馈分析",
     "examples": ["退货", "退货率", "DRS-XXX 退货为啥"]},
    {"id": "competitor-monitor", "desc": "竞品趋势监控",
     "examples": ["看趋势", "今年流行什么", "同行卖什么"]},
    {"id": "product-matching", "desc": "AI 产品搭配推荐",
     "examples": ["DRS-XXX 配什么", "搭配推荐", "主图穿搭"]},
    {"id": "launch-decision", "desc": "新品下单决策 4 维信号",
     "examples": ["这款下多少件", "翻单几件", "备货建议", "DRS-XXX 该备多少"]},

    # 销售增长
    {"id": "platform-analytics", "desc": "4 平台销售分析",
     "examples": ["平台数据", "抖音卖得咋样", "淘宝今天 GMV"]},
    {"id": "live-streaming", "desc": "直播管理库存匹配",
     "examples": ["直播", "今日直播总结", "下场直播带什么"]},
    {"id": "private-domain", "desc": "私域客户运营",
     "examples": ["客户", "私域", "赵姐之前买过啥"]},

    # 工作流
    {"id": "task-lifecycle", "desc": "任务生命周期巡检 + 升级逾期",
     "examples": ["看下任务", "巡检任务", "任务追踪", "逾期"]},
    {"id": "blogger-monitor", "desc": "对标博主监控 + 视频脚本拆解（合一）",
     "examples": ["看竞品博主", "今日同行 TOP", "博主排行", "拆这个视频", "拆 [URL]"]},

    # AI 数字员工
    {"id": "boss-clone-aily", "desc": "问老板娘 AI 分身（基于 200 题语料）",
     "examples": ["问老板", "老板会怎么决定", "老板分身"]},
    {"id": "lingo-fashion-glossary", "desc": "查女装术语词典",
     "examples": ["DRS 什么意思", "卷王是什么", "ZC 工厂在哪"]},

    # 视频 / 内容
    {"id": "content-pipeline", "desc": "内容创作工作流",
     "examples": ["写文案", "做内容", "选题"]},

    # 开源雷达
    {"id": "opensource-radar", "desc": "开源项目每日扫描 + 改造建议",
     "examples": ["开源雷达", "今日开源推荐", "github 上有啥新东西"]},

    # 其余 14 个 skill 同样注册（略）...
]


ROUTER_PROMPT_TEMPLATE = """你是飞书 cockpit 的意图识别助手。员工的话比较口语化，要宽容理解。

【可用 skill 清单】
{skills}

【用户消息】
{message}

请输出 JSON（不要 markdown 代码块包裹）：
{{
  "skill_id": "最匹配的 skill id（不匹配返回 null）",
  "params": {{}},
  "confidence": 0-1 浮点数,
  "fallback_message": "不匹配时给用户的友好提示，列 3-5 个能干的事"
}}

参数提取规则：
- product_id：DRS-XXXX-XX / KNT-XXXX-XX / BLK-XXXX-XX 这种编码
- url：https:// 开头的链接
- owner：人名（马萍蔓 / 申丽媛 / 朱健豪等）

confidence 评分：
- 关键词命中 + 上下文清晰 → 0.9+
- 模糊但能猜 → 0.7
- 不太对 → 0.5
- 完全不相关 → 0.1

confidence < 0.5 就返回 skill_id=null + 给 fallback_message
"""


def route_intent(message: str):
    if not DEEPSEEK_API_KEY:
        return {"skill_id": None, "params": {}, "confidence": 0,
                "fallback_message": "未配 DEEPSEEK_API_KEY，无法识别意图"}

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    skills_compact = [{"id": s["id"], "desc": s["desc"], "ex": s["examples"][:3]}
                      for s in SKILLS_REGISTRY]
    prompt = ROUTER_PROMPT_TEMPLATE.format(
        skills=json.dumps(skills_compact, ensure_ascii=False),
        message=message,
    )
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL_FAST,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        if not raw or not raw.strip():
            return {"skill_id": None, "params": {}, "confidence": 0,
                    "fallback_message": "DeepSeek 返回空响应"}
        # 调试：把原始响应也打出来
        print(f"[debug] raw response: {raw[:500]}", file=sys.stderr)
        return json.loads(raw)
    except Exception as e:
        return {"skill_id": None, "params": {}, "confidence": 0,
                "fallback_message": f"识别失败: {type(e).__name__}: {e}"}


def main():
    if len(sys.argv) < 2:
        print("用法: python intent-router.py \"今天卖得咋样\"")
        sys.exit(1)
    msg = " ".join(sys.argv[1:])
    print(f"输入: {msg}")
    result = route_intent(msg)
    print(f"\n识别结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
