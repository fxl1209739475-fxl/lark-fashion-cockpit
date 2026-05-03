---
name: lark-fashion-cockpit-morning-report
version: 1.0.0
description: "经营晨报 — 整合 4 平台数据 + 库存预警 + 任务进度 + OKR 达成率，AI 生成简报推送到老板群。当用户说「今天经营怎么样」「店铺日报」「老板早报」「我家店今日数据」「看下今日异常」时使用。可手动触发或 cron 定时（每日 08:00）。属于 lark-fashion-cockpit 公司经营板块。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# 经营晨报 — 一句话看店

> **🌅 老板娘最爱用的能力。** 每天早上 8 点（或一句话触发），agent 自动整合所有运营数据 → AI 生成简报 → 飞书 IM 卡片推送。

> **板块：** 🅰 公司经营  
> **调用 lark-cli skill：** `base` + `doc` + `im`  
> **多维表依赖：** `01_产品库` / `02_4平台销售` / `03_库存预警` / `05_任务清单` / `13_OKR` / `经营总览仪表盘`

---

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:dashboard:read docs:document:write_only im:message:write"
```

---

## 二、工作流（5 维度整合）

```
触发：用户说"今天怎么样" 或 cron 08:00
        ↓
Step 1: 读 02_4平台销售 — 昨日销售总览（GMV/订单/转化）
Step 2: 读 03_库存预警 — 当前预警 SKU 列表
Step 3: 读 05_任务清单 — 进行中 + 超期任务
Step 4: 读 13_OKR — 各 OKR 进度
Step 5: 读 经营总览 仪表盘 — 总体健康度
        ↓
AI 整合：5 维数据 → 简报模板
        ↓
输出：
- 飞书文档（详细报告，可点开查看）
- IM 卡片（精华版推送到老板群/私聊）
```

---

### Step 1: 4 平台销售总览

```bash
# 昨天的销售数据
YESTERDAY=$(date -d 'yesterday' +%s)000
TODAY_0=$(date +%s)000

lark-cli base +record-list \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"日期","operator":"isGreaterEqual","value":"'$YESTERDAY'"},
    {"field_name":"日期","operator":"isLess","value":"'$TODAY_0'"}
  ]}' \
  --jq '[.data.records[] | {平台:.fields.平台, GMV:.fields.GMV, 订单:.fields.订单数, UV:.fields.UV, 转化率:.fields.转化率}]'
```

预期输出：
```json
[
  {"平台":"淘宝", "GMV":98600, "订单":512, "UV":18640, "转化率":2.75},
  {"平台":"抖音", "GMV":85400, "订单":420, "UV":35200, "转化率":1.19},
  ...
]
```

### Step 2: 库存预警（紧急 + 中等）

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblq2jhCQiRFeDXh \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"紧急度","operator":"is","value":"紧急"}
  ]}'
```

### Step 3: 任务异常

```bash
NOW=$(date +%s)000
TOMORROW=$(date -d '+1 day' +%s)000

# 超期 / 即将超期
lark-cli base +record-list \
  --base-token <APP> --table-id tblRnB14n1xW1vou \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"is","value":"进行中"},
    {"field_name":"截止日期","operator":"isLess","value":"'$TOMORROW'"}
  ]}'
```

### Step 4: OKR 进度

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"周期","operator":"is","value":"2026Q2"}
  ]}' \
  --jq '[.data.records[] | {OKR:.fields["OKR标题"], 进度:.fields.进度, 部门:.fields.部门}]'
```

### Step 5: AI 整合 + 输出

把 4 步的数据塞给 LLM，提示词模板：

```
你是一个女装电商品牌运营助手。基于下面的数据生成一份「经营晨报」（150-300字）：

【昨日销售】
{step1 数据}

【库存预警】
{step2 数据}

【任务异常】
{step3 数据}

【OKR 进度】
{step4 数据}

输出格式（DocxXML 适配飞书文档）：
<title>🌅 经营晨报 - YYYY-MM-DD</title>
<callout emoji="🎯"><p>【一句话总结】昨日 GMV X 万 / 同比 +X% / 异常 X 项</p></callout>
<h1>📈 4 平台销售</h1>
<table>...</table>
<h1>⚠️ 异常事项（按优先级）</h1>
<ul><li>...</li></ul>
<h1>🎯 OKR 进度</h1>
...
<h1>✅ 今日推荐行动</h1>
<checkbox done="false">...</checkbox>
```

### Step 6: 飞书文档创建

```bash
lark-cli docs +create --api-version v2 --content "@/tmp/morning-report.xml"
# 拿到 doc_url
```

### Step 7: IM 卡片推送

```bash
lark-cli im chats messages create \
  --user-id "<老板 open_id>" \
  --msg-type interactive \
  --content '{
    "config":{"wide_screen_mode":true},
    "header":{"title":{"tag":"plain_text","content":"🌅 5 月 4 日经营晨报"},"template":"green"},
    "elements":[
      {"tag":"div","text":{"tag":"lark_md","content":"**昨日 GMV** ¥8.6 万 (+12% MoM)\n**异常** 3 项 ⚠️\n\n【库存预警】SKT-0328-A 售罄风险\n【任务超期】设计稿出图 张三\n【OKR 落后】2026Q2 商品上新 进度 58%"}},
      {"tag":"action","actions":[
        {"tag":"button","text":{"tag":"plain_text","content":"查看完整报告"},"type":"primary","url":"<doc_url>"}
      ]}
    ]
  }'
```

---

## 三、定时执行（cron 模式）

可以让用户配置每天 08:00 自动跑：

```bash
# 在用户机器上加一个 crontab（macOS/Linux）
0 8 * * * cd /path/to/lark-fashion-cockpit && agent run morning-report > /tmp/morning-report.log 2>&1

# 或者用 lark-event 订阅"每日触发"事件（如果飞书有该能力）
```

---

## 四、典型对话示例

```
用户：今天经营怎么样

agent：
正在拉取 5 维数据...
✓ 4 平台销售（昨日总 ¥86,400 / 同比 +12%）
✓ 库存预警 1 条紧急
✓ 任务超期 1 条
✓ OKR 进度（4 个，平均 68.75%）

🌅 简报已生成 → 已推送到您的私聊
查看完整：https://my.feishu.cn/docx/<doc_id>
```

---

## 五、参考

- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md) — 任务异常详情
- [`../stock-replenishment/SKILL.md`](../stock-replenishment/SKILL.md) — 库存详细处理
- [`../okr-cascade/SKILL.md`](../okr-cascade/SKILL.md) — OKR 进度详细
- [`../../../lark-base/references/lark-base-data-query.md`](../../../lark-base/references/lark-base-data-query.md) — 聚合查询
