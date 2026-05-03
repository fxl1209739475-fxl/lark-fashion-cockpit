---
name: lark-fashion-cockpit-product-library
version: 1.0.0
description: "产品库 + 8 维详情 + AI 产品分析 + 产品关系图 — 当用户说「看 X 款产品」「分析卖得好的款」「找出售罄率<50%的春夏款」「画 X 款的关系图」「新增 X 款产品」「比较 SKU」时使用。包含 3 大杀手锏：AI 产品分析助手 / 产品关系图 / 8 维产品详情。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# 产品库 — 8 维详情 + AI 分析 + 关系图 ⭐

> **🔥 这是 lark-fashion-cockpit 含 3 大杀手锏的核心 skill：**
> - **杀手锏 1：AI 产品分析助手** — 自然语言问业务问题 → 读多维表 → 生成飞书文档
> - **杀手锏 2：产品关系图** — 自动画"产品×SKU×内容×投流×直播×素材×元素"全维度关系图
> - **杀手锏 3：8 维产品详情** — 一个产品多维度全景报告

> **板块：** 🅱 商品中心  
> **调用 lark-cli skill：** `base` + `whiteboard` + `doc` + `drive`  
> **多维表依赖：** `01_产品库`（核心）/ `02_4平台销售` / `05_任务清单` / `06_选题池` / `07_文案库` / `08_直播排期` / `11_退货反馈` / `16_竞品产品监控`

---

## 一、前置条件

读 [`../../lark-shared/SKILL.md`](../../../lark-shared/SKILL.md) + [`../../../lark-base/SKILL.md`](../../../lark-base/SKILL.md) + [`../../../lark-whiteboard/SKILL.md`](../../../lark-whiteboard/SKILL.md)。

### scope

```bash
lark-cli auth login --scope "base:record:read base:record:create base:record:update base:field:read docs:document:write_only docs:document.media:upload board:whiteboard:node:create drive:file:upload"
```

---

## 二、4 大工作流

### 工作流 A：📋 8 维产品详情报告

**触发语：** "看下 X 款产品" / "X 款的详情" / "X 款卖得怎么样"

#### 8 维结构

| # | 维度 | 数据源 |
|---|---|---|
| 1 | 经营数据 | `01_产品库`（库存/做货/已实销/售价）+ `02_4平台销售` |
| 2 | SKU 颜色尺码 | `01_产品库`（颜色/尺码 multi-select）|
| 3 | 关联内容 | `06_选题池` + `07_文案库` 中关联此款的记录 |
| 4 | 付费投流 | `02_4平台销售` 投流字段 / 自定义补充 |
| 5 | 直播讲解 | `08_直播排期` 中"主推款"等于此款的记录 |
| 6 | 素材详情 | `01_产品库.附件字段` + `lark-drive` 文件夹 |
| 7 | 元素标签 | AI 从产品名/描述提炼（颜色/风格/面料/场景）|
| 8 | 关系图 | 见 工作流 C |

#### 执行步骤

```bash
# Step 1: 拿主产品记录
lark-cli base +record-list \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --filter '{"conjunction":"and","conditions":[{"field_name":"款号","operator":"is","value":"DRS-0429-FL"}]}' \
  --jq '.data.records[0]'

# Step 2: 跨表拉关联数据（每张表分别查）
# 销售
lark-cli base +record-list --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --filter '{"conjunction":"and","conditions":[{"field_name":"关联款","operator":"contains","value":"<款record_id>"}]}'

# 选题
lark-cli base +record-list --base-token <APP> --table-id tblTlCI2hQ7o1kr8 \
  --filter '{"conjunction":"and","conditions":[{"field_name":"关联款","operator":"contains","value":"<款record_id>"}]}'

# 直播
lark-cli base +record-list --base-token <APP> --table-id tblAuzO7UsdjlXyL \
  --filter '{"conjunction":"and","conditions":[{"field_name":"主推款","operator":"contains","value":"<款record_id>"}]}'

# 退货
lark-cli base +record-list --base-token <APP> --table-id tblCwJGr0HTMFtXD \
  --filter '{"conjunction":"and","conditions":[{"field_name":"SKU","operator":"contains","value":"<款号>"}]}'
```

#### Step 3: AI 提炼元素标签

