---
name: lark-fashion-cockpit-meeting-workflow
version: 1.0.0
description: "经营复盘会工作流 — 自动整理飞书会议纪要 → AI 提取行动项 → 自动建任务给负责人 → 飞书周报文档。当用户说「整理上周会议」「这周复盘会的待办」「会议纪要变任务」「自动周报」时使用。属于 lark-fashion-cockpit 公司管理板块。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli vc --help"
---

# 经营复盘会工作流 — 妙记 → 任务 → 周报

> **🏆 这是 4/13 飞书 CLI 直播评委（张咋啦/Zara）亲自夸过的核心场景。** 整合 vc + minutes + workflow-meeting-summary + task 4 个原生 skill，把"开完会忘记落地"这个痛点根除。

> **板块：** 🅴 公司管理  
> **调用 lark-cli skill：** `vc` + `minutes` + `workflow-meeting-summary` + `task` + `doc` + `base`  
> **多维表依赖：** `05_任务清单`（写）/ `13_OKR`（关联）

---

## 一、前置条件

```bash
lark-cli auth login --scope "vc:meeting.search:read vc:note:read minutes:minutes:readonly minutes:minutes.artifacts:read minutes:minutes.transcript:export task:task:write base:record:create docs:document:write_only drive:drive.metadata:readonly"
```

读 [`../../../lark-vc/SKILL.md`](../../../lark-vc/SKILL.md) + [`../../../lark-minutes/SKILL.md`](../../../lark-minutes/SKILL.md) + [`../../../lark-workflow-meeting-summary/SKILL.md`](../../../lark-workflow-meeting-summary/SKILL.md)。

---

## 二、工作流（4 步链式）

```
触发：用户说"整理上周复盘会"
        ↓
Step 1: lark-cli vc +search 找本周/上周会议
        ↓
Step 2: lark-cli vc +notes 拿到妙记的 doc_token + AI 总结
        ↓
Step 3: AI 解析行动项 + 推断负责人
        ↓
Step 4: lark-cli task +create + +assign 批量建任务给负责人
        ↓
Step 5: lark-cli base +record-batch-create 同步到 05_任务清单
        ↓
Step 6: lark-cli docs +create 写飞书周报文档（含会议链接 + 任务列表）
```

---

### Step 1: 搜索会议

```bash
# 上周
START=$(date -d 'last monday' +%Y-%m-%d)
END=$(date +%Y-%m-%d)

lark-cli vc +search \
  --start "$START" \
  --end "$END" \
  --format json --page-size 30 \
  --jq '[.data.events[] | {meeting_id:.id, title:.summary, start:.start_time, attendees:.attendees}]'
```

筛选含"复盘"/"周会"/"经营"等关键词的会议。

### Step 2: 拿到妙记 + AI 总结

```bash
# 拿 minute_token + note_doc_token
lark-cli vc +notes --meeting-ids "<id1>,<id2>,<id3>" \
  --jq '[.data.notes[] | {meeting:.meeting_id, minute_token:.minute_token, note_doc:.note_doc_token, verbatim_doc:.verbatim_doc_token}]'

# 拉妙记 AI 总结（含待办、章节）
lark-cli docs +fetch --doc <note_doc_token> --api-version v2 --format pretty
```

### Step 3: AI 提取行动项

把妙记 AI 总结里的"待办"章节 + 逐字稿（如有）喂给 LLM：

```
你是一个会议纪要 → 任务转换器。从下面的会议纪要提取所有行动项，输出结构化 JSON：

【会议主题】{title}
【参会人】{attendees}
【纪要正文】{notes}

输出 JSON：
{
  "actions": [
    {
      "title": "行动项简明描述",
      "owner_name": "推断的负责人姓名",
      "owner_clue": "推断依据（如纪要原话）",
      "deadline_relative": "本周五 / 7 天内 / 月底前",
      "priority": "P0/P1/P2",
      "related_topic": "对应的项目/产品/选题"
    }
  ]
}

推断负责人规则：
1. 如果纪要里明确指派（"@张三 负责..."），直接用
2. 如果说"我会去做..."，从发言人记录推断
3. 都不明确 → owner_name 留空，输出"待补"
```

