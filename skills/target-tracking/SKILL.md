---
name: lark-fashion-cockpit-target-tracking
version: 1.0.0
description: "目标进度追踪 — 年度/季度/月度/平台目标 vs 实际，达成率自动算 + 缺口预警。当用户说「看年度目标」「Q2 进度」「这个月 GMV 还差多少」「平台目标完成率」「目标缺口」时使用。属于 lark-fashion-cockpit 公司经营板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 目标进度追踪

> **板块：** 🅰 公司经营  
> **调用：** `base` + `doc`  
> **多维表依赖：** `02_4平台销售` / `13_OKR`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read docs:document:write_only"
```

## 二、工作流

### 场景 A: 看年度目标进度

**触发语：** "看年度进度" / "今年完成了多少" / "全年目标达成率"

```bash
# Step 1: 读 13_OKR 找年度 OKR
lark-cli base +record-list \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --filter '{"conjunction":"and","conditions":[{"field_name":"周期","operator":"is","value":"2026年度"}]}'

# Step 2: 读 02_4平台销售 算 YTD GMV
lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[{"field_name":"GMV","rollup":"SUM"}],
    "filter":{"conjunction":"and","conditions":[
      {"field_name":"日期","operator":"isGreaterEqual","value":"<本年1/1毫秒>"}
    ]}
  }'

# Step 3: AI 计算达成率 + 剩余天数 + 日均所需 GMV
# Step 4: 输出飞书文档
```

### 场景 B: 看季度/月度进度

类似上面，把 OKR 周期换成 `2026Q2` 或月份。

### 场景 C: 平台目标进度

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[{"field_name":"GMV","rollup":"SUM"}],
    "group_by":[{"field_name":"平台","mode":"integrated","sort":{"type":"value","order":"desc"}}]
  }'
```

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `02_4平台销售` | 读（聚合 GMV）|
| `13_OKR` | 读（取目标值）|

## 四、典型对话示例

```
用户：今年完成了多少

agent：
✓ 年度 GMV 目标 ¥500 万
✓ YTD（截至 5/3）已完成 ¥187 万 = 37.4%
✓ 剩余 242 天，日均需要 ¥12,938 才能达标
✓ 当前日均 ¥18,700，进度 ✅ 超前

📊 详情：https://my.feishu.cn/docx/<id>
```

## 五、与其他 skill 协作

- `morning-report`：晨报里展示当日进度
- `okr-cascade`：拆到部门/个人 OKR
- `profit-analysis`：搭配看利润而非纯 GMV

## 六、参考

- [`../okr-cascade/SKILL.md`](../okr-cascade/SKILL.md)
- [`../platform-analytics/SKILL.md`](../platform-analytics/SKILL.md)