把产品名 + 描述喂给 LLM，提示词：

```
分析下面这款女装产品，提炼出关键元素标签（每类 2-3 个）：
- 颜色：xxx
- 风格：xxx（如 法式 / 通勤 / 韩系 / OL / 街头 / 复古）
- 面料：xxx（如 雪纺 / 针织 / 西装料 / 棉麻）
- 场景：xxx（如 通勤 / 度假 / 约会 / 居家）
- 版型：xxx（如 收腰 / 直筒 / A字 / 紧身）

产品：{产品名}
描述：{描述/卖点}
```

#### Step 4: 输出飞书文档

读 [`../../../lark-doc/SKILL.md`](../../../lark-doc/SKILL.md)。用 DocxXML 格式：

```bash
lark-cli docs +create --api-version v2 --content '<title>📋 X款 — 8 维产品详情</title>
<callout emoji="🎯"><p>款号：DRS-0429-FL / 季节：春夏 / 状态：在售</p></callout>
<h1>1. 经营数据</h1>
<table>...</table>
<h1>2. SKU 颜色尺码</h1>
...
<h1>8. 产品关系图</h1>
<whiteboard token="<上一步生成的 wb_token>"></whiteboard>'
```

---

### 工作流 B：🤖 AI 产品分析助手（杀手锏 1）

**触发语：** "找出售罄率<50%的春夏款" / "比较 X 和 Y 哪个更赚钱" / "哪些款滞销" / "回报率最高的 5 款"

#### 执行流程

```
用户问："找出售罄率<50%的产品，按春夏秋冬分类，按售卖权重排序"
        ↓
Step 1: AI 把自然语言问题翻译成结构化 query
        ↓
Step 2: 用 lark-cli base +data-query 跑（含聚合/筛选/排序）
        ↓
Step 3: AI 把查询结果总结成飞书文档（含表格 + 洞察 + 建议）
```

#### Step 1: 自然语言 → 结构化 query

AI 提示词模板：

```
把下面的业务问题翻译成 lark-cli base +data-query 的 JSON 配置：

业务问题：{用户原话}

可用字段（01_产品库）：
- 款号 (text)
- 品类 (select: 连衣裙/裤装/上衣/外套/半裙/针织/衬衫)
- 季节 (select: 春夏/秋冬/早春/早秋)
- 状态 (select: 在售/售罄/历史款/开发中)
- 库存 (number)
- 做货数 (number)
- 已实销 (number)
- 售价 (number)

派生指标（公式）：
- 售罄率 = 已实销 / 做货数 * 100
- 实销 GMV = 已实销 × 售价
- 库存周转 = 库存 / (已实销 / 30)（天）

输出 JSON 结构：{table_name, series, group_by, filter, sort, limit}
```

#### Step 2: 跑查询

```bash
lark-cli base +data-query \
  --base-token <APP> \
  --table-id tblrKzymnPPQ98ZX \
  --json @./query.json
```

#### Step 3: 输出飞书文档

```bash
lark-cli docs +create --api-version v2 --content '<title>🤖 AI 产品分析 — {用户问题}</title>
<callout emoji="📊"><p>{结论一句话}</p></callout>
<h1>查询结果</h1>
<table>...</table>
<h1>洞察</h1>
<ul><li>...</li></ul>
<h1>行动建议</h1>
<checkbox done="false">...</checkbox>'
```

#### 用户预设问题（可在 README 列出）

- "找出售罄率<50%的产品，按季节分类排序"
- "哪些款距目标还需实销最多，给出优先推进顺序"
- "高退货率 + 高库存的风险款"
- "本季度 ROI 最高的 5 款"

---

### 工作流 C：🕸️ 产品关系图（杀手锏 2）

**触发语：** "画下 X 款的关系图" / "X 款关联了哪些资源" / "X 款的全景"

读 [`../../../lark-whiteboard/SKILL.md`](../../../lark-whiteboard/SKILL.md) 学习 DSL/Mermaid 写法。

#### Step 1: 收集关联数据

调用上面工作流 A 的 Step 2，拿到该产品关联的：
- N 个 SKU（颜色×尺码）
- M 个内容（选题/文案）
- K 个直播场次
- L 个投流活动
- P 个素材
- Q 个元素标签

