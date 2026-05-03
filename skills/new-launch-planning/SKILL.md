---
name: lark-fashion-cockpit-new-launch-planning
version: 1.0.0
description: "商品企划上新波段 — 上新批次规划与跟踪、开发款式管理、商品结构分析。当用户说「看上新波段」「Q2 上新计划」「开发中款式」「商品结构」「企划新一波上新」时使用。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 商品企划上新波段

> **板块：** 🅱 商品中心  
> **调用：** `base` + `calendar` + `task` + `doc`  
> **多维表依赖：** `04_上新波段`（核心）/ `01_产品库`（开发中款式）/ `05_任务清单`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create calendar:calendar.event:create task:task:write docs:document:write_only"
```

## 二、工作流

### 场景 A: 看当前上新波段

**触发语：** "看上新波段" / "本季上新计划"

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblnXnsxZN0H0z3P \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"isNot","value":"已完成"}
  ]}'
```

或打开 `04_上新波段` 表的卡片视图直接看图。

### 场景 B: 企划新一波上新

**触发语：** "企划 X 波段" / "新建一波上新"

```bash
# Step 1: 创建波段记录
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblnXnsxZN0H0z3P \
  --json '{
    "fields":["波段名","启动日期","预计上架日","状态","关联产品"],
    "rows":[
      ["2026Q3 早秋第一波", <启动日 ms>, <上架日 ms>, "企划中", [{"id":"<款1>"},{"id":"<款2>"}]]
    ]
  }'

# Step 2: 在飞书日历建里程碑事件
lark-cli calendar +create-event --title "2026Q3 早秋第一波 上架日" --start "2026-08-01" --description "..."

# Step 3: 调 task-collaboration 把任务下发
```

### 场景 C: 商品结构分析

**触发语：** "看商品结构" / "类目分布" / "价格带分析"

```bash
# 按品类
lark-cli base +data-query \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --json '{
    "table_name":"01_产品库",
    "count_all":true,
    "group_by":[{"field_name":"品类","mode":"integrated","sort":{"type":"value","order":"desc"}}]
  }'
```

### 场景 D: 开发中款式跟踪

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"is","value":"开发中"}
  ]}'
```

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `04_上新波段` | 读 / 写 |
| `01_产品库` | 读（开发中款式）|
| `05_任务清单` | 写（链 task-collaboration）|
| `09_生产档案` | 读（打样进度）|

## 四、典型对话示例

```
用户：企划一波早秋上新，5 款

agent：
✓ 已创建 04_上新波段：「2026Q3 早秋第一波」
✓ 飞书日历加事件：8/1 上架日（提前 90 天提醒）
✓ 关联开发中产品：5 款
✓ 已自动调 task-collaboration 下发 12 个任务给团队

📋 波段详情：https://my.feishu.cn/base/<APP>?table=tblnXnsxZN0H0z3P
```

## 五、与其他 skill 协作

- `task-collaboration`：下发上新任务（核心闭环）
- `production-supplier`：跟工厂打样进度
- `content-pipeline`：每个新款进入选题池

## 六、参考

- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
- [`../production-supplier/SKILL.md`](../production-supplier/SKILL.md)
