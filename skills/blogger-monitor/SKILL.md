---
name: lark-fashion-cockpit-blogger-monitor
version: 2.0.0
description: "对标博主每日监控 + 视频脚本一键拆解 — 监控竞品博主（抖音/快手/视频号）最新视频，AI 评分爆款指数；选中爆款一键拆脚本（yt-dlp + faster-whisper + DOUBAO 多模态 5 维度：镜头/台词/视觉/声音/节奏）。当用户说「监控博主」「看竞品博主」「同行发了啥」「拆这条视频」「二创脚本」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python", "yt-dlp", "ffmpeg"]
    pip: ["openai", "faster-whisper"]
---

# 对标博主监控 + 视频拆解一站式

> **🎯 痛点：** 老板娘每天花 2 小时刷竞品博主，看完没数据沉淀也不知道哪条值得学；想二创还要切工具拉视频 + 拆脚本，工作流断裂。

> **核心能力：**
> 1. 监控 N 个博主 → 算法评分 → 飞书卡片汇报 TOP 3
> 2. **同 skill 内一键拆脚本** —— 选中爆款 → yt-dlp 拉视频 → faster-whisper 转录 → DOUBAO 多模态拆解 5 维度（镜头 / 台词 / 视觉 / 声音 / 节奏）→ 输出可执行二创 md

## 二、视频拆解能力（合并自原 video-script-parser）

`scripts/parse-video-script.py` 主脚本：

```bash
# 单条拆解
python scripts/parse-video-script.py --url "https://www.douyin.com/video/xxx"

# 不写飞书 wiki 只本地存
python scripts/parse-video-script.py --url "..." --no-wiki
```

输出 5 维度结构化拆解：
- 一、镜头脚本（按秒粒度）
- 二、文案台词（含转场点）
- 三、视觉设计（构图 / 配色 / 道具）
- 四、声音设计（旁白节奏 / BGM 选型）
- 五、节奏分析（高潮点位置）

依赖外部能力：
- `yt-dlp` 拉抖音 / 快手 / 视频号视频
- `faster-whisper` 本地 ASR（备选：DOUBAO ASR API，HF 网络受阻时用）
- `DOUBAO doubao-1-5-vision-pro-32k-250115` 多模态视觉拆帧
- 防盗链：requests Referer + Cookie header 解决 CDN 403

## 三、典型工作流（监控 → 拆解一气呵成）

```
每天 9:00 自动跑 monitor-bloggers.py
  ↓
飞书卡片"今日 Top 3 爆款"
  ↓
老板娘点其中一条的【拆脚本】按钮
  ↓
parse-video-script.py 自动跑
  ↓
30 秒后飞书 wiki 收到完整拆解 md
  ↓
朱健豪基于 md 二创新视频
```

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

- 视频拆解能力已合并入本 skill（见上方"二、视频拆解能力"），同 skill 内一键调 `parse-video-script.py`
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
