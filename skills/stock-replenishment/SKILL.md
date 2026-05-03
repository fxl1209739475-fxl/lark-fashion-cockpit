---
name: lark-fashion-cockpit-stock-replenishment
version: 1.0.0
description: "库存补货决策 — 自动巡检低库存 SKU + AI 算补货量 + 平台库存分配建议 + IM 卡片告警。当用户说「看下哪些要补货」「库存预警」「售罄风险」「平台库存怎么分」时使用。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 库存补货决策

> **板块：** 🅱 商品中心  
> **调用：** `base` + `im` + `task` + AI  
> **多维表依赖：** `01_产品库`（读）/ `03_库存预警`（写）/ `02_4平台销售`（读销售速率）

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create im:message:write task:task:write"
```

## 二、工作流

### 场景 A: 自动巡检低库存

**触发语：** "看下哪些要补货" / "巡检库存" / "低库存预警"

```
Step 1: 读 01_产品库 筛选 状态!=历史款 AND 库存 < 阈值
Step 2: 读 02_4平台销售 算每个 SKU 近 7 天日均销量
Step 3: AI 计算补货建议（覆盖未来 30 天 + 安全库存）
Step 4: 写入 03_库存预警 表
Step 5: IM 红色卡片告警 + task 建补货任务
```

#### Step 1: 筛选低库存款

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"isNot","value":"历史款"},
    {"field_name":"库存","operator":"isLess","value":50}
  ]}'
```

#### Step 2: 销售速率（近 7 天日均）

```bash
SEVEN_DAYS_AGO=$(date -d '-7 day' +%s)000

lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[{"field_name":"订单数","rollup":"SUM"}],
    "group_by":[{"field_name":"关联款","mode":"enumerated"}],
    "filter":{"conjunction":"and","conditions":[
      {"field_name":"日期","operator":"isGreaterEqual","value":"'$SEVEN_DAYS_AGO'"}
    ]}
  }'
```

#### Step 3: AI 补货建议

提示词：

```
对每款低库存 SKU，基于以下数据给出补货建议：
- 当前库存：{库存}
- 安全线：50（建议覆盖 7 天）
- 近 7 天销量：{销量}
- 日均销量：{日均}
- 生产交期：21 天

输出：
- 紧急度：紧急 / 中 / 低
  - 紧急：当前库存 < 5 天日均销量
  - 中：5-15 天
  - 低：>15 天
- 建议补货量：覆盖 30 天 + 安全库存
- 平台分配：基于过去销量占比分配（如 淘宝50%/抖音30%/小红书15%/视频号5%）
```

#### Step 4: 写入预警表

```bash
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblq2jhCQiRFeDXh \
  --json @./stock-alerts.json
```

#### Step 5: IM 告警 + 建补货任务

```bash
# 红色卡片
lark-cli im chats messages create --user-id <老板> --msg-type interactive \
  --content '{"header":{"template":"red","title":{"tag":"plain_text","content":"🔴 库存预警 — 3 个紧急 SKU"}},"elements":[...]}'

# 给生产主管建补货任务（链 task-collaboration）
lark-cli task +create --summary "补货：DRS-0429-FL × 200 件" --assign "生产主管" --priority "high"
```

### 场景 B: 平台库存分配建议

按各平台销售占比 + 平台特点给出分配策略。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `01_产品库` | 读（库存）|
| `02_4平台销售` | 读（销量） |
| `03_库存预警` | 写 |
| `05_任务清单` | 写（补货任务）|

## 四、典型对话示例

```
用户：看下哪些要补货

agent：
✓ 巡检 01_产品库（25 款在售）
✓ 发现 3 款低库存：
  🔴 SKT-0328-A：5 件，售罄风险（紧急）
  🟡 PNT-0418-SU：35 件，10 天可用（中）
  🟡 KNT-0402-CD：28 件，12 天可用（中）

✓ 已写入 03_库存预警
✓ 已建 3 个补货任务给生产主管 @张三
✓ 已发红色 IM 卡片
```

## 五、与其他 skill 协作

- `task-collaboration`：建补货任务
- `morning-report`：晨报里展示库存预警数量
- `production-supplier`：补货执行链路

## 六、参考

- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
- [`../production-supplier/SKILL.md`](../production-supplier/SKILL.md)
