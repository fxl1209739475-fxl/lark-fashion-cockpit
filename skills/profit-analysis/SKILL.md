---
name: lark-fashion-cockpit-profit-analysis
version: 1.0.0
description: "利润财务分析 — 平台利润拆解 + 成本结构 + 单品利润排行（看哪些款真赚钱）。当用户说「看利润」「单品利润排行」「平台 ROI」「成本结构」「哪些款赚钱」时使用。属于 lark-fashion-cockpit 公司经营板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 利润财务分析

> **板块：** 🅰 公司经营  
> **调用：** `base` + `doc` + AI  
> **多维表依赖：** `01_产品库` / `02_4平台销售`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read docs:document:write_only"
```

## 二、工作流

### 场景 A: 单品利润排行（核心）

**触发语：** "哪些款真赚钱" / "单品利润排行" / "看利润榜"

```
Step 1: 读 01_产品库 + 02_4平台销售
Step 2: AI 计算每款单品利润 = 已实销 × (售价 - 成本)
   注：成本字段如未配置，假设 = 售价 × 0.4（行业默认）
Step 3: 排序，输出 Top 10 / Bottom 10
Step 4: 写飞书文档
```

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --json '{
    "table_name":"01_产品库",
    "series":[{"field_name":"已实销","rollup":"SUM"}],
    "group_by":[{"field_name":"款号","mode":"integrated","sort":{"type":"value","order":"desc"}}],
    "limit":10
  }'
```

### 场景 B: 平台利润拆解

每个平台 GMV - 投放 - 平台扣点 - 物流 = 净利。

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[{"field_name":"GMV","rollup":"SUM"}],
    "group_by":[{"field_name":"平台","mode":"integrated"}]
  }'

# AI 后处理：扣点系数
# 淘宝 5% / 抖音 5% / 小红书 8% / 视频号 5%
# 投放 + 物流自定义补充
```

### 场景 C: 成本结构

商品成本 + 平台扣点 + 投放 + 达人佣金 + 物流 = 总成本。

输出饼图（用 dashboard）+ 文字解读。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `01_产品库` | 读（售价、已实销）|
| `02_4平台销售` | 读（GMV）|

## 四、典型对话示例

```
用户：哪些款真赚钱

agent：
✓ 已分析 8 款产品
🥇 SHT-0420-SP（防晒衬衫）：利润 ¥45,675（已实销 450 × 利润率 60%）
🥈 DRS-0429-FL（碎花连衣裙）：¥38,304
🥉 OUT-2024-OL（OL 西服）：¥33,048
...

📊 利润榜单：https://my.feishu.cn/docx/<id>
💡 建议：把营销资源向 Top 3 倾斜
```

## 五、与其他 skill 协作

- `target-tracking`：搭配 GMV 进度看
- `morning-report`：晨报展示日利润
- `okr-cascade`：利润 OKR 进度

## 六、参考

- [`../target-tracking/SKILL.md`](../target-tracking/SKILL.md)
- [`../platform-analytics/SKILL.md`](../platform-analytics/SKILL.md)
