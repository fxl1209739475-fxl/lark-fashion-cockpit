---
name: lark-fashion-cockpit-video-script-parser
version: 1.0.0
description: "短视频脚本拆解 Skill — 输入抖音/快手/TikTok/B 站视频 URL，自动下载视频、ffmpeg 抽帧、豆包多模态分析，按 6 维结构输出完整脚本（基础要求/场景设定/分镜按秒/声音设计/文字设计/可调参数）。当用户说「拆解视频」「分析视频脚本」「这视频怎么拍的」「拆这个视频 [URL]」时使用。基于 yt-dlp + f2 + ffmpeg + 豆包视觉理解 + 飞书多维表格。"
metadata:
  requires:
    bins: ["lark-cli", "python", "yt-dlp", "ffmpeg"]
---

# 视频脚本拆解 — 不看视频也能拿到完整脚本

> **🎯 痛点：** 想学竞品爆款视频结构（分镜/旁白/情绪），但一条条看完几十条爆款要 4 小时。

> **核心能力：** 输入 URL → 30-60 秒输出完整结构化脚本（含分镜按秒 + 旁白 + 文字 OCR + 情绪标签）

---

## 一、为什么这个 skill 价值高

| 场景 | 传统方式 | 用这个 skill |
|---|---|---|
| 学一条爆款视频结构 | 反复看 5-10 遍记笔记，30 分钟 | **30-60 秒拿到完整 markdown 脚本** |
| 复盘一周 50 条对标博主 | 不可能（要 25 小时）| 1 小时跑完所有，写到飞书表 |
| 给设计师讲清楚怎么拍 | 口头描述 / 截图 | 把脚本 markdown 直接发给她 |
| 团队复盘会议 | 每个人主观印象 | 客观的分镜表 + 文字 OCR |

---

## 二、前置条件

```bash
# 1. 装依赖
npm install -g @larksuite/cli
pip install yt-dlp openai
# ffmpeg 单独装：https://ffmpeg.org/

# 2. 配置环境变量
export DOUBAO_API_KEY="ark-xxxxxxxxxxxxxxxxxx"  # 火山方舟 API Key
export DOUBAO_MODEL="doubao-1-5-vision-pro-32k-250115"

# 3. 抖音视频还需要 cookie（从你登录的抖音 web 版 F12 复制）
export DOUYIN_COOKIE="..."

# 4. 飞书 base 认证
lark-cli auth login --scope "bitable:app:readwrite"
```

豆包视觉模型在 [火山方舟](https://console.volcengine.com/ark) 注册即开通，**新用户免费 50 万 tokens**（够跑 80+ 条视频）。

---

## 三、单条视频拆解

```bash
python scripts/parse-video-script.py --url "https://v.douyin.com/xxx"
# 或
python scripts/parse-video-script.py --url "https://www.tiktok.com/@xxx/video/123"
# 或写回飞书 27 表
python scripts/parse-video-script.py --url "..." --record-id recXXX
```

**输出**（自动保存到 `out/video-analysis/<hash>/script.md`）：

```markdown
## 一、基础要求
- 平台：抖音
- 比例：9:16 竖屏
- 风格：真实手持拍摄

## 二、场景设定
- 场景类型：服装店门店
- 地面：浅色瓷砖
- 光源：顶部灯光
- 背景：服装展示架，挂着各种款式

## 三、分镜结构
| 时间区间 | 镜头动作 | 画面内容 |
| 0-1s | 固定 | 男子穿黑色西装，左手伸出掌心朝镜头 |
| 1-2s | 固定 | 男子右手竖起大拇指，左手叉腰 |
| ...

## 四、声音设计
- BGM：欧美流行节奏明快
- 旁白：年轻女声，调皮种草
- 旁白台词：「干服装的姐姐辛苦了，风吹雨打自己扛...」
- 环境音：未明显呈现

## 五、文字设计
- 位置：画面中央
- 字体：白色无衬线
- 文字：「干服装的姐姐」「赚钱养家样样强」「全品类女装批发」

## 六、可调参数
- 镜头：第三人称
- 抖动：轻微
- 情绪：亲切、热情、种草
```

---

## 四、与飞书 base 联动（写回单元格）

```bash
# 先在 base 加一个「视频拆解」字段（text 类型）
lark-cli base +field-create \
  --base-token $LARK_FASHION_COCKPIT_BASE_TOKEN \
  --table-id $TABLE_BLOGGER_VIDEOS \
  --json '{"name":"视频拆解","type":"text"}'

# 拆解后写回单元格
python scripts/parse-video-script.py \
  --url "..." \
  --record-id <record_id>
```

---

## 五、批量拆解（联动 blogger-monitor）

```bash
# 把昨天监控发现的 TOP 5 爆款全部拆解
python scripts/parse-video-script.py --batch-from-table \
  --base-token $LARK_FASHION_COCKPIT_BASE_TOKEN \
  --table-id $TABLE_BLOGGER_VIDEOS \
  --filter "状态=已选中"
```

---

## 六、技术细节

| 步骤 | 工具 | 时间 |
|---|---|---|
| URL 解析 + 视频下载 | yt-dlp（TikTok）/ f2（抖音 cookie 模式）| 5-10s |
| 抽帧（每秒 1 张）| ffmpeg | 2-5s |
| 多模态分析 | 豆包 Doubao-1.5-vision-pro | 20-40s |
| 写回飞书 base | lark-cli base +record-upsert | 1s |
| **合计** | | **~30-60s/视频** |

**成本：** 一条 30 秒视频约 ¥0.024（用豆包 V4 视觉），50 万免费 tokens 够跑 80+ 条。

---

## 七、与其他 skill 协作

- [`blogger-monitor`](../blogger-monitor/SKILL.md) — 监控发现爆款 → 自动调本 skill 拆解
- [`content-pipeline`](../content-pipeline/SKILL.md) — 拆解结果作为二创素材
- [`event-router`](../event-router/SKILL.md) — 飞书群发「拆 [URL]」自动触发

---

## 八、典型对话示例

```
老板娘 → 飞书群「拆 https://v.douyin.com/xxx」
event-listener → video-script-parser 触发
[reaction +EYES] msg=om_xxx
[1/4] f2 拿 CDN 直链 ...
[2/4] ffmpeg 抽帧 → 9 帧
[3/4] 豆包多模态分析 9 帧 ...
[4/4] 写回 27 表 record_id=recXXX 视频拆解 字段 ...
[reaction +DONE]
飞书卡片：🎬 拆解完成 + 27 表链接
```

---

## 九、参考

- 主脚本：[`scripts/parse-video-script.py`](./scripts/parse-video-script.py)
- 完整示例：[`examples/sample-output.md`](./examples/sample-output.md)
- 提示词设计：[`references/prompt-design.md`](./references/prompt-design.md)
