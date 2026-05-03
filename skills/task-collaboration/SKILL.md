---
name: lark-fashion-cockpit-task-collaboration
version: 1.0.0
description: "跨部门任务协同 — 上新波段一键下发、按角色分配任务、跟进进度、督促超期。当用户说「启动 X 上新」「把任务下发给团队」「看本月任务进度」「谁还没动」「分配任务给设计师/摄影师/主播 等」时使用。属于 lark-fashion-cockpit 的核心子 skill（🅰 公司经营板块）。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli task --help"
---

# 跨部门任务协同 — 上新一键下发

> **🎯 这是 lark-fashion-cockpit 最炸场的能力。** 用户一句话 → agent 自动拆解 N 个任务 → 批量建到飞书原生任务系统 + 同步多维表 → 分配给 9 个角色 → 设提醒 → IM 卡片汇报。

> **板块：** 🅰 公司经营  
> **调用 lark-cli skill：** `task` + `base` + `im` + `contact`  
> **多维表依赖：** `04_上新波段`（读）/ `05_任务清单`（写）/ `13_OKR`（读）/ `01_产品库`（读）

---

## 一、前置条件

执行任何动作前，**必须先读 [`../../lark-shared/SKILL.md`](../../../lark-shared/SKILL.md)** 了解认证、scope、用户 ID 解析。

### 必须授权的 scope

```bash
lark-cli auth login --scope "task:task:write task:task:read task:tasklist:write task:tasklist:read base:record:create base:record:read im:message:write contact:user:search auth:user.id:read"
```

### 必须已就位的资源

- ✅ 多维表 App 已初始化（参考主 [`SKILL.md`](../../SKILL.md) "初始化"章节，14+2 表已建好）
- ✅ `01_产品库` 至少有 1 条记录
- ✅ `04_上新波段` 至少有 1 条记录（关联产品已设置）

---

## 二、3 大工作流

### 工作流 A：🚀 上新波段一键下发（最炸的场景）

**触发语：** "启动 X 波段上新" / "下发 X 上新任务" / "把 X 上新拆给团队"

```
用户输入：「启动 2026Q2 早春第一波 上新」
        ↓
Step 1: 读 04_上新波段 找匹配波段 + 关联产品
        ↓
Step 2: 读 13_OKR 找当前周期相关 OKR（用于关联）
        ↓
Step 3: 用上新流程模板（11 步 × 角色矩阵）拆解任务
        ↓
Step 4: 批量调 lark-cli task +create 建飞书原生任务
        ↓
Step 5: 解析角色对应负责人 open_id（contact +resolve）
        ↓
Step 6: lark-cli task +assign 分配 + +reminder 设提醒
        ↓
Step 7: lark-cli base +record-batch-create 同步到 05_任务清单（含波段/OKR/产品 link）
        ↓
Step 8: lark-cli im 发卡片汇报「已下发 N 个任务」
```

#### Step 1: 读上新波段

```bash
# 替换 <BASE_TOKEN> 和波段名
lark-cli base +record-list \
  --base-token <BASE_TOKEN> \
  --table-id tblnXnsxZN0H0z3P \
  --filter '{"conjunction":"and","conditions":[{"field_name":"波段名","operator":"is","value":"2026Q2 早春第一波"}]}' \
  --jq '.data.records[0] | {wave_id: .record_id, products: .fields["关联产品"]}'
```

记录返回的 `wave_id` 和 `products`（产品 record_id 数组）。

#### Step 2: 读相关 OKR

```bash
lark-cli base +record-list \
  --base-token <BASE_TOKEN> \
  --table-id tbl0tdusQ2fw98wZ \
  --filter '{"conjunction":"and","conditions":[{"field_name":"周期","operator":"is","value":"2026Q2"},{"field_name":"部门","operator":"is","value":"商品"}]}' \
  --jq '.data.records[0].record_id'
```

记录商品 OKR 的 `okr_id`（也可同时读"内容 OKR"）。

#### Step 3: 上新流程模板拆解

按下面这张「11 步 × 9 角色」标准模板生成任务列表（以波段启动日为 0 天起算）：

