---
name: lark-fashion-cockpit-order-fulfillment
version: 1.0.0
description: "订单履约 + 物流 — 订单状态、超时风险、物流异常。当用户说「看订单」「履约异常」「待发货」「物流状态」「超时订单」时使用。属于 lark-fashion-cockpit 供应链履约板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 订单履约 + 物流

> **板块：** 🅳 供应链履约  
> **调用：** `base` + `im`  
> **多维表依赖：** 自定义订单表（用户对接电商 API 后录入）

> ⚠️ 由于电商平台订单 API 各家不同，本 skill 提供数据中枢框架，具体采集路径用户根据自己接入方式补充。

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create im:message:write"
```

## 二、工作流

### 场景 A: 订单总览

**触发语：** "看订单" / "今日订单"

读各平台订单表（用户自定义建表，如 17_订单流水）：

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id <订单表> \
  --json '{
    "table_name":"订单流水",
    "count_all":true,
    "group_by":[{"field_name":"订单状态","mode":"integrated"}]
  }'
```

### 场景 B: 履约异常预警

**触发语：** "看异常" / "超时订单"

```
Step 1: 筛选 状态=已付款 AND 付款时间 > 24小时前 AND 未发货
Step 2: 列出超时订单清单
Step 3: 私聊提醒发货同事
```

### 场景 C: 物流异常监控

**触发语：** "物流异常"

筛选物流状态异常（揽收延迟/派送失败/拒收/退回）：

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id <订单表> \
  --filter '{"conjunction":"or","conditions":[
    {"field_name":"物流状态","operator":"is","value":"揽收延迟"},
    {"field_name":"物流状态","operator":"is","value":"派送失败"},
    {"field_name":"物流状态","operator":"is","value":"拒收"}
  ]}'
```

AI 生成处理建议（联系客户 / 重发 / 退款）。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `订单流水`（自定义）| 读 |

## 四、典型对话示例

```
用户：看下今天订单异常

agent：
✓ 今日订单 412 单
✓ 异常 5 单：
  - 3 单超时未发货（@仓库 王五 处理）
  - 1 单物流退回（@客服 李四 联系客户）
  - 1 单地址异常（@客服 李四 改地址）

✓ 已私聊提醒相关同事
```

## 五、与其他 skill 协作

- `private-domain`：客户层级影响处理优先级（钻石优先）
- `task-collaboration`：建处理任务给客服

## 六、参考

- 等待电商平台 API 接入后细化
- [`../private-domain/SKILL.md`](../private-domain/SKILL.md)
