---
name: lark-fashion-cockpit-blogger-monitor
version: 1.0.0
description: "对标博主每日监控 Skill — 监控指定竞品博主清单（抖音/快手/视频号）的最新视频，按 5 项算法（赞粉比/收藏率/分享率/评赞比/AI 评分）给爆款指数 0-10 分，4 路筛选出值得二创的 TOP N，发飞书工作汇报卡片。当用户说「监控博主」「看竞品博主」「同行最近发了啥」「TOP N 爆款」「博主每日汇报」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 对标博主每日监控 — 不刷抖音也能掌握同行动态

> **🎯 痛点：** 老板娘每天花 2 小时刷竞品博主，看完没数据沉淀也不知道哪条值得学。

> **核心能力：** 监控 N 个博主 → 算法筛选 → 飞书卡片汇报 TOP 3，附数据指标 + 文案前 120 字 + 看视频按钮

---

## 一、5 项算法 + 4 路筛选（复刻 douyin-monitor AI 博主监控）

### 算法（爆款指数 0-10）
| 指标 | 公式 | 阈值 |
|---|---|---|
| 赞粉比 | likes / fans | ≥0.5 → 5 分 / ≥0.2 → 3 分 / ≥0.05 → 1 分 |
| 分享率 | shares / likes | ≥0.1 → 2 分 / ≥0.03 → 1 分 |
| 收藏率 | collects / likes | ≥0.1 → 2 分 / ≥0.05 → 1 分 |
| 评赞比 | comments / likes | ≥0.05 → 1 分 |

### 4 路筛选（任一满足 → 已选中）
1. AI 评分 ≥ 7（豆包/DeepSeek 主观打分）
2. 收藏率 ≥ 10%（高保留价值）
3. 评赞比 ≥ 8%（讨论度高）
4. 赞粉比 ≥ 40%（爆款潜力）

不满足 → 待评估（不浪费老板娘时间看）

---

## 二、前置条件

```bash
pip install httpx openai
lark-cli auth login --scope "bitable:app:readwrite im:message:send"

# 配凭证
export LARK_FASHION_COCKPIT_BASE_TOKEN="..."
export TABLE_BLOGGER_VIDEOS="tblxxxxxxxx"  # 27 表
export DEEPSEEK_API_KEY="..."
export DOUYIN_COOKIE="..."  # 抖音爬数据用
```

---

## 三、初始化（建表 + 灌 mock 数据）

```bash
python scripts/seed-mock-bloggers.py
# → 在飞书 27 表灌入 10 条 mock 女装博主数据（含真实风格的口播文案）
```

19 个字段：博主名 / 粉丝 / 视频标题 / 发布日期 / 视频链接 / 点赞 / 评论 / 收藏 / 分享 / 赞粉比 / 互动率 / 分享率 / 收藏率 / 评赞比 / 爆款指数 / AI 评分 / 推荐角度 / 口播文案 / 状态

---

## 四、运行监控

```bash
# 完整流程：抓数据 → 算分 → 写表 → 发卡片
python scripts/monitor-bloggers.py

# 自定义参数
python scripts/monitor-bloggers.py --top 5 --reply-chat-id oc_xxx
```

---

## 五、典型汇报卡片

```
👀 对标博主每日监控

📊 监控博主：10 位 ｜ 今日抓取视频：10 条
🎯 已选中（值得二创）：3 条 ｜ 待评估：7 条

🔥 爆款指数 TOP 3（按算法排序）

[1] 程程姐_穿搭教学 · 粉丝 85.0w · 🎤 有口播
📝 150 显高显瘦秘籍 ｜ 衬衫塞进高腰裤的 3 种正确方式
👍 42.5w  💬 8.5k  ⭐ 5.6w  🔄 1.2w
赞粉比 50.00%  收藏率 13.18%  爆款指数 9/10
💡 推荐角度：教学型痛点解决
口播文案（前 120 字）：嗨大家好我是程程姐。今天教你们三招衬衫塞进高腰裤的正确方式...
[▶ 看视频]

[2] Sandy小苹果 · ...
[3] 大码姑娘子涵 · ...

[📋 查看完整 27 表]
```

---

## 六、与其他 skill 协作

- [`video-script-parser`](../video-script-parser/SKILL.md) — 老板娘看完 TOP 3 选 1 个发「拆 NO.001」自动拆解视频脚本到 27 表「视频拆解」字段
- [`content-pipeline`](../content-pipeline/SKILL.md) — 选中的视频作为二创素材源
- [`competitor-monitor`](../competitor-monitor/SKILL.md) — 趋势分析联动

---

## 七、cron 定时跑（推荐）

```bash
# 早 8:30 自动跑（搭配 morning-report 9:00）
crontab -e
30 8 * * * cd /path/to/lark-fashion-cockpit && python skills/blogger-monitor/scripts/monitor-bloggers.py
```

---

## 八、参考

- 监控主脚本：[`scripts/monitor-bloggers.py`](./scripts/monitor-bloggers.py)
- mock 数据脚本：[`scripts/seed-mock-bloggers.py`](./scripts/seed-mock-bloggers.py)
- 卡片样式 sample：[`examples/sample-card.md`](./examples/sample-card.md)