| # | 任务标题模板 | 默认角色 | 优先级 | 默认 +天 | 涉及产品 | 关联 OKR |
|---|---|---|---|---|---|---|
| 1 | 选款评审会 — `<波段名>` 定稿 | 运营 | P0 | 0 | 全部 | 商品 |
| 2 | 设计稿出图 — N 款 | 设计师 | P1 | 7 | 全部 | 商品 |
| 3 | 打版 — 含尺码网格调整 | 打版师 | P1 | 12 | 全部 | 商品 |
| 4 | 打样确认 — 工厂样衣审核 | 生产主管 | P0 | 19 | 全部 | 商品 |
| 5 | 大货生产投单 | 生产主管 | P0 | 40 | 全部 | 商品 |
| 6 | 主图 + 模特图拍摄 | 摄影师 | P1 | 33 | 全部 | 商品 |
| 7 | 详情页 — 4 平台版本 | 运营 | P1 | 38 | 全部 | 商品 |
| 8 | 抖音种草视频 — N 条 | 内容编辑 | P1 | 42 | 抽 2-3 款 | 内容 |
| 9 | 小红书图文 — N 条 | 内容编辑 | P2 | 45 | 抽 2-3 款 | 内容 |
| 10 | 直播预热 + 排期 — 4 场 | 主播 | P1 | 48 | 主推 2 款 | 内容 |
| 11 | 上架 4 平台 + 投流 | 运营 | P0 | 55 | 全部 | 商品 |
| 12 | 客服话术更新 + 培训 | 客服 | P2 | 56 | 全部 | 商品 |

**总周期：约 60 天**。所以一个 4 月启动的波段，6 月初完整上线。

#### Step 4: 批量建飞书原生任务

对模板里每一行，循环：

```bash
DUE_TS=$(date -d "+7 days" +%s)000  # 转毫秒（macOS 用 gdate）

lark-cli task +create \
  --summary "2. 设计稿出图 — 5 款" \
  --description "波段：2026Q2 早春第一波\n关联款：DRS-0429-FL, SHT-0420-SP, ..." \
  --due "$DUE_TS" \
  --priority "high" \
  --jq '.data.task.guid'  # 记录返回的 task_guid
```

#### Step 5: 解析角色对应负责人

如果用户配置了"角色→人"映射（比如在 wiki 或自定义配置中），读出来。否则提示用户补全：

```bash
# 解析姓名到 open_id
lark-cli contact +resolve --query "张三" --jq '.data.users[0].open_id'
```

#### Step 6: 分配 + 设提醒

```bash
# 分配
lark-cli task +assign \
  --task-guid "$TASK_GUID" \
  --user-id "ou_xxxx" \
  --user-id-type open_id

# 截止前 1 天提醒（毫秒时间戳，截止时间 - 86400000）
REMIND_TS=$((DUE_TS - 86400000))
lark-cli task +reminder \
  --task-guid "$TASK_GUID" \
  --relative-fire-minute 1440  # 截止前 24 小时
```

#### Step 7: 同步多维表（关键！）

把刚建好的飞书任务**镜像**到 `05_任务清单`，建立"产品/波段/OKR"三向关联，让 OKR 表能反向看到拆解任务（双向关联生效）：

```bash
# tasks-sync.json 示例（一次性 batch）
cat > /tmp/tasks-sync.json << 'EOF'
{
  "fields": ["任务标题","角色","优先级","状态","关联款","所属波段","所属OKR","飞书任务ID"],
  "rows": [
    ["2. 设计稿出图 — 5 款", "设计师", "P1", "待启动",
     [{"id":"<产品rec1>"},{"id":"<产品rec2>"}],
     [{"id":"<波段rec>"}],
     [{"id":"<OKRrec>"}],
     "<飞书 task_guid>"]
  ]
}
EOF

lark-cli base +record-batch-create \
  --base-token <BASE_TOKEN> \
  --table-id tblRnB14n1xW1vou \
  --json @/tmp/tasks-sync.json
```

#### Step 8: 飞书 IM 卡片汇报

读 [`../../../lark-im/SKILL.md`](../../../lark-im/SKILL.md) 学习卡片格式。简化版：

```bash
lark-cli im chats messages create \
  --chat-id "<老板群 chat_id>" \
  --msg-type "interactive" \
  --content '{
    "config":{"wide_screen_mode":true},
    "header":{"title":{"tag":"plain_text","content":"🚀 上新任务已下发"},"template":"green"},
    "elements":[
      {"tag":"div","text":{"tag":"lark_md","content":"**波段：** 2026Q2 早春第一波\n**任务数：** 12\n**周期：** 60 天\n**涉及角色：** 9\n\n详情见 [任务清单](https://my.feishu.cn/base/<APP_TOKEN>?table=tblRnB14n1xW1vou)"}}
    ]
  }'
```

---

### 工作流 B：📋 看团队本月任务

**触发语：** "看本月任务" / "团队总览" / "X 月谁负责什么"

直接打开 `05_任务清单` 表的「本月团队总览」视图（已建好）：

```bash
echo "https://my.feishu.cn/base/<APP_TOKEN>?table=tblRnB14n1xW1vou&view=vewZV6Kcar"
```

或读出来 AI 总结：

```bash
lark-cli base +record-list \
  --base-token <BASE_TOKEN> \
  --table-id tblRnB14n1xW1vou \
  --filter '{"conjunction":"and","conditions":[{"field_name":"截止日期","operator":"isGreaterEqual","value":"<本月1日 ms>"},{"field_name":"截止日期","operator":"isLess","value":"<下月1日 ms>"}]}' \
  --jq '[.data.records[] | {标题:.fields.任务标题, 负责人:.fields.负责人, 截止:.fields.截止日期, 状态:.fields.状态}]'
```

