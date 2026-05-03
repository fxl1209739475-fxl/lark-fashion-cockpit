---
name: lark-fashion-cockpit-okr-cascade
version: 1.0.0
description: "OKR 目标拆解 — 年度→季度→平台→部门→个人，与任务清单双向关联（任务承接 OKR）。当用户说「看 OKR」「拆 Q2 目标」「部门 OKR」「OKR 进度」时使用。属于 lark-fashion-cockpit 公司管理板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# OKR 目标拆解

> **板块：** 🅴 公司管理  
> **调用：** `okr` + `base` + `doc`  
> **多维表依赖：** `13_OKR`（核心）/ `05_任务清单`（双向关联，承接拆解任务）

## 一、前置条件

```bash
lark-cli auth login --scope "okr:okr:read okr:okr:write base:record:read base:record:create"
```

读 [`../../../lark-okr/SKILL.md`](../../../lark-okr/SKILL.md)。

## 二、工作流

### 场景 A: 看当前 OKR 全景

**触发语：** "看 OKR" / "Q2 目标全部" / "公司 OKR"

```bash
# 读飞书原生 OKR
lark-cli okr periods list --jq '.data.periods[] | {id, name, status}'
lark-cli okr okrs list --period-id <Q2_id>

# 同时读多维表镜像（含拆解任务双向关联）
lark-cli base +record-list \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"周期","operator":"is","value":"2026Q2"}
  ]}'
```

### 场景 B: 拆解 OKR 到部门/个人

**触发语：** "把 Q2 GMV 目标拆到 4 个平台" / "拆部门 OKR"

```bash
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --json '{
    "fields":["OKR标题","周期","Objective","KR列表","进度","部门"],
    "rows":[
      ["Q2 淘宝 GMV 200 万","2026Q2","淘宝渠道完成 200 万 GMV","KR1: 月均 ≥66 万 KR2: 转化率 ≥3%",0,"运营"]
    ]
  }'
```

### 场景 C: OKR 进度自动更新

由于 OKR ↔ 任务双向关联，OKR 表里"拆解任务"字段自动同步：

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --record-id <okr_id> \
  --jq '.data.record.fields["拆解任务"]'

# AI 算进度：已完成任务数 / 总任务数 × 权重
lark-cli base +record-update \
  --base-token <APP> --table-id tbl0tdusQ2fw98wZ \
  --record-id <okr_id> \
  --json '{"进度": 65}'
```

### 场景 D: OKR 周报

每周一自动跑 + 推送到部门群：

```bash
lark-cli docs +create --api-version v2 --content '<title>📊 OKR 周报 — 第 X 周</title>
<callout emoji="🎯"><p>4 个 OKR，平均完成 65%，落后 1 项</p></callout>
<h1>各 OKR 进度</h1>
...
<h1>本周关键风险</h1>
<ul><li>商品上新 OKR 落后 ⚠️ 因打样周期延误</li></ul>'
```

## 三、双向关联的妙用

```
13_OKR.「2026Q1商品上新」
  └─ 拆解任务（自动反向）
      ├─ 1. 选款评审会 ✅
      ├─ 2. 设计稿出图 ✅
      ├─ 3. 打版 ✅
      ├─ 4. 打样 ✅
      ├─ 5. 大货生产投单 🟡
      ├─ 6. 主图拍摄 🟡
      └─ ...（共 8 条，4 已完成 = OKR 进度 50%）
```

## 四、典型对话示例

```
用户：看 Q2 OKR 进度

agent：
✓ 4 个 OKR
  🟢 全公司业绩：65% (轨道内)
  🟡 商品上新：58% (落后 7%，打样延误)
  🟢 抖音内容：72% (超前)
  🟢 客户体验：80% (超前)

📊 周报：https://my.feishu.cn/docx/<id>
⚠️ 商品上新 OKR 需要您关注，建议给生产主管加压。
```

## 五、与其他 skill 协作

- `task-collaboration`：任务建立时自动关联到 OKR
- `meeting-workflow`：会议行动项自动挂到 OKR
- `morning-report`：晨报里展示 OKR 进度

## 六、参考

- [`../../../lark-okr/SKILL.md`](../../../lark-okr/SKILL.md)
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
- [`../meeting-workflow/SKILL.md`](../meeting-workflow/SKILL.md)
