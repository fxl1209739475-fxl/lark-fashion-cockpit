---
name: lark-fashion-cockpit-content-pipeline
version: 1.0.0
description: "内容创作 5 阶段流转 — 选题→脚本→拍摄→剪辑→已发布。当用户说「看下选题池」「生成 X 款的文案」「这条选题进入拍摄」「内容产能漏斗」「拉一波竞品爆款」时使用。整合 douyin-monitor Python CLI 抓取爆款博主视频，AI 评分推荐二创（穿搭类只推荐二创、讲解类生成文案）。属于 lark-fashion-cockpit 销售增长板块。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
  cliHelp: "lark-cli base --help"
---

# 内容创作 5 阶段流转

> **🎯 这是 lark-fashion-cockpit 串联 douyin-monitor 的核心能力。** 整合 douyin-monitor Python CLI 抓爆款博主 → AI 评分 → 高分进选题池 → 5 阶段流转（选题/脚本/拍摄/剪辑/已发布）→ 文案库（仅讲解类）。

> **板块：** 🅲 销售增长  
> **调用 lark-cli skill：** `base` + `doc` + `task` + `im`  
> **外部 CLI：** `douyin-monitor`（用户已有的 Python 项目）  
> **多维表依赖：** `15_市场内容监控` / `06_选题池` / `07_文案库` / `01_产品库` / `12_竞品博主库`

---

## 一、前置条件

读 [`../../lark-shared/SKILL.md`](../../../lark-shared/SKILL.md)。如果用户没有 douyin-monitor，跳过工作流 A 的采集步骤。

### scope

```bash
lark-cli auth login --scope "base:record:read base:record:create base:record:update docs:document:write_only task:task:write im:message:write"
```

### 外部依赖

- ✅ douyin-monitor（用户的 Python 项目）路径已在 `lib/external/douyin-monitor.config.json` 配置
- ✅ DeepSeek / 其他 LLM API key 已配置（用于 AI 评分 + 文案生成）

---

## 二、5 阶段流转（核心模型）

```
[市场监控]      [选题池]                                              [文案库]
   ↓             ↓                                                      ↑
博主视频       待启动 → 脚本 → 拍摄 → 剪辑 → 已发布            （仅讲解类）
   ↓             ↓        ↓       ↓        ↓         ↓
AI 评分        飞书 base 多视图看板 / 任务清单中跟进
   ↓             ↓
推荐二创      二创类型分流：
            - 穿搭类 → 仅二创（不进文案库）
            - 讲解类 → 生成文案 → 文案库
```

---

## 三、5 大工作流

### 工作流 A：🔍 市场内容监控（从博主+热榜抓视频）

**触发语：** "拉一波竞品爆款" / "更新今天的市场监控" / "看下今日抖音热榜"

#### Step 1: 调 douyin-monitor 抓取

```bash
# 进 douyin-monitor 项目目录跑采集
cd ~/douyin-monitor
python main.py --bloggers @./config/fashion-bloggers.json --output /tmp/today-videos.json

# 或者只抓今日热榜
python scripts/hot_search.py --output /tmp/today-hot.json
```

输出 JSON 格式（每条视频含 标题/博主/平台/发布时间/播放/点赞/评论/转发/链接）。

#### Step 2: AI 评分 + 视频类型分类

调 DeepSeek 给每条视频打分（0-10）+ 判断类型：

```python
# 提示词（在 douyin-monitor 内已实现，cockpit 复用）
prompt = """
分析下面这条短视频的元数据，给出：
1. AI 推荐分数（0-10）：综合考虑互动率、相关性、二创可行性
2. 视频类型：穿搭 / 讲解 / 测评 / 生活 / 其他
3. 推荐操作：
   - 穿搭类高分 → "仅二创"
   - 讲解类高分 → "二创+文案"
   - 低分 → "不推荐"

视频数据：{video_json}
"""
```

#### Step 3: 写入 15_市场内容监控

```bash
# 用 base +record-batch-create 批量插入
lark-cli base +record-batch-create \
  --base-token <APP> \
  --table-id tblW888G2M8KMgZk \
  --json @/tmp/today-videos-with-score.json
```

JSON 格式（参考 `lib/mock-data/15-market-content.json` 待建）：

```json
{
  "fields": ["视频标题","来源","博主名","平台","发布时间","播放量","点赞","评论","AI分数","视频类型","推荐操作","状态"],
  "rows": [
    ["法式连衣裙夏日穿搭...", "博主视频", "@时尚博主A", "抖音", 1751299200000, 285000, 12500, 320, 8.5, "穿搭", "仅二创", "待处理"]
  ]
}
```

---

### 工作流 B：📥 监控视频 → 选题池（高分晋级）

**触发语：** "把这条进入选题池" / "高分推荐自动晋级"

#### Step 1: 筛选高分待处理

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblW888G2M8KMgZk \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"AI分数","operator":"isGreaterEqual","value":7.5},
    {"field_name":"状态","operator":"is","value":"待处理"}
  ]}'
