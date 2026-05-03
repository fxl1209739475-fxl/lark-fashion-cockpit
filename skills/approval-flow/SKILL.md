---
name: lark-fashion-cockpit-approval-flow
version: 1.0.0
description: "审批流程自动化 — 上新预算 / 采购 / 退货特批 / 营销投放等审批，飞书移动端 1 分钟搞定。当用户说「提个审批」「我要批 X」「上新预算审批」「看待审」「我审批的」时使用。属于 lark-fashion-cockpit 公司管理板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 审批流程自动化

> **板块：** 🅴 公司管理  
> **调用：** `approval` + `base` + `im`  
> **多维表依赖：** `14_审批记录`

## 一、前置条件

```bash
lark-cli auth login --scope "approval:instance:read approval:instance:write approval:task:read approval:task:write base:record:create im:message:write"
```

读 [`../../../lark-approval/SKILL.md`](../../../lark-approval/SKILL.md)。

## 二、工作流

### 场景 A: 提交审批

**触发语：** "提个 X 审批" / "我要批 5 万采购"

```bash
# Step 1: 飞书原生审批（需要先在飞书后台创建审批模板）
lark-cli approval instances create --approval-code <code> --form '{...}'

# Step 2: 同步到 14_审批记录 多维表镜像
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblAxWcmHnFl0qUE \
  --json '{
    "fields":["审批标题","类型","金额","申请人","审批人","状态","创建日期"],
    "rows":[
      ["5/10 上新生产投单 5 万","上新预算",50000,[{"id":"<self>"}],[{"id":"<boss>"}],"待审批",<现在 ms>]
    ]
  }'

# Step 3: 给审批人发飞书 IM 卡片
lark-cli im chats messages create --user-id <boss> --msg-type interactive \
  --content '{...审批卡片，含同意/驳回按钮...}'
```

### 场景 B: 看待审 / 我审的

**触发语：** "看待审" / "我审批的" / "今天要批的"

```bash
# 飞书原生审批
lark-cli approval tasks list --status "Pending"

# 或多维表筛选
lark-cli base +record-list \
  --base-token <APP> --table-id tblAxWcmHnFl0qUE \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"is","value":"待审批"},
    {"field_name":"审批人","operator":"is","value":"<self>"}
  ]}'
```

### 场景 C: 审批分类自动路由

预设审批路由规则（可在主 SKILL.md 配置）：

| 审批类型 | 金额阈值 | 审批人 |
|---|---|---|
| 上新预算 | <3万 | 商品经理 |
| 上新预算 | 3-10万 | 老板 |
| 采购 | <1万 | 运营经理 |
| 采购 | ≥1万 | 老板 |
| 退货特批 | 任意 | 客服主管 |
| 营销投放 | <5千 | 运营经理 |
| 营销投放 | ≥5千 | 老板 |

agent 根据用户输入自动判断走哪个路由。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `14_审批记录` | 读 / 写（镜像）|

## 四、典型对话示例

```
用户：提个 5 万上新预算审批，5/10 大货生产投单

agent：
✓ 识别：审批类型=上新预算，金额=5万 → 路由到老板
✓ 已建飞书审批实例（编号 #2026-051）
✓ 同步到 14_审批记录
✓ 已给 @老板 发审批卡片（含同意/驳回按钮）

预计 1 小时内有结果。我会在审批完成后通知您。
```

## 五、与其他 skill 协作

- `task-collaboration`：审批通过后自动建后续任务
- `morning-report`：晨报展示待审批数量

## 六、参考

- [`../../../lark-approval/SKILL.md`](../../../lark-approval/SKILL.md)
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
