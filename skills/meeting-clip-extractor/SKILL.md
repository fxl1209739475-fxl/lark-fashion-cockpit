---
name: lark-fashion-cockpit-meeting-clip-extractor
version: 1.0.0
description: "妙记自动剪辑高光片段 — 给 minute_token + 主题 + 时长，30 秒出片含字幕。当用户说「剪个高光视频」「会议金句剪辑」「剪个 20 秒片段」「自动加字幕」时使用。属于 lark-fashion-cockpit 公司管理板块（第 32 个能力）。"
metadata:
  requires:
    bins: ["lark-cli", "ffmpeg", "python"]
  cliHelp: "lark-cli minutes +download --help"
---

# 妙记自动剪辑 — 30 秒出片含字幕

> **🎯 用户洞察：** "我有妙记会议记录和文字稿，能自动剪个 2 分钟高光片段吗？"

> **🚀 解决：** 主题关键词 → AI 选最佳章节 → 找金句段 → 自动生成 SRT → ffmpeg 烧字幕 → mp4 出片。**30 个对手作品里没人做了「会议高光自动剪辑」。**

> **板块：** 🅴 公司管理（第 32 个能力）  
> **数据源：** lark-cli minutes / vc / docs（已接通）  
> **输出：** 飞书云盘 / IM 卡片附 mp4 链接

---

## 一、为什么需要这个 skill

| 场景 | 旧方案 | 新方案 |
|---|---|---|
| 演示视频 | 人工手剪 1 小时 | 30 秒自动出片 |
| 会议金句剪辑 | 翻 transcript 找段 | 主题关键词自动定位 |
| 字幕加工 | 剪映/Pr 手动打字 | transcript 自动转 SRT |
| 多场景版本 | 重新剪 | 同会议出 N 主题版本 |

---

## 二、7 步全自动工作流

```
1. lark-cli vc +notes              拉妙记 AI 摘要 + 章节列表
2. 主题关键词匹配                   遍历 20 章节，title+summary 含关键词得高分 → 选最佳章节
3. lark-cli minutes +download      下载妙记原音频（首次）
4. 解析 transcript.txt              提取"说话人 时间戳 内容"段（526 段）
5. 章节内找金句                     在最佳章节范围内，按主题关键词评分 → 定位金句起点
6. 自动生成 SRT                     transcript 段时间戳相对化 → SRT 字幕
7. ffmpeg 一站式合成                剪音频 + 烧字幕 + 静态背景 → mp4
```

---

## 三、关键技术点

### A. 字幕烧录（ffmpeg subtitles 滤镜）

```bash
ffmpeg -loop 1 -i bg.png -ss 00:05:43 -t 20 -i src.m4a \
  -vf "subtitles=sub.srt:force_style='FontName=Microsoft YaHei,FontSize=42,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,BorderStyle=1,Outline=3,Alignment=2,MarginV=80'" \
  -c:v libx264 -tune stillimage -c:a aac -shortest out.mp4
```

- **硬字幕**（直接画到画面，永久保留 — 发飞书/微信/抖音都不丢）
- 微软雅黑 + 黑色描边 3px → 任何背景都看得清

### B. SRT 自动生成（时间戳相对化）

```
绝对时间（妙记 transcript）：
  女帝 00:05:43.300  其实信息如果完全的情况下...

相对时间（剪辑后 SRT）：
  00:00:00,000 --> 00:00:06,000
  其实信息如果完全的情况下，人做判断是挺简单的一件事情
```

公式：`relative_time = absolute_time - clip_start_time`

### C. 章节智能选择（关键词加权）

```
score = title_match * 3 + summary_match * 2
返回最高分章节
```

如主题 "信息 沟通 卡点" → 自动选中章节"内部信息同步问题及处理难度探讨"

---

## 四、运行方式

```powershell
# 单次出片
PowerShell -File scripts/meeting-clip-extractor.ps1 \
  -MinuteToken obcnb31y6p4jd3u9t63h91gf \
  -Theme "上传下达" \
  -Duration 20

# 批量出片（多主题，演示视频常用）
foreach($theme in "信息卡点", "AI 决策", "数据沟通"){
  PowerShell -File scripts/meeting-clip-extractor.ps1 -MinuteToken xxx -Theme $theme -Duration 20
}

# 集成 event-listener 触发（老板娘飞书一句话出片）
# 老板娘: "剪 4/29 会议 信息卡点 主题 20 秒"
# event-listener 路由到本 skill
```

---

## 五、实测演示（5/4 真跑通）

| 主题 | 自动选章节 | 起点 | 时长 | 输出 |
|---|---|---|---|---|
| "上传下达" | 04:45 - 18:02 章节（默认） | 5:43 | 20s | highlights-20s.mp4 (0.67MB) |
| "AI 决策" | 21:09-33:36「品牌爆款规律探寻及AI在下单决策中的应用」 | 29:57 | 25s | clip-AI决策-25s.mp4 (0.93MB) |
| "信息 沟通 卡点" | 00:00-01:22「内部信息同步问题及处理难度探讨」 | 0:05 | 30s | clip-20260504-160602.mp4 (1.05MB) |

3 个主题 → 3 个不同章节 → 3 个独立视频 → 全自动。

---

## 六、和 meeting-broadcaster 的差别（4 件套完整闭环）

```
1. task-lifecycle         妙记 → 派任务            （文字结果）
2. meeting-broadcaster      妙记 → 个性化简报        （文字+定制）
3. meeting-clip-extractor   妙记 → 高光视频          （视觉素材）⭐ 本能力
```

**4 件套覆盖从会议结束到产出落地的全链路。**

---

## 七、为什么是杀手级创新

| 维度 | 评估 |
|---|---|
| **创新性** | ⭐⭐⭐⭐⭐ 30 对手没人做"会议高光自动剪辑" |
| **通用性** | ⭐⭐⭐⭐⭐ 所有有妙记的会议都能剪（教育/医疗/制造业等）|
| **商业价值** | ⭐⭐⭐⭐⭐ 替代专业剪辑师，每条片子节省 1 小时人工 |
| **工程深度** | ⭐⭐⭐⭐ 240 行 PowerShell + lark-cli 4 命令 + ffmpeg + PIL 编排 |

---

## 八、参考

- 飞书 CLI 工具：lark-cli minutes/vc/docs 链路
- 剪辑工具：ffmpeg subtitles 滤镜
- 字幕格式：SRT（行业标准）
- 字体：Microsoft YaHei（中文清晰描边）
- 演示文件：`assets/clips/highlights-20s.mp4`（首版手写字幕）/ `clip-20260504-160602.mp4`（自动 SRT 版）