```

#### Step 2: 写入 06_选题池

```bash
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblTlCI2hQ7o1kr8 \
  --json @./topics-from-monitor.json
```

#### Step 3: 回写 15 表状态 = "已加入选题池"

```bash
lark-cli base +record-batch-update \
  --base-token <APP> --table-id tblW888G2M8KMgZk \
  --json @./mark-as-promoted.json
```

---

### 工作流 C：✍️ 选题 → 文案（仅讲解类）⭐

**触发语：** "给 X 选题生成文案" / "讲解类批量出文案"

**核心规则：穿搭类不生成文案（直接拍即可），讲解类需要文案脚本。**

#### Step 1: 筛选讲解类选题

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblTlCI2hQ7o1kr8 \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"视频类型","operator":"is","value":"讲解"},
    {"field_name":"阶段","operator":"is","value":"待启动"}
  ]}'
```

#### Step 2: AI 生成 4 平台文案

提示词模板（在 `lib/prompts/content-script.md` 待建）：

```
根据这个讲解类选题，生成 4 个平台版本的文案：

选题：{选题标题}
关联款：{产品名 + 卖点}

请输出：
1. 抖音版（150-200字，钩子+痛点+产品+CTA，口语化）
2. 小红书版（300-400字，标题党+痛点+体验+种草，含emoji）
3. 视频号版（200字，温和叙事+使用场景）
4. 淘宝版（图文详情，强卖点+材质+使用场景）

每个版本独立成段。
```

#### Step 3: 写入 07_文案库

```bash
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblBAJCOKKnMgUrQ \
  --json @./scripts.json
```

每个选题 → 4 条文案记录（每个平台一条）。

---

### 工作流 D：🔄 5 阶段流转

**触发语：** "把 X 选题推进到拍摄" / "已发布 X 选题"

```bash
# 流转一个选题（更新阶段字段）
lark-cli base +record-update \
  --base-token <APP> --table-id tblTlCI2hQ7o1kr8 \
  --record-id <topic_record_id> \
  --json '{"阶段":"拍摄"}'
```

并自动建对应任务（链 task-collaboration skill）：

```bash
# 进入"拍摄"阶段时自动建任务给摄影师 + 主播
lark-cli task +create --summary "拍摄: <选题>" --assign-role "摄影师"
```

---

### 工作流 E：📊 内容产能漏斗（管理视图）

**触发语：** "看下内容漏斗" / "本月产能"

直接打开 06_选题池 的看板视图（按"阶段"分列），或：

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tblTlCI2hQ7o1kr8 \
  --json '{
    "table_name":"06_选题池",
    "count_all":true,
    "group_by":[{"field_name":"阶段","mode":"integrated"}]
  }'
```

输出（待启动 12 / 脚本 5 / 拍摄 3 / 剪辑 2 / 已发布 8）→ AI 总结 → 飞书文档。

---

## 四、涉及多维表（数据流向）

```
[douyin-monitor Python CLI]
        ↓
[15_市场内容监控] ──→ 筛选高分 ──→ [06_选题池]
                                      ↓
                              讲解类才进 [07_文案库]
                                      ↓
                              所有进入 [05_任务清单]（拍摄/剪辑任务）
                                      ↓
                              关联到 [01_产品库]（被推产品）
```

---

## 五、典型对话示例

### 例 1：完整流程

```
用户：拉一波今天的市场监控

agent：
✓ 调用 douyin-monitor 抓 12 个博主的最新视频
✓ 共抓到 47 条
✓ AI 评分 + 类型分类完成
✓ 写入 15_市场内容监控（47 条）
  - 穿搭类 28 条 / 讲解类 12 条 / 其他 7 条
  - 高分(≥7.5) 11 条
✓ 自动晋级到选题池（11 条）

📋 高分选题池：https://my.feishu.cn/base/<APP>?table=06_选题池
推荐操作：
- 穿搭类 8 条 → 直接进拍摄（不需文案）
- 讲解类 3 条 → 已自动生成 4 平台文案 → https://...

是否要给摄影师/内容编辑批量分发任务？
```

### 例 2：定时晨报

每天 08:00 自动跑（用 lark-event 长连接 + cron skill）：

```
🌅 今日内容监控简报
- 新增视频 47 条
- 高分晋级 11 条（穿搭 8 / 讲解 3）
- 文案已就绪 12 篇
- 待审 3 篇 [@小李 请审核]
```

---

## 六、与其他 skill 协作

- `competitor-monitor`：补充竞品博主到 12_竞品博主库
- `task-collaboration`：把每个选题的拍摄任务批量下发给团队
- `live-streaming`：高分款进入直播主推

---

## 七、参考

- [`../../../lark-base/SKILL.md`](../../../lark-base/SKILL.md) — 多维表
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md) — 流转到拍摄任务
- [`../product-library/SKILL.md`](../product-library/SKILL.md) — 关联产品分析
- 用户的 douyin-monitor 项目（`profile/project_context.md`）— 抓取实现细节
