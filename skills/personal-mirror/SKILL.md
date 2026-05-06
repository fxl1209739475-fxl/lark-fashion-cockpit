---
name: lark-fashion-cockpit-personal-mirror
version: 1.0.0
description: "个人 AI 镜子 Skill — 每晚 22:00 自动拉员工今日全部飞书留痕（聊天/妙记/任务/审批/文档操作），AI 分析 4 维度（今日做了什么/做得好/待改进/待办），检测反复模式（同需求被表达 3+ 次/同问题循环出现/同事反复找配合）触发"该沉淀成 SOP"建议，自动写入员工个人飞书文档 + 个人知识库（不是公司 wiki，是员工自己的库），每日自动迭代结构。当用户说「每日复盘」「我今天都干啥了」「该沉淀什么 SOP」「我的成长档案」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 个人 AI 镜子 — 每日复盘 + 自动 SOP 沉淀

> **🎯 老板娘的洞察：** 公司里**最大的低效**不是事没做，而是"同一件事反复做、踩同一个坑、教新人同一遍"。员工自己很难意识到"这事我应该沉淀"。

> **核心创新：** 每晚 AI 自动**镜像**员工今日所有飞书行为，找出该沉淀的、该改进的、该升级成 SKILL 的，**送到他个人**（不发群、不发老板），让员工自己的能力**被动复利成长**。

---

## 一、为什么需要这个 skill

| 现状 | 用 personal-mirror 之后 |
|---|---|
| 员工"今天都干啥了"自己说不清 | 自动列出今日所有飞书留痕 + AI 总结 |
| 同一个问题客户问了 5 遍每次手打 | 第 3 次时机器人提示"这该沉淀成 SOP" |
| 教新人时口头说，新人 1 个月后又问 | 工作中自动沉淀文档 |
| 公司 wiki 沉淀慢（要主动写）| 员工每晚被动收到自己的"成长档案"自动更新 |
| 老板给员工反馈靠会议靠记忆 | 员工自己的复盘比老板还细 |

**触发模式（最炸点）**：
- 同一需求被员工表达 3+ 次给不同同事 → 提示"客户/同事都问 → 写成 SOP 群发即可省 1h"
- 同一问题反复出现（如"DRS-XXX 退货咋办"问 5 次）→ 提示"建词典 / 写流程"
- 同事反复来配合（如设计师收到工厂 3 次"色差"反馈）→ 提示"你的设计稿色卡需要升级"

---

## 二、数据源（员工今日所有飞书留痕）

| 数据 | API | 字段 |
|---|---|---|
| **今日聊天** | `im messages list` 按时间过滤 | sender / 群名 / 关键词 |
| **今日妙记**（参加的会议）| `vc +notes` 拉摘要 | 会议主题 / AI 摘要 / 待办 |
| **今日任务**（创建/完成）| `task +get-my-tasks` | 任务标题 / 状态变化 |
| **今日审批** | `approval` API | 我发起的 / 我审批的 |
| **今日文档/base 操作** | `docs` / `base history` | 编辑了哪些文档 / 改了哪些表 |
| **今日日历** | `calendar +agenda` | 参加了哪些会议 |

---

## 三、前置条件

```bash
# 1. 装依赖
pip install httpx openai

# 2. 飞书认证（员工自己授权一次）
lark-cli auth login --scope "im:message:read vc:meeting:read task:task minutes:minutes:readonly bitable:app:readonly docs:document:readonly"

# 3. 配置员工个人知识库 space_id（每人一个）
# 跑一次 init-personal-knowledge.py 自动建：
#   - 个人 wiki 空间「我的成长档案 - <name>」
#   - 个人 SOP 库（base 表「我的 SOP 库」)
```

---

## 四、工作流（每晚 22:00 cron）

```
00:00 ─ 22:00 cron 触发 personal-mirror.py（每位注册员工各跑一次）
  ↓
[1] 拉员工今天 0:00-22:00 飞书全留痕
[2] DeepSeek V4 Pro 分析 4 维度：
    a) 今日做了什么（10 条以内的关键事件流）
    b) 做得好的亮点（推断"为什么好"）
    c) 没做好的（推断"哪里可以优化"）
    d) 待办：
       - 短期（明天/本周）
       - 长期目标进度（关联 OKR 表）
[3] 反复模式检测（最关键）：
    - 关键词频次扫描（同一个 product_id / 客户名 / 问题关键词）
    - "重复请求"识别（同事 N 次找你同一类配合）
    - 阈值 ≥ 3 → 触发"应该沉淀"
[4] 生成"今日 SOP 候选"：
    - 标题（AI 起）
    - 触发原因（同事/问题/需求）
    - SOP 内容草稿（AI 写）
    - 工时估算（写完省多少时间）
[5] 写入员工个人资产：
    - 飞书文档「我的成长档案 - YYYY-MM-DD」（追加今日条目）
    - 飞书 wiki「我的 SOP 库」（候选 SOP 待员工 confirm）
    - 26_老板语料库 / 28_开源雷达 等表的"反向贡献"
[6] 22:00 私聊员工本人 — 个人成长卡片（不发群，不抄送老板）
```

---

## 五、典型成长卡片（22:00 私聊员工）

