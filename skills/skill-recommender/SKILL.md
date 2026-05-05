---
name: lark-fashion-cockpit-skill-recommender
version: 1.0.0
description: "skill 自演进推荐器 — 基于 trigger-log.jsonl 真实触发记录 + 飞书 IM 历史，AI 推荐老板娘下次该用哪个 skill。当用户说「我接下来该用什么 skill」「skill 推荐」「下一步建议」时使用，或在 cockpit 早 8:00 晨报后自动跑。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# Skill Recommender — cockpit 自演进推荐器

> **🎯 痛点：** 32 个 sub-skill 老板娘记不全。早上忙起来忘了今天该跑什么。

> **核心创新：** 不是"推荐用法手册"，而是**基于真实触发历史 + 当前业务状态**的个性化推荐。
>
> **数据源：**
> - `logs/trigger-log.jsonl`（event-listener 持久化的所有 IM 触发）
> - `25_未完成事项`（待办池）
> - `02_4平台销售` / `03_库存预警`（业务状态）
> - 飞书 IM 历史（最近聊天关键词）

## 一、工作流

### 场景 A：早 8:00 cron 自动推荐
```bash
python scripts/recommend.py --mode morning
# → 综合"今日数据 + 待办 + 历史触发频率" → 飞书发"今天建议跑这 3 个 skill" 卡片
```

### 场景 B：飞书群发"推荐"
```
老板娘 →「skill 推荐」/「下一步该做什么」
listener 路由 → recommend.py
→ 卡片回复 TOP 3 推荐
```

### 场景 C：跑完一个 skill 后自动追问
```
跑完 morning-report 卡片底部加按钮：「📊 接下来要 launch-decision 吗？」
点 → 触发对应 skill
```

## 二、推荐算法

```python
# scripts/recommend.py
def recommend(context):
    candidates = list_all_skills()  # 32 个

    for s in candidates:
        s.score = 0
        # 1. 触发频率（高频 = 老板娘常用，加分）
        s.score += freq_in_trigger_log(s, days=7) * 2

        # 2. 业务状态匹配（如库存预警 → 推 stock-replenishment）
        if has_stock_alert() and s.id == "stock-replenishment":
            s.score += 10

        # 3. 时间敏感（如直播日 → 推 livestream-recap）
        if today_has_livestream() and s.id == "live-streaming":
            s.score += 8

        # 4. 待办关联（25 表里有 P0/P1 任务相关 → 加分）
        s.score += related_pending_todo_count(s) * 3

        # 5. 上下文延续（刚跑完 X，常接 Y）
        last_skill = get_last_triggered()
        if (last_skill, s.id) in COMMON_PIPELINES:
            s.score += 5

    return sorted(candidates, key=lambda x: -x.score)[:3]
```

## 三、推荐 pipeline 模板（基于历史数据自学）

```python
COMMON_PIPELINES = {
    ("morning-report", "stock-replenishment"): 0.7,
    ("morning-report", "task-lifecycle"): 0.8,
    ("competitor-monitor", "video-script-parser"): 0.6,
    ("monitor-bloggers", "video-script-parser"): 0.85,  # 看完爆款常拆脚本
    ("livestream-daily-report", "task-collaboration"): 0.5,
    ("launch-decision", "approval-flow"): 0.9,  # 决策完起审批
    # ... 这些权重 = (X 后跑 Y 的次数 / X 跑过的总次数)，自动从 trigger-log 学
}
```

## 四、典型卡片输出

```
📊 老板娘 cockpit 今日 skill 推荐 - 2026-05-05 08:00

[1] 🔥 stock-replenishment
   理由：DRS-0429-FL 库存仅 12 件（03 表），昨日卖出 35 件，3 天断货
   一键跑 → [按钮]

[2] 📺 livestream-daily-report
   理由：昨晚 21:00-23:00 直播刚结束，主播未提交复盘
   一键跑 → [按钮]

[3] 👑 boss-clone-aily
   理由：14_审批表有 2 件待批 P0 任务超 24h
   一键问 → [按钮]
```

## 五、与其他 skill 联动

- `morning-report` 跑完后调用 recommend.py 决定下一步
- `event-router` 路由表里加「推荐」关键词
- `task-lifecycle` 巡检逾期任务时一并推荐解决 skill

## 六、自演进机制

每次老板娘真实触发了一个 skill → recommend.py 把这条记录写进 `logs/trigger-log.jsonl`：
```json
{"ts": "2026-05-05T08:30:00", "skill": "morning-report", "source": "im_message"}
```

每周一 cron 跑 `scripts/learn-pipelines.py` 重算 COMMON_PIPELINES 权重 — **越用越准**。

## 七、参考

- 数据源：`logs/trigger-log.jsonl`（event-listener.py 已持久化）
- 调用脚本：`scripts/recommend.py`
- 学习脚本：`scripts/learn-pipelines.py`（赛后做）
