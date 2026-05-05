---
name: lark-fashion-cockpit
version: 1.0.0
description: "女装电商运营驾驶舱 — 给电商品牌主的飞书 CLI 数字化方案。包含 38 大能力（经营/商品/销售/供应链/管理 5 大板块）+ 飞书 CLI 12 个深度集成 + 14 个独家创新（自演进/精准传达/评论迭代/经验沉淀/双级审批/智能反哺/客观贡献度/妙记自动剪辑/货盘梳理/直播话术分析/虚拟试穿/直播日报/库存 GMV 智能匹配/浏览器自动抓数据）。覆盖经营全流程+组织学习闭环+文档协作闭环+多模态视频/试穿+直播自动化抓数据。当用户提到女装/电商运营/搭配推荐/新品下单/任务追踪/手机指挥/AI 自演进/上传下达/根据评论改文档/经验沉淀/员工贡献度/剪个高光视频/会议金句剪辑/货盘梳理/直播话术分析/虚拟试穿/产品上身/今日直播总结/库存 GMV/浏览器自动抓数据/抖音视频号小红书自动化/初始化系统等场景时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli --help"
---

# lark-fashion-cockpit — 女装电商运营驾驶舱

> **🎯 核心定位：** 给做女装的人用的（适用所有服装电商品类，化妆品/家居/食品改改字段也能跑）
>
> **📦 集成深度：** 飞书 CLI 23 个原生 skill 中调用 13 个 + 多 CLI 套娃编排（飞书 CLI + douyin-monitor Python CLI）
>
> **🚀 一键搭建：** 用户首次说「初始化 / 帮我搭建系统 / 装这个 Skill」时，跳到下方 [初始化流程](#-初始化流程一键搭建整套数据中枢) 章节。

## 🚦 路由总览（用户意图 → 子 skill）

读完本路由表，根据用户意图跳到对应的 `skills/<name>/SKILL.md` 读详细工作流。

### 🅰️ 公司经营（7 能力，含 1 个 meta-skill）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "今天怎么样 / 经营异常 / 健康度 / 老板早报" | [`morning-report`](skills/morning-report/SKILL.md) |
| "目标 / 进度 / 完成率 / 缺口 / 季度 / 月度" | [`target-tracking`](skills/target-tracking/SKILL.md) |
| "利润 / 哪些款赚钱 / 投放 ROI / 成本结构" | [`profit-analysis`](skills/profit-analysis/SKILL.md) |
| **"上新任务下发 / 给团队分任务 / 协同跟进"** ⭐ | [`task-collaboration`](skills/task-collaboration/SKILL.md) |
| **"巡检任务 / 看下逾期 / 任务追踪 / 任务复盘 / 为啥老延期"** ⭐ | [`task-lifecycle`](skills/task-lifecycle/SKILL.md) |
| **"飞书消息触发 / 手机指挥 / 离开电脑跑 skill / 套娃模式"** 🔥 | [`event-router`](skills/event-router/SKILL.md) |
| **"AI 推荐 skills / 自演进 / 把高频操作固化"** 🔥 | [`skill-recommender`](scripts/skill-recommender.ps1) |
| **"AI 审稿 / 设计稿评论 / 自动找改进点"** | scripts/design-review-comments |
| **"审批分流 / 自动批 / 大额升级老板"** | scripts/approval-router.ps1 |
| **"agent 越用越懂我 / 长期记忆 / 自动学习"** | scripts/memory-evolve.ps1 |
| **"会议总结分发 / 按岗位定制纪要 / 让员工不懵 / 上传下达"** 🔥 | [`meeting-broadcaster`](skills/meeting-broadcaster/SKILL.md) |

### 🅱️ 商品中心（8 能力）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| **"产品库 / 产品详情 / SKU / AI 产品分析 / 产品关系图"** ⭐ | [`product-library`](skills/product-library/SKILL.md) |
| "上新波段 / 商品企划 / 开发款式 / 上新节奏" | [`new-launch-planning`](skills/new-launch-planning/SKILL.md) |
| "库存 / 补货 / 缺货 / 滞销 / 平台库存分配" | [`stock-replenishment`](skills/stock-replenishment/SKILL.md) |
| "退货原因 / 评价反馈 / 商品反馈" | [`feedback-returns`](skills/feedback-returns/SKILL.md) |
| "竞品 / 爆款 / 趋势 / 同行" | [`competitor-monitor`](skills/competitor-monitor/SKILL.md) |
| **"XX 配什么好 / 搭配推荐 / 主图穿搭 / 直播搭配 / 老库存清仓"** ⭐ | [`product-matching`](skills/product-matching/SKILL.md) |
| **"产品关系图 / 画产品全景 / 白板生成 / 全维度图"** 🔥 | [`product-graph`](skills/product-graph/SKILL.md) |
| **"新品下多少件 / 备货建议 / 翻单决策 / 尺码颜色占比 / 面料备多少"** ⭐ | [`launch-decision`](skills/launch-decision/SKILL.md) |

### 🅲 销售增长（4 能力）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "销售数据 / 4 平台对比 / 销售趋势" | [`platform-analytics`](skills/platform-analytics/SKILL.md) |
| **"选题 / 文案 / 内容创作 / 拍摄 / 剪辑 / 发布 5 阶段"** ⭐ | [`content-pipeline`](skills/content-pipeline/SKILL.md) |
| "直播 / 主播 / 排期 / 活动 / 投放 ROI" | [`live-streaming`](skills/live-streaming/SKILL.md) |
| "私域 / 会员 / 客户分层 / 客服" | [`private-domain`](skills/private-domain/SKILL.md) |

### 🅳 供应链履约（2 能力）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "生产 / 供应商 / 工厂 / 打样 / 交期" | [`production-supplier`](skills/production-supplier/SKILL.md) |
| "订单 / 发货 / 物流 / 履约异常" | [`order-fulfillment`](skills/order-fulfillment/SKILL.md) |

### 🅴 公司管理（11 能力 — 飞书 CLI 增值层 + 组织学习闭环 + 视频剪辑）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "知识库 / SOP / 客服话术 / 培训资料" | [`knowledge-base`](skills/knowledge-base/SKILL.md) |
| **"复盘会 / 周会纪要 / 会议待办 / 自动出报告"** ⭐ | [`meeting-workflow`](skills/meeting-workflow/SKILL.md) |
| **"会议总结分发 / 按岗位定制纪要 / 上传下达不损耗"** 🔥 | [`meeting-broadcaster`](skills/meeting-broadcaster/SKILL.md) |
| **"根据评论改文档 / 整合评论意见 / 文档 V2 / 评论合并"** 🔥 | [`doc-iterator`](skills/doc-iterator/SKILL.md) |
| **"提交经验 / 失败教训 / 改进建议 / 经验沉淀"** 🔥 | scripts/experience-capture.ps1 |
| **"经验审批 / 知识库归档 / 复用部门"** 🔥 | scripts/experience-approval.ps1 |
| **"AI 反哺 / 别人犯过吗 / 有人用过吗 / 找谁请教"** 🔥 | scripts/knowledge-feedback.ps1 |
| **"员工贡献度 / 客观评估 / 奖金参考 / 年终述职"** 🔥 | scripts/contribution-tracker.ps1 |
| **"剪个高光视频 / 妙记自动剪辑 / 会议金句 / 自动加字幕"** 🔥 | [`meeting-clip-extractor`](skills/meeting-clip-extractor/SKILL.md) |
| **"货盘梳理 / 选品 / 冲销售/清库存/测款/提利润"** 🔥 | scripts/merchandise-curation.ps1 |
| **"直播话术分析 / 主播评分 / 5 维度复盘"** 🔥 | scripts/livestream-script-analyzer.ps1 |
| **"虚拟试穿 / 模特换装 / 产品上身预览"** 🔥 | scripts/virtual-tryon-mock.py |
| **"今日直播总结 / 直播日报 / 早晚场对比"** 🔥 | scripts/livestream-daily-report.ps1 |
| **"库存 GMV / 库存款销售 / 库存消化"** 🔥 | scripts/inventory-gmv-matcher.ps1 |
| **"浏览器自动抓数据 / 直播平台自动化 / 抖音视频号小红书爬数据"** 🔥 | scripts/livestream-scraper.py |
| **"抓直播 / 拉直播数据 / 自动抓数据"** 🔥 | scripts/livestream-fetch-by-record.ps1 |
| "OKR / 目标拆解 / 部门指标" | [`okr-cascade`](skills/okr-cascade/SKILL.md) |
| "审批 / 预算 / 采购单 / 退货特批" | [`approval-flow`](skills/approval-flow/SKILL.md) |

## 🔥 4 大杀手锏（贯穿全局，不单独成 skill）

| 杀手锏 | 描述 | 在哪用 |
|---|---|---|
| **1. 飞书套娃远程指挥** | event 长连接订阅，老板手机一句话 → agent 调全部 skill | 全局入口（参考 `examples/larkchannel-pattern.md`）|
| **2. AI 产品分析助手** | 自然语言问业务问题 → 读多维表 → 生成飞书文档 | 嵌入 `product-library` |
| **3. 产品关系图** | whiteboard 自动生成"产品×SKU×内容×投流×直播×素材×元素"图 | 嵌入 `product-library` |
| **4. 多 CLI 套娃编排** | 飞书 CLI + douyin-monitor Python CLI + 即梦 CLI + ffmpeg 串联 | 架构层 |

## 📊 数据中枢：14 张飞书多维表

详见 [`lib/base-schema/README.md`](lib/base-schema/README.md)。所有 19 能力共享同一个飞书多维表 App。

| # | 表名 | 服务能力 |
|---|---|---|
| 1 | 产品库 | 5, 7, 14 |
| 2 | 4 平台销售 | 1, 2, 10 |
| 3 | 库存预警 | 7 |
| 4 | 上新波段 | 4, 6 |
| 5 | 任务清单 | 4, 6, 11, 14 |
| 6 | 选题池 | 9, 11 |
| 7 | 文案库 | 11 |
| 8 | 直播排期 | 12 |
| 9 | 生产档案 | 14 |
| 10 | 客户分层 | 13 |
| 11 | 退货反馈 | 8 |
| 12 | 竞品库 | 9 |
| 13 | OKR | 18 |
| 14 | 审批记录 | 19 |

## 🧑‍🤝‍🧑 9 个角色 + 10 步上新流程

任务下发的标准模板（`task-collaboration` 用）：

```
选款 → 设计稿 → 打版 → 打样 → 生产 → 摄影 → 详情页 → 种草内容 → 直播预热 → 上架投流 → 客服培训
```

| 角色 | 负责步骤 |
|---|---|
| 设计师 | 设计稿 |
| 打版师 | 打版 / 打样 |
| 生产主管 ⭐ | 跟工厂 / 进度 / 交期 |
| 摄影师 | 产品图 + 模特图 |
| 模特 | 拍摄配合 |
| 运营 | 详情页 / 上架 / 投流 |
| 内容编辑 | 种草视频 / 图文 |
| 主播 ⭐ | 直播预热 / 直播讲解 |
| 客服 | 话术更新 / 团队培训 |

## 🚀 安装与使用

### 路径 1：完全零代码（推荐普通老板娘）
打开 [飞书 CLI Web](https://github.com/jingsongliujing/Feishu-CLI-Web)（参赛同期作品） → 登录飞书 → 输入 "帮我安装 lark-fashion-cockpit" → 输入 "看下今天卖得怎么样" → 完事

### 路径 2：装国产 agent（5 分钟）
1. 装扣子 / Trae / 爱马仕（任意）
2. 复制安装飞书 CLI：`npm install -g @larksuite/cli`
3. 对 agent 说："安装 lark-fashion-cockpit Skill"
4. 用自然语言指挥

### 路径 3：开发者向（Claude code / Codex）
```bash
git clone https://github.com/fxl1209739475-fxl/lark-fashion-cockpit.git
# 复制到 ~/.claude/skills/ 或 ~/.codex/skills/
```

## 🚀 初始化流程（一键搭建整套数据中枢）

> **当用户首次说「初始化 / 帮我搭建系统 / 装这个 Skill」时，按本章 9 步执行。**
> 完成后用户飞书账号下会有：1 个多维表 App / 16 张表 / 118 字段 / 4 视图 / 1 仪表盘 8 图表 / 1 个独人通知群 / 1 份团队配置。

### Step 0：检查授权 scope

执行任何动作前确认用户已授权：

```bash
lark-cli auth login --scope "base:app:create base:table:create base:table:delete base:field:create base:record:create base:record:read base:dashboard:create base:view:read im:chat:create_by_user im:message.send_as_user task:task:write task:task:read contact:user:search docs:document:write_only"
```

如果有 missing_scope 错误，让用户跑上面命令补授权。

### Step 1：建多维表 App

```bash
lark-cli base +base-create \
  --name "lark-fashion-cockpit 数据中枢" \
  --time-zone "Asia/Shanghai" \
  --jq '.data.base.base_token'
```

记录返回的 `base_token`（后续每个命令都要用），写入用户 `~/.lark-fashion-cockpit/config.json`：

```json
{"base_token": "xxxxx", "init_at": "2026-05-XX"}
```

### Step 2：批量建 16 张表

按以下顺序循环 `base +table-create --base-token <token> --name <name>`：

```
01_产品库 / 02_4平台销售 / 03_库存预警 / 04_上新波段 / 05_任务清单 / 06_选题池 / 07_文案库 / 08_直播排期 / 09_生产档案 / 10_客户分层 / 11_退货反馈 / 12_竞品博主库 / 13_OKR / 14_审批记录 / 15_市场内容监控 / 16_竞品产品监控
```

每张表保存返回的 `table_id` 到 config.json 的 `tables` 字典里。

> ⚠️ 飞书有限流：每分钟约 60 次创建。建议每个 table 后 `sleep 0.5` 秒。

### Step 3：删除默认占位表

`base +base-create` 会自动建一张默认表「数据表」。需手动删除：

```bash
lark-cli base +table-list --base-token <token>  # 找 name="数据表" 的 id
lark-cli base +table-delete --base-token <token> --table-id <默认表id> --yes
```

### Step 4：批量建 118 字段

读 `lib/base-schema/fields/*.json`（69 个普通字段 + 11 个主字段 + 7 个 link 字段，文件名前缀为表序号）：

```bash
for json_file in lib/base-schema/fields/*.json; do
  table_name=$(basename "$json_file" | cut -d'-' -f1)  # 如 "01"
  table_id=$(jq -r ".tables[\"$table_name\"]" config.json)
  
  lark-cli base +field-create \
    --base-token "$base_token" \
    --table-id "$table_id" \
    --json "@$json_file"
  sleep 0.4
done
```

> ⚠️ **关键坑（实测踩过）：**
> 1. JSON 文件**必须是 UTF-8 无 BOM**（PowerShell 默认带 BOM 会报错 `invalid character 'ï'`）
> 2. select 字段的 hue 只能用枚举值：`Red / Orange / Yellow / Lime / Green / Turquoise / Wathet / Blue / Carmine / Purple / Gray`（不要用 Cyan / Pink，会报错）
> 3. link 字段不能传 `multiple` 字段，会报 `Unrecognized key 'multiple'`

### Step 5：建 link 双向关联（关键）

最重要的一条：05_任务清单.所属OKR ↔ 13_OKR.拆解任务 双向关联

```json
{
  "name": "所属OKR",
  "type": "link",
  "link_table": "<13_OKR table_id>",
  "bidirectional": true,
  "bidirectional_link_field_name": "拆解任务"
}
```

这一步建好后，OKR 表里会自动出现"拆解任务"反向字段，13 个 OKR 跟踪靠它。

### Step 6：建任务清单 4 个视图

```bash
for view in "本月团队总览" "我的待办" "按状态看板" "截止日历"; do
  lark-cli base +view-create \
    --base-token "$base_token" \
    --table-id "<05_任务清单 id>" \
    --json "{\"name\":\"$view\",\"type\":\"grid\"}"
done
```

> 视图的筛选/分组/排序需要单独调 `+view-set-filter` / `+view-set-sort` 等。本 Skill 推荐用户在飞书 GUI 直接配置（5 分钟搞定，比 API 简单）。

### Step 7：建经营总览仪表盘

```bash
DASH_ID=$(lark-cli base +dashboard-create \
  --base-token "$base_token" \
  --name "🎯 经营总览" \
  --jq '.data.dashboard.dashboard_id')
```

然后批量建 8 个 block（4 指标卡 + 1 饼图 + 1 环形 + 2 柱状）：

读 `lib/base-schema/dashboard/block-*.json`，循环：
```bash
lark-cli base +dashboard-block-create \
  --base-token "$base_token" \
  --dashboard-id "$DASH_ID" \
  --type "<type>" \
  --name "<name>" \
  --data-config "@<block 文件>"
```

最后自动布局：
```bash
lark-cli base +dashboard-arrange --base-token "$base_token" --dashboard-id "$DASH_ID"
```

### Step 8：建独人通知群（解决 P2P self 无推送的坑）

```bash
NOTIFY_CHAT_ID=$(lark-cli im +chat-create \
  --as user --type private \
  --name "🚀 lark-fashion-cockpit 助手" \
  --description "lark-fashion-cockpit Skill 自动通知：上新/库存/AI分析/晨报" \
  --jq '.data.chat_id')
```

> ⚠️ **关键坑（实测踩过）：**
> 1. 给 user-id 自己发消息 API 返回 ok 但飞书 UI 不弹推送
> 2. 跨租户外部联系人不能拉到群（错 232033），所以独人群只能含本人
> 3. 解决方案：建独人群后所有通知发到群里，飞书会原生推送（小红点+角标+锁屏）

### Step 9：写入团队配置

```json
// ~/.lark-fashion-cockpit/team-config.json
{
  "boss": {"name": "<姓名>", "open_id": "<self open_id>"},
  "notification_chat": {"chat_id": "<step 8 返回>"},
  "team_members": {
    "设计师": {"name": "", "open_id": ""},
    "打版师": {"name": "", "open_id": ""},
    "生产主管": {"name": "", "open_id": ""},
    "摄影师": {"name": "", "open_id": ""},
    "模特": {"name": "", "open_id": ""},
    "运营": {"name": "", "open_id": ""},
    "内容编辑": {"name": "", "open_id": ""},
    "主播": {"name": "", "open_id": ""},
    "客服": {"name": "", "open_id": ""}
  },
  "tables": {/* 16 张表 id 字典 */},
  "dashboard_id": "<step 7 返回>"
}
```

引导用户：
```
你的 9 个团队角色对应谁？需要的话告诉我每个角色的姓名，
我用 contact +search-user 找到 open_id 自动填进配置。
未配置的角色，分配任务时会提示用户补全。
```

### Step 10：跑一次「初始化校验」

```bash
# 1. 列所有表确认 16 张
lark-cli base +table-list --base-token "$base_token"

# 2. 试发一条 IM 卡片到通知群
lark-cli im +messages-send --as user --chat-id "$NOTIFY_CHAT_ID" \
  --markdown "🎉 lark-fashion-cockpit 初始化完成！16 张表 + 1 仪表盘 + 1 通知群已就位。"
```

老板在飞书群收到这条消息 = **初始化成功**。

---

## 🎬 初始化完成后的 6 个推荐首次操作

让 agent 引导用户：

```
✅ 初始化完成！现在你可以试这些（都是自然语言一句话）：

1. "新增第一款产品 [款名]" → 启动产品库
2. "录入今天 4 平台销售数据" → 录销售
3. "企划 Q3 早秋第一波，5 款" → 启动上新流程
4. "找出某条件的产品" → AI 产品分析
5. "看下哪些款要补货" → 库存预警
6. "今天店里怎么样" → 经营晨报

对应的子 skill 见上方「路由总览」。
```

## 💡 设计哲学

> **"AI 的能力 = 它使用的工具 + 上下文"** — 归藏（飞书 CLI 创作者大赛 4/1 直播）

- **上下文**：飞书生态（聊天/会议/文档/多维表/日历/任务/OKR/审批）= 电商品牌主的运营全部数据
- **工具**：13 个 lark-cli skill + douyin-monitor Python CLI
- **目标**：让女装老板娘**离开电脑回去休息**，手机一句话搞定经营

## 📜 许可

MIT License — 欢迎 fork / 改造 / 用于其他垂直行业（化妆品/家居/食品）

## 🙏 致谢

- 飞书 CLI 团队（开源整个生态）
- 4 月 1 日直播嘉宾：张咋啦、AJ、归藏、来新璐
- 来新璐 [Larkchannel](https://github.com/sharelab) — 套娃模式启发
