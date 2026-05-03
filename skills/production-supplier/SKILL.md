---
name: lark-fashion-cockpit-production-supplier
version: 1.0.0
description: "生产 + 供应商管理 — 生产进度跟踪、供应商档案、成品率/准时率监控。当用户说「看生产进度」「工厂状态」「打样到哪了」「供应商表现」时使用。属于 lark-fashion-cockpit 供应链履约板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 生产 + 供应商管理

> **板块：** 🅳 供应链履约  
> **调用：** `base` + `task` + `im`  
> **多维表依赖：** `09_生产档案`（核心）/ `01_产品库`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create base:record:update task:task:write im:message:write"
```

## 二、工作流

### 场景 A: 生产进度看板

**触发语：** "看生产进度" / "工厂状态" / "打样到哪了"

```bash
# 按进度阶段分组
lark-cli base +data-query \
  --base-token <APP> --table-id tblePNIIcpUvTPLp \
  --json '{
    "table_name":"09_生产档案",
    "count_all":true,
    "group_by":[{"field_name":"进度","mode":"integrated"}]
  }'
```

或打开 09_生产档案 表的看板视图（按进度分列）。

### 场景 B: 单工厂表现分析

**触发语：** "X 工厂怎么样" / "供应商表现"

```bash
# 读单工厂的所有生产单
lark-cli base +record-list \
  --base-token <APP> --table-id tblePNIIcpUvTPLp \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"工厂","operator":"is","value":"杭州XX服饰"}
  ]}'

# AI 算：平均成品率 / 平均交期延误 / 完成率
```

### 场景 C: 延期预警

**触发语：** "看延期" / "哪个工厂延误了"

```bash
NOW=$(date +%s)000

# 筛选：交期 < 今天 AND 状态 != 已交付
lark-cli base +record-list \
  --base-token <APP> --table-id tblePNIIcpUvTPLp \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"交期","operator":"isLess","value":"'$NOW'"},
    {"field_name":"进度","operator":"isNot","value":"已交付"}
  ]}'

# 私聊提醒生产主管
lark-cli im chats messages create --user-id <生产主管> --msg-type text \
  --content '{"text":"⚠️ 3 个生产单已超期，请联系工厂跟进"}'
```

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `09_生产档案` | 读 / 写 |
| `01_产品库` | 读（在做款）|
| `05_任务清单` | 写（跟进任务）|

## 四、典型对话示例

```
用户：看生产进度

agent：
✓ 当前 12 个生产单：
  打样 3 / 在做 5 / 质检 2 / 入仓 1 / 已交付 1

⚠️ 风险：
- 杭州XX服饰：DRS-0429-FL × 600 件，交期 5/8（剩 5 天，进度 60%）
- 广州YY制衣：PNT-0418-SU × 600 件，已超期 2 天 🔴

✓ 已私聊生产主管 @张三 提醒
✓ 建议：超期单建议 IM 工厂询问，必要时换厂
```

## 五、与其他 skill 协作

- `stock-replenishment`：补货任务对应生产单
- `task-collaboration`：跟进任务给生产主管
- `new-launch-planning`：上新波段的打样跟进

## 六、参考

- [`../stock-replenishment/SKILL.md`](../stock-replenishment/SKILL.md)
- [`../new-launch-planning/SKILL.md`](../new-launch-planning/SKILL.md)