### Step 4: 批量建任务

```bash
for action in <actions>; do
  # 解析负责人
  if [ -n "$owner_name" ]; then
    OWNER_OPENID=$(lark-cli contact +resolve --query "$owner_name" --jq '.data.users[0].open_id')
  fi
  
  # 建任务
  TASK_GUID=$(lark-cli task +create \
    --summary "$title" \
    --description "来自会议《$meeting_title》$start_time\n上下文：$owner_clue" \
    --due "$deadline_ms" \
    --priority "$priority" \
    --jq '.data.task.guid')
  
  # 分配
  if [ -n "$OWNER_OPENID" ]; then
    lark-cli task +assign --task-guid "$TASK_GUID" --user-id "$OWNER_OPENID"
  fi
  
  # 提醒
  lark-cli task +reminder --task-guid "$TASK_GUID" --relative-fire-minute 1440
done
```

### Step 5: 同步多维表

```bash
# 同时写入 05_任务清单（含来源会议字段）
lark-cli base +record-batch-create \
  --base-token <APP> --table-id tblRnB14n1xW1vou \
  --json @./tasks-from-meeting.json
```

### Step 6: 写飞书周报

```bash
lark-cli docs +create --api-version v2 --content '<title>📋 上周复盘会汇总 (2026-04-28 ~ 05-03)</title>
<callout emoji="📊"><p>共 N 场会议，提取 M 个行动项，已分配 K 人</p></callout>
<h1>会议清单</h1>
<ul>
<li><a href="<spc_link>">5/2 周一晨会</a> — N 个行动项</li>
<li><a href="<spc_link>">5/2 商品月会</a> — N 个行动项</li>
</ul>
<h1>行动项总览（按负责人分组）</h1>
<h2>@张三（设计师）</h2>
<checkbox done="false">5 款设计稿（来自 5/2 商品月会，截止 5/9）</checkbox>
<h2>@李四（生产主管）</h2>
<checkbox done="false">跟工厂确认打样进度（来自 5/2 周一晨会，截止 5/4）</checkbox>
<h1>本周关键决策</h1>
<ul><li>...</li></ul>'
```

---

## 三、典型对话示例

```
用户：整理一下上周的复盘会

agent：
✓ 搜索 4/28-5/3 会议：3 场（周一晨会 / 商品月会 / 内容碰头会）
✓ 拉取妙记 AI 总结：3 份
✓ 提取行动项：12 个
  - 已自动推断负责人：10 个
  - 待补充负责人：2 个 ⚠️
✓ 批量建飞书任务 → 同步多维表 → 周报文档

📋 周报：https://my.feishu.cn/docx/<id>
✅ 12 个任务已分配
⚠️ 2 个待补充负责人，请确认：
  - 「品牌升级方案 v2」会议没明确指派
  - 「客服话术库审核」候选 张三 / 李四 / 王五

要继续指派吗？
```

---

## 四、与其他 skill 协作

- 跟 `task-collaboration` 共用任务模板和分配逻辑
- 跟 `morning-report` 共用：晨报里"昨日待办进度"读这里建的任务
- 跟 `okr-cascade` 关联：会议提取的行动项可以挂在某个 OKR 下

---

## 五、参考

- [`../../../lark-vc/SKILL.md`](../../../lark-vc/SKILL.md) — 会议查询 + 妙记
- [`../../../lark-minutes/SKILL.md`](../../../lark-minutes/SKILL.md) — 妙记基础信息
- [`../../../lark-workflow-meeting-summary/SKILL.md`](../../../lark-workflow-meeting-summary/SKILL.md) — 会议纪要工作流模板
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md) — 任务下发能力
