---
name: lark-fashion-cockpit-live-streaming
version: 1.0.0
description: "营销直播管理 — 直播排期、活动 ROI、主推款管理、主播档案。当用户说「看直播排期」「下周直播」「直播 ROI」「主推款」「投流活动」时使用。属于 lark-fashion-cockpit 销售增长板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 营销直播管理

> **板块：** 🅲 销售增长  
> **调用：** `base` + `calendar` + `task`  
> **多维表依赖：** `08_直播排期`（核心）/ `01_产品库`（主推款）

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create calendar:calendar.event:create task:task:write"
```

## 二、工作流

### 场景 A: 看直播排期

**触发语：** "看直播排期" / "下周直播"

```bash
NEXT_WEEK_END=$(date -d '+7 day' +%s)000
NOW=$(date +%s)000

lark-cli base +record-list \
  --base-token <APP> --table-id tblAuzO7UsdjlXyL \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"日期","operator":"isGreaterEqual","value":"'$NOW'"},
    {"field_name":"日期","operator":"isLess","value":"'$NEXT_WEEK_END'"}
  ]}'
```

### 场景 B: 排一场新直播

**触发语：** "排个直播" / "新增直播"

```bash
# Step 1: 在 08_直播排期 建记录
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblAuzO7UsdjlXyL \
  --json '{
    "fields":["日期","主播","主推款","预估GMV","直播间链接"],
    "rows":[
      [<日期 ms>, [{"id":"<主播 open_id>"}], [{"id":"<款 record_id>"}], 50000, "https://live.douyin.com/..."]
    ]
  }'

# Step 2: 飞书日历加事件提醒主播
lark-cli calendar +create-event --title "5/10 直播 主推: DRS-0429-FL"

# Step 3: 给主播建准备任务（链 task-collaboration）
lark-cli task +create --summary "直播预热: 5/10 主推 DRS-0429-FL" --assign-role "主播"
```

### 场景 C: 直播 ROI 复盘

**触发语：** "上场直播怎么样" / "直播 ROI"

```bash
# 读直播排期 + 销售数据对比预估 vs 实际
lark-cli base +record-list \
  --base-token <APP> --table-id tblAuzO7UsdjlXyL \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"日期","operator":"isLess","value":"<今天 ms>"}
  ]}' --jq '[.data.records[] | {日期, 主播, 预估GMV:.fields["预估GMV"], 实际GMV:.fields["实际GMV"]}]'
```

AI 分析达成率、主播效率、主推款转化。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `08_直播排期` | 读 / 写 |
| `01_产品库` | 读（主推款）|
| `05_任务清单` | 写（直播准备任务）|

## 四、典型对话示例

```
用户：排个 5/15 直播，主推 DRS-0429-FL

agent：
✓ 已建直播排期：5/15 19:00
✓ 主播：@张三（自动分配，根据近 30 天 ROI 推荐）
✓ 主推款：DRS-0429-FL（库存 280，足够直播销售）
✓ 预估 GMV：¥48,000（基于该款近 4 场直播均值）
✓ 飞书日历已加提醒
✓ 已给 @张三 建直播预热任务（5 个子任务）

详情：https://my.feishu.cn/base/<APP>?table=tblAuzO7UsdjlXyL
```

## 五、与其他 skill 协作

- `task-collaboration`：直播准备任务下发给主播
- `content-pipeline`：直播预热视频从选题池抽
- `product-library`：主推款的 8 维详情参考

## 六、参考

- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
- [`../product-library/SKILL.md`](../product-library/SKILL.md)