#### Step 2: 用 Mermaid 画图

```bash
WB_CONTENT='graph LR
  P[📦 DRS-0429-FL<br/>法式收腰碎花连衣裙] --> S1[🎨 莓果红/M]
  P --> S2[🎨 奶油白/L]
  P --> C1[🎬 抖音种草视频]
  P --> C2[📷 小红书图文]
  P --> L1[🎤 4/15 主播 A 直播]
  P --> L2[🎤 4/22 主播 B 直播]
  P --> A1[💰 抖音投流活动]
  P --> M1[🎨 模特图×20]
  P --> T1[🏷️ 法式 / 收腰 / 雪纺]'

lark-cli whiteboard +update \
  --doc-token <挂载文档> \
  --whiteboard-token <wb_token> \
  --type mermaid \
  --content "$WB_CONTENT"
```

或者用飞书白板的 DSL（更精细控制配色和形状），见 [`../../../lark-whiteboard/SKILL.md`](../../../lark-whiteboard/SKILL.md)。

---

### 工作流 D：➕ 新增产品

**触发语：** "新增产品 X" / "录入新款 X"

```bash
cat > /tmp/new-product.json << 'EOF'
{
  "fields": ["款号","产品名称","品类","季节","状态","颜色","尺码","库存","做货数","已实销","售价"],
  "rows": [
    ["DRS-2026-0501-NEW", "品牌一-法式茶歇连衣裙", "连衣裙", "春夏", "开发中", ["奶油白","莓果红"], ["S","M","L"], 0, 300, 0, 269]
  ]
}
EOF

lark-cli base +record-batch-create \
  --base-token <APP> \
  --table-id tblrKzymnPPQ98ZX \
  --json @/tmp/new-product.json
```

后续可以让 agent 顺便：
- 创建对应的"开发中"上新波段（如未存在）
- 在 09_生产档案 录入打样任务（链 task-collaboration skill）

---

## 三、涉及多维表

| 表 | 操作 | 用途 |
|---|---|---|
| `01_产品库` | 读 / 写 | 主体 |
| `02_4平台销售` | 读 | 拉销售数据 |
| `05_任务清单` | 读 | 拉关联任务 |
| `06_选题池` | 读 | 拉关联选题 |
| `07_文案库` | 读 | 拉关联文案 |
| `08_直播排期` | 读 | 拉直播场次 |
| `11_退货反馈` | 读 | 拉退货数据 |
| `16_竞品产品监控` | 读 | 拉对标款数据 |

---

## 四、典型对话示例

### 例 1：8 维详情报告

```
用户：看下 DRS-0429-FL 这款怎么样

agent：
正在拉取 8 维数据...
✓ 经营：库存 280 / 做货 600 / 已实销 320（售罄率 53%）/ 售价 ¥299
✓ SKU：莓果红 + 奶油白 × XS-XL（10 个 SKU）
✓ 内容：3 条抖音种草、2 条小红书图文
✓ 直播：4/22 主播 A 主推
✓ 退货：12 条退货，主因「尺码偏小」
✓ 元素标签：法式 / 收腰 / 雪纺 / 春夏 / 通勤约会

📋 报告已生成：https://my.feishu.cn/docx/<doc_id>
🕸️ 关系图：https://my.feishu.cn/board/<wb_id>

⚠️ 风险：尺码退货率偏高，建议下批生产时调整版型。
```

### 例 2：AI 产品分析

```
用户：找出春夏款里售罄率低于 50% 的，按销量排序，告诉我哪些该清仓

agent：
✓ 解析问题为结构化 query
✓ 跑 base +data-query
✓ 找到 4 款：
  1. 品牌二-OL极简通勤西服（40%）— 库存 180，建议清仓
  2. ...

📊 分析报告 + 清仓建议已生成：https://my.feishu.cn/docx/...
```

---

## 五、参考

- [`../../../lark-base/references/lark-base-data-query.md`](../../../lark-base/references/lark-base-data-query.md) — data-query DSL
- [`../../../lark-whiteboard/SKILL.md`](../../../lark-whiteboard/SKILL.md) — 白板/关系图
- [`../../../lark-doc/SKILL.md`](../../../lark-doc/SKILL.md) — 文档创建
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md) — 跨部门任务（建产品后建任务）