```
🪞 萍蔓姐 · 2026-05-05 个人成长复盘

📊 今日留痕：38 条 IM / 2 个会议 / 5 任务 / 3 文档编辑

✅ 今日做了什么（5 件事）
1. 09:00 完成 DRS-0429-FL 主图设计（提前 14 分钟）
2. 11:00 跟工厂申丽媛对接 KNT-0402 色卡（来回 8 条 IM）
3. 14:00 参加上新企划会（妙记 23 分钟摘要已读）
4. 16:00 帮内容编辑朱健豪改 3 张产品图
5. 19:30 提交 5 月第 2 周设计任务清单

🌟 做得好（亮点）
- DRS-0429 提前完成（团队平均 18:00 你 17:46 交）
- 跟工厂沟通主动提供色卡参考（之前需要别人催）

⚠️ 待改进
- KNT-0402 色卡反复对了 3 次（沟通成本高）→ 建议下次直接给工厂 Pantone 色号

📋 待办
**短期（明天）**
- [ ] 完成 DRS-0501-WT 草稿（已分配）
- [ ] 跟工厂二次确认 KNT-0402 实样

**长期（本季度目标进度）**
- 设计 50 款新品：当前 28/50 (56%)，进度正常
- 改稿率从 40% → 25%：当前 32%，趋势向好

═══════════════════════════════
🚨 SOP 沉淀建议（这是该写下来的事！）

这周你跟工厂对接「色卡确认」流程已经 5 次（萍蔓姐我数了你的 IM）
→ 建议沉淀「色卡确认 SOP」到你的个人知识库

我已经帮你起草了 SOP 草稿：
   "色卡确认 3 步法
    1. 设计稿先标 Pantone 色号
    2. 给工厂发标准色卡照片 + 灯光说明
    3. 工厂打样后双方都用 D65 标准光源比对
    （草稿已存「我的 SOP 库」），你点确认就生效"

[✅ 确认沉淀] [✏️ 编辑后沉淀] [❌ 不沉淀]
═══════════════════════════════

📚 你的个人成长档案
[查看完整复盘文档] [查看 SOP 库]
```

---

## 六、反复模式检测算法

```python
# scripts/pattern-detector.py

def detect_patterns(today_data, history_7d):
    """检测今日 + 近 7 天有没有"该沉淀"的反复模式"""
    triggers = []

    # 模式 1：同关键词请求 ≥ 3 次（不同同事 or 不同时间）
    keyword_freq = count_keywords_in_im(history_7d)
    for kw, freq in keyword_freq.items():
        if freq >= 3:
            triggers.append({
                "type": "重复请求",
                "keyword": kw,
                "count": freq,
                "suggestion": f"「{kw}」被问了 {freq} 次，建议写 SOP",
            })

    # 模式 2：同事反复来配合同类事
    helper_requests = group_by_requester_and_topic(history_7d)
    for (requester, topic), times in helper_requests.items():
        if times >= 3:
            triggers.append({
                "type": "反复配合",
                "from": requester,
                "topic": topic,
                "suggestion": f"{requester} {times} 次找你做{topic}，可考虑标准化",
            })

    # 模式 3：今日工作发现历史 SOP 已存在但没用上
    today_keywords = extract_keywords(today_data)
    for kw in today_keywords:
        if kw in personal_sop_index:
            triggers.append({
                "type": "未用 SOP 提醒",
                "keyword": kw,
                "suggestion": f"你 SOP 库有《{personal_sop_index[kw]}》关于「{kw}」，今天好像没用上",
            })

    return triggers
```

---

## 七、自动迭代员工个人知识库

每次新 SOP 加入员工自己的"我的 SOP 库"时，AI 自动：
1. **去重**：跟已有 SOP 比对，重复的合并 / 升级版本号
2. **重排**：按主题（沟通/设计/任务/工厂...）分组
3. **加索引**：生成「快速查找词典」让员工 hover 一个词就能找到对应 SOP
4. **失效提醒**：如果 SOP 6 个月没用上，提示"这条还需要吗"

---

## 八、隐私边界

- ✅ 个人成长档案 → 写**员工自己的**飞书文档（管理员看不到员工私密复盘）
- ✅ 私聊汇报 → 不发群、不抄送老板、不存到 cockpit 公共 base
- ✅ 反复模式检测 → 用员工自己的 IM 数据，不跨员工分析
- ⚠️ 老板娘想看员工成长档案 → 需要员工**主动分享文档权限**给老板娘

---

## 九、与其他 skill 联动

- [`morning-report`](../morning-report/SKILL.md) — 早 8:00 经营晨报（公司视角） + 22:00 个人镜子（个人视角）= 全天双重复盘
- [`task-lifecycle`](../task-lifecycle/SKILL.md) — 提取员工今日任务作为镜子数据源
- [`knowledge-base`](../knowledge-base/SKILL.md) — 个人 SOP 库是员工私域 wiki
- [`lingo-fashion-glossary`](../lingo-fashion-glossary/SKILL.md) — 反复出现的术语自动加词典

---

## 十、参考

- 主脚本：[`scripts/personal-mirror.py`](./scripts/personal-mirror.py)
- 反复模式检测：[`scripts/pattern-detector.py`](./scripts/pattern-detector.py)
- 个人知识库初始化：[`scripts/init-personal-knowledge.py`](./scripts/init-personal-knowledge.py)
- AI 提示词模板：[`references/ai-prompt-template.md`](./references/ai-prompt-template.md)
- SOP 触发规则：[`references/sop-trigger-rules.md`](./references/sop-trigger-rules.md)
- 卡片样例：[`examples/sample-daily-card.md`](./examples/sample-daily-card.md)