把结果交给 AI 按角色分组 + 写成简报。

---

### 工作流 C：⚠️ 督促超期任务

**触发语：** "谁还没动" / "看下超期任务" / "提醒 X 老师"

#### Step 1: 筛选超期 / 即将超期任务

```bash
NOW_TS=$(date +%s)000
TOMORROW_TS=$(date -d "+1 day" +%s)000

lark-cli base +record-list \
  --base-token <BASE_TOKEN> \
  --table-id tblRnB14n1xW1vou \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"状态","operator":"isNot","value":"已完成"},
    {"field_name":"状态","operator":"isNot","value":"已取消"},
    {"field_name":"截止日期","operator":"isLess","value":"'$TOMORROW_TS'"}
  ]}'
```

#### Step 2: 私聊提醒每个负责人

```bash
for task in <超期任务>; do
  lark-cli im chats messages create \
    --user-id "<负责人 open_id>" \
    --msg-type text \
    --content '{"text":"⚠️ 你负责的任务「'<标题>'」已超期/即将超期，请尽快推进。"}'
done
```

---

## 三、涉及多维表（数据流向）

| 表 | 作用 | 操作 |
|---|---|---|
| `01_产品库` (tblrKzymnPPQ98ZX) | 拿产品 record_id 用于 link | 读 |
| `04_上新波段` (tblnXnsxZN0H0z3P) | 拿波段 + 关联产品列表 | 读 |
| `13_OKR` (tbl0tdusQ2fw98wZ) | 拿 OKR record_id 用于 link | 读 |
| `05_任务清单` (tblRnB14n1xW1vou) | 镜像写入 + 同步状态 | 写 + 读 |

> **关键：** 所有任务**先建到飞书原生任务系统**（task），**再镜像到多维表**。这样既能用飞书任务的提醒/分配能力，又能在多维表里跨字段统计。

---

## 四、权限表

| 操作 | scope |
|---|---|
| 创建任务 | `task:task:write` |
| 分配任务成员 | `task:task:write` |
| 任务提醒 | `task:task:write` |
| 列表/查询任务 | `task:task:read` |
| 多维表读写 | `base:record:create` `base:record:read` |
| 解析用户 | `contact:user:search` |
| 发送 IM 消息 | `im:message:write` |

---

## 五、错误处理

### 限流
飞书任务 API 有限流（每分钟 ~60 次创建）。批量建超过 50 个任务时：
- 每个任务间 sleep 200ms
- 收到 `code=800004135 method limited` 时退避 5 秒重试

### 字段值不匹配
- `select` 字段：value 必须**精确匹配**选项名（区分大小写、空格）
- `link` 字段：value 必须是 `[{"id":"recXXX"}]` 数组格式（不是字符串）
- `datetime` 字段：value 必须是**毫秒时间戳**（不是秒）

### 用户解析失败
- `contact +resolve` 找不到时，agent 应**回退到提示用户**："找不到 X，请提供 open_id 或在角色映射里配置"

---

## 六、典型对话示例

### 例 1：上新一键下发

```
用户：启动 2026Q2 早春第一波 上新

agent：
✓ 找到波段：2026Q2 早春第一波（关联 5 款产品）
✓ 找到 OKR：商品上新（2026Q1）/ 抖音内容（2026Q1）
✓ 按 11 步流程模板生成 12 个任务
✓ 批量建飞书任务...完成（12 个 task_guid）
✓ 分配给 9 个角色...完成
✓ 设置截止前 1 天提醒...完成
✓ 同步到 05_任务清单 多维表...完成

🚀 已下发 12 个任务，预计 6/30 全部交付。
查看：https://my.feishu.cn/base/<APP>?table=05_任务清单&view=本月团队总览
```

### 例 2：超期督促

```
用户：看下谁还没动

agent：
扫描中...
⚠️ 发现 2 个超期任务：
1. 「设计稿出图」— @张三（设计师）已超期 3 天
2. 「打版」— @李四（打版师）今天截止还未启动

已私聊提醒。是否需要我创建升级任务给主管？
```

---

## 七、参考

- [`../../../lark-task/SKILL.md`](../../../lark-task/SKILL.md) — 任务管理详细
- [`../../../lark-base/SKILL.md`](../../../lark-base/SKILL.md) — 多维表操作
- [`../../../lark-im/SKILL.md`](../../../lark-im/SKILL.md) — IM 卡片
- [`../../../lark-contact/SKILL.md`](../../../lark-contact/SKILL.md) — 用户解析
- 主 [`SKILL.md`](../../SKILL.md) — 仓库总览
- [`../../lib/base-schema/tables.json`](../../lib/base-schema/tables.json) — 表字段 schema
