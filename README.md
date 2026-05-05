# 🚀 lark-fashion-cockpit

> **女装电商运营驾驶舱 Skill** — 给电商品牌主的飞书 CLI 数字化方案
>
> 适用所有服装电商品类，化妆品 / 家居 / 食品改改字段也能跑。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![飞书 CLI 创作者大赛](https://img.shields.io/badge/%E9%A3%9E%E4%B9%A6CLI-%E5%88%9B%E4%BD%9C%E8%80%85%E5%A4%A7%E8%B5%9B-orange)](https://github.com/larksuite/cli)
[![已实测](https://img.shields.io/badge/%E5%B7%B2%E5%AE%9E%E6%B5%8B-%E7%9C%9F%E6%9C%8B%E5%8F%8B%E7%9C%9F%E4%BB%BB%E5%8A%A1%E7%9C%9F%E5%AE%8C%E6%88%90-brightgreen)](./examples/01-real-launch-demo.md)
[![40 sub-skill](https://img.shields.io/badge/sub--skill-40%20%E4%B8%AA%E8%87%AA%E5%8C%85%E5%90%AB-blue)](#-40-个-sub-skill-清单)
[![lark-cli skills](https://img.shields.io/badge/npx%20skills%20add-fxl1209739475--fxl%2Flark--fashion--cockpit-purple)](#-安装与使用)

---

## 📦 安装与使用

**一个仓库 = 一个大 skill 包，包含 40 个独立 self-contained sub-skill。**

### 一键装全部 40 个 skill

```bash
# 1. 装 lark-cli 主程序
npm install -g @larksuite/cli

# 2. 装官方基础 skill
npx skills add larksuite/cli -g -y

# 3. 装本仓库 40 个 sub-skill
npx skills add fxl1209739475-fxl/lark-fashion-cockpit -g -y

# 4. 配置环境变量（拷贝模板填值）
cp .env.example .env
# 然后填 DOUBAO_API_KEY / DEEPSEEK_API_KEY / DOUYIN_COOKIE 等

# 5. 一键初始化飞书 base（建 27 张表 schema + 字段 + mock 演示数据）
python scripts/init-cockpit.py
```

> ⚠️ **重要：装 skill ≠ 自动建表**
>
> Skill 是 SKILL.md 工作流文档（教 AI 用 lark-cli 完成业务的"配方"）。**飞书多维表是数据载体**，需要单独建。
> - **40 个 sub-skill** 装在 `~/.claude/skills/`（步骤 3 完成）
> - **27 张多维表** 需要在你飞书 base 里建（步骤 5 完成）
> - 两者**关系是 N:M**：一个 skill 可能用 0-N 张表，一张表可能被多个 skill 共用

### 两种使用模式

| 模式 | 适用 | 装哪些 |
|---|---|---|
| **🅐 完整应用模式** | 想体验完整女装运营驾驶舱 | 装全部 40 skill + 跑 init-cockpit.py 建 27 张表 + 飞书机器人 |
| **🅑 单 skill 模式** | 只想用某个能力（如 video-script-parser）| 选装单个 skill + 自己已有的飞书表（按 SKILL.md 配 env 变量）|

### 选装单个 skill

```bash
# 只装"视频脚本拆解"
npx skills add fxl1209739475-fxl/lark-fashion-cockpit -s video-script-parser -y -g

# 只装"老板分身"
npx skills add fxl1209739475-fxl/lark-fashion-cockpit -s boss-clone-aily -y -g
```

### 触发方式（自然语言对话 AI agent）

装好 skill 后，在 Claude Code / 飞书机器人 / 任何支持 lark-cli 的 AI agent 里说自然语言：

| 你说 | 自动触发的 sub-skill |
|---|---|
| "今天卖得怎么样" | `morning-report`（晨报）|
| "DRS-0429 配什么款" | `product-matching`（产品搭配）|
| "巡检任务" | `task-lifecycle`（任务生命周期）|
| "拆这个视频 [URL]" | `video-script-parser`（视频拆解）|
| "问老板这款备多少件" | `boss-clone-aily`（老板分身）|
| "看竞品博主" | `competitor-monitor`（对标博主监控）|
| "今日直播总结" | `live-streaming` + `livestream-recap` |

---

## 📋 40 个 sub-skill 清单（按板块分类）

### 🅐 公司经营（4）
- [`morning-report`](skills/morning-report/SKILL.md) — 经营晨报，5 维数据 + AI 综合分析
- [`target-tracking`](skills/target-tracking/SKILL.md) — 目标追踪，OKR + 实时进度
- [`profit-analysis`](skills/profit-analysis/SKILL.md) — 利润分析，单品 + 平台双维拆解
- [`task-collaboration`](skills/task-collaboration/SKILL.md) — 任务协作，跨租户朋友派工

### 🅑 商品中心（9）
- [`product-library`](skills/product-library/SKILL.md) — 产品库，元素标签 32 选项 × 5 维
- [`new-launch-planning`](skills/new-launch-planning/SKILL.md) — 上新企划，波段排期
- [`stock-replenishment`](skills/stock-replenishment/SKILL.md) — 库存补货
- [`feedback-returns`](skills/feedback-returns/SKILL.md) — 退货反馈分析
- [`competitor-monitor`](skills/competitor-monitor/SKILL.md) — 竞品监控
- [`product-matching`](skills/product-matching/SKILL.md) — 产品搭配 ⭐（库存倾斜算法独家）
- [`product-graph`](skills/product-graph/SKILL.md) — 产品关系图（飞书白板渲染）
- [`launch-decision`](skills/launch-decision/SKILL.md) — 新品下单决策（4 维信号 + 教训库）
- [`base-extension-product-matcher`](skills/base-extension-product-matcher/SKILL.md) ⭐ — 多维表格内置 AI 按钮

### 🅒 销售增长（4）
- [`platform-analytics`](skills/platform-analytics/SKILL.md) — 4 平台销售分析
- [`content-pipeline`](skills/content-pipeline/SKILL.md) — 内容创作工作流
- [`live-streaming`](skills/live-streaming/SKILL.md) — 直播管理 + 库存 GMV 匹配
- [`private-domain`](skills/private-domain/SKILL.md) — 私域客户运营

### 🅓 供应链履约（2）
- [`production-supplier`](skills/production-supplier/SKILL.md) — 工厂供应商管理
- [`order-fulfillment`](skills/order-fulfillment/SKILL.md) — 订单履约

### 🅔 公司管理（5）
- [`knowledge-base`](skills/knowledge-base/SKILL.md) — 知识库
- [`meeting-workflow`](skills/meeting-workflow/SKILL.md) — 会议工作流
- [`okr-cascade`](skills/okr-cascade/SKILL.md) — OKR 层级
- [`approval-flow`](skills/approval-flow/SKILL.md) — 审批流
- [`doc-iterator`](skills/doc-iterator/SKILL.md) — 文档迭代

### 🅕 工作流（5）
- [`task-lifecycle`](skills/task-lifecycle/SKILL.md) — 任务生命周期巡检 ⭐
- [`event-router`](skills/event-router/SKILL.md) — 事件路由（飞书 IM 套娃模式）
- [`meeting-broadcaster`](skills/meeting-broadcaster/SKILL.md) — 会议广播
- [`meeting-clip-extractor`](skills/meeting-clip-extractor/SKILL.md) — 会议精彩切片
- [`skill-recommender`](skills/skill-recommender/SKILL.md) — AI 推荐下一步用哪个 skill（自演进）

### 🅖 AI 数字员工（3）⭐ 最新加
- [`boss-clone-aily`](skills/boss-clone-aily/SKILL.md) ⭐ — 老板分身（飞书 Aily 原生）
- [`lingo-fashion-glossary`](skills/lingo-fashion-glossary/SKILL.md) — 女装术语词典 Lingo
- [`helpdesk-customer-tickets`](skills/helpdesk-customer-tickets/SKILL.md) — 客户工单系统

### 🅗 可视化扩展（1）⭐
- [`workplace-block-cockpit`](skills/workplace-block-cockpit/SKILL.md) ⭐ — 工作台首页 cockpit 仪表盘 widget

### 🅘 开源生态雷达（1）⭐ 最新加
- [`opensource-radar`](skills/opensource-radar/SKILL.md) ⭐ — 开源雷达每日扫描 GitHub + AI 评估和女装电商相关度 + 给改造方案 + 知识库归档

### 🅙 视频拆解工具（2）⭐
- [`video-script-parser`](skills/video-script-parser/SKILL.md) ⭐ — 视频脚本拆解（豆包多模态）
- [`blogger-monitor`](skills/blogger-monitor/SKILL.md) ⭐ — 对标博主每日监控

---

## 📜 原创性声明

- **原创**：库存倾斜搭配 / 4 维信号下单 / 任务生命周期大脑 / skill-recommender 自演进 / 产品关系图飞书白板 / 多角色权限矩阵 / 个人成长复盘 + SOP 自沉淀 / 开源雷达 等核心创新由作者独立设计实现
- **致敬开源精神**：飞书 IM 长连接事件订阅模式按 [lark-cli 官方 event 文档](https://github.com/larksuite/cli) 实现；多模态视觉用 [豆包视觉理解 API](https://www.volcengine.com/docs/82379/1553586)；ASR 用 faster-whisper 开源模型
- **官方推荐能力实现**：12+ 飞书原生能力（base / im / event / docs / vc / minutes / wiki / sheets / approval / task / okr / mail）按 lark-cli 官方文档落地
- **mock 数据声明**：8 款产品 / 17 表销售数据均为虚构 mock；3 真朋友任务系统 / 3 真实妙记 / 飞书白板 Wiki 云盘均为真实接通

---

## ✅ 真实数据 vs Mock 透明声明

**真实接通（8 个层）：**
- ✅ 3 真朋友跨租户任务系统（马萍蔓 14 分 41 秒真完成）
- ✅ 3 场真实飞书会议妙记（vc + minutes API 拉 90 章节 AI 摘要）
- ✅ 飞书云盘 11 张真上传文件 + 3 子文件夹
- ✅ 飞书白板真渲染产品关系图（Mermaid → docs +whiteboard-update）
- ✅ 飞书 Wiki 1 空间 + 5 节点真创建
- ✅ 飞书日历 5 个上新事件真写入
- ✅ 18+ 篇飞书云文档真生成（含 5 条 AI 审稿评论）
- ✅ event-listener 真持久化触发记录（trigger-log.jsonl）→ skill-recommender 真读 → 真生成推荐

**Mock 数据（明确声明）：**
- 🟡 8 款女装产品 / 17 表销售/库存/退货等业务数据
- 🟡 4 平台 GMV 数据（淘宝/抖音/小红书/视频号）
- 🟡 客户分层 / 生产档案 / 竞品监控
- 🟡 库存占用金额 / 单品销售数据（如「OUT-2024-OL ¥82,620」等）

> 🔐 **数据隐私声明**：作者真实经营的女装品牌数据涉及商业机密 + 客户隐私 + 工厂供应链信息，**不能在公开仓库泄露**。本仓库所有金额 / SKU / 客户 / 销量数字均为**模拟测试数据**，仅用于演示 cockpit 工作流和算法逻辑。**真实使用时用户自己的飞书 base 数据完全隔离在自己租户内，作者无权访问**。

**Mock 替换路径：** 详见 [`docs/REAL-DATA-ROADMAP.md`](./docs/REAL-DATA-ROADMAP.md) — Phase 1 飞书原生数据已 80% 接通，Phase 2-5 接通真实电商平台 API 路径清晰（5-10 天/平台）。

---

## ⚠️ 已知限制（诚实声明）

为了让评委明确认知作品边界，主动声明以下限制：

### 1. 部分集成是脚本框架，待 scope 授权后真生产可用
- **OKR 双向同步**（`scripts/okr-sync.ps1`）：等待 `okr:okr.period:readonly` 等 scope 授权（1 行命令 + 1 小时跑通，详见 [`docs/OKR-APPROVAL-MIGRATION.md`](./docs/OKR-APPROVAL-MIGRATION.md)）
- **飞书原生审批接通**（`scripts/approval-router.ps1`）：当前基于 `14_审批` mock 表运行，接通飞书原生审批流需要后台配置 4 个审批模板 + 30 分钟

### 2. 多事件并发 daemon 部署
- `event-watcher.py` 多线程订阅 3 类事件，**生产部署需要常驻进程托管**（Windows 任务计划 / Linux systemd）
- 当前演示是模拟模式 + 单事件源真实启动验证

### 3. 通用性边界
- 业务规则（元素标签 5 维 / 互补品类 / 11 步上新流程）女装专属
- **架构层 100% 通用**，跨行业迁移指南详见 [`docs/INDUSTRY-ADAPT.md`](./docs/INDUSTRY-ADAPT.md)
- 化妆品 / 男装 / 童装 1-2 天可适配；家居 / 食品 3-5 天

### 4. 跨租户能力受飞书平台限制
- 跨租户 P2P IM 不支持（错误 230038）→ 改用飞书原生任务通知（已绕过）
- 跨租户用户不能拉同一群（错误 232033）→ 解决方案见 [`examples/04-im-card-best-practice.md`](./examples/04-im-card-best-practice.md)

### 5. 视觉生成能力
- 当前产品图为 PIL 占位卡（颜色 + 品类 + 价格）
- 真实 AI 模特上身图需接入虚拟试穿 API（OOTDiffusion 本地 / 阿里 OutfitAnyone / 快手 Kolors-VTON）
- 接入路线：1 天写脚本 + 1 张 ¥1 元成本

---

## 🎬 一句话价值

> **老板娘手机飞书一句话「启动 5 月连衣裙波段上新」 → agent 后台 30 秒搞定 12 任务下发到 9 个角色 + 仪表盘自动联动 + 群里弹卡片汇报。**
>
> **离开电脑回去休息。**

---

## 📖 为什么做这个

我做过**莫千衣**、**一支探戈**等多个女装项目。最痛的不是设计款式，是**每天早上的运营对账**：

| 痛点 | 时间成本 | 影响 |
|---|---|---|
| 切 4 个平台后台抄销售数据 | 每天 1 小时 | 决策滞后 1 天 |
| 库存盲区，售罄才知道 | 每周丢 5-10 单 | ¥几千-几万损失 |
| 上新流程靠微信群喊 | 漏单率 30% | 团队心里没数 |
| 复盘会不落地行动项 | 100% 都忘 | 改进不了 |
| 选品靠"感觉" | — | 滞销库存堆积 |
| OKR 拆解不下去 | — | 目标空转 |

所以我做了 `lark-fashion-cockpit`：把上面这些痛点全部用飞书 CLI + AI 编排成**自动化工作流**。**老板娘手机一句话，agent 在飞书里干活。**

> **设计哲学：** 让女装老板娘**离开电脑回去休息**。

---

## ✅ 已实测：真朋友真任务真完成

> **2026-05-03 实测：作者用本 Skill 真给 3 个真朋友（跨租户外部联系人）下发任务。马萍蔓 14 分 41 秒后真点了完成，作者飞书群弹完成卡片。**

| 测试 | 时间 | 结果 |
|---|---|---|
| 上新一键下发 | 20:32 | ✅ 12 任务真分配，3 朋友手机响 |
| 真朋友点完成 | 20:47 | ✅ 老板群自动弹绿色完成卡片 |
| AI 产品分析 | 20:55 | ✅ 6 秒生成飞书报告 + 跳转按钮 |
| 库存预警联动 | 21:10 | ✅ 自动给生产主管建紧急补货任务 |

详见 [examples/](./examples/) 4 个真实演示日志。

---

## 🎯 核心能力（40 大 + 4 杀手锏 + 自演进 meta-skill）

### 5 大业务板块

| 板块 | 能力数 | 涵盖 |
|---|---|---|
| 🅰️ **公司经营** | 4 | 经营晨报 / 目标进度 / 利润分析 / **跨部门任务协同** ⭐ / **任务生命周期大脑** ⭐ / **飞书 IM 套娃自然语言路由** 🔥 / **skill-recommender 自演进 meta-skill** 🔥（独家）|
| 🅱️ **商品中心** | 9 | **产品库 + 8 维详情** ⭐ / 上新企划 / 库存补货 / 退货反馈 / 竞品监控 / **产品搭配（库存倾斜清老货）** ⭐ / **新品下单判断（4 维信号）** ⭐ / **产品关系图（飞书白板真实化）** 🔥 |
| 🅲 **销售增长** | 4 | 4 平台数据 / **内容 5 阶段流转** ⭐ / 营销直播 / 私域 + 服务 |
| 🅳 **供应链履约** | 2 | 生产 + 供应商 / 订单 + 物流 |
| 🅴 **公司管理** | 4 | 知识库 / **复盘会工作流** ⭐ / OKR / 审批流 |

### 4 大杀手锏

1. **🔥 飞书套娃远程指挥** — 老板手机飞书发消息 → agent 自动调用全部能力（基于 lark-event WebSocket 长连接 + 自然语言意图识别 + 角色权限矩阵）
2. **🤖 AI 产品分析助手** — 自然语言问"找出售罄率<50%的春夏款排序" → AI 读多维表 → 生成飞书文档 → 群里弹卡片含按钮
3. **🕸️ 产品关系图** — 飞书白板自动生成"产品×SKU×内容×投流×直播×素材×元素"全维度关系图
4. **🔗 多 CLI 套娃编排** — 飞书 CLI + douyin-monitor Python CLI + 即梦 CLI + ffmpeg 串联

---

## 🚀 三种使用方式

### 🟢 路径 1：完全零代码（推荐普通老板娘）

打开 [飞书 CLI Web](https://github.com/jingsongliujing/Feishu-CLI-Web)（参赛同期作品）→ 登录飞书 → 直接对 AI 说：
```
帮我安装 lark-fashion-cockpit
初始化系统
```

然后日常用：
```
今天店铺经营怎么样？
启动 4 月连衣裙波段上新
看下哪些款要补货
找出春夏款里售罄率不到 50% 的
整理上周复盘会
```

### 🟡 路径 2：装国产 agent（5 分钟）

```bash
# 1. 装扣子 / Trae / 爱马仕（任选）
# 2. 装飞书 CLI
npm install -g @larksuite/cli

# 3. 对 agent 说
"安装 lark-fashion-cockpit Skill"
"初始化系统"
```

### 🔴 路径 3：开发者向（Claude code / Codex）

```bash
git clone https://github.com/fxl1209739475-fxl/lark-fashion-cockpit.git ~/.claude/skills/lark-fashion-cockpit
```

详见 [`SKILL.md`](SKILL.md) 主路由 + [`SKILL.md#初始化流程`](SKILL.md#-初始化流程一键搭建整套数据中枢)（10 步搭建完整数据中枢）。

---

## 🎬 演示场景（4 个已实测）

### 1️⃣ 上新一键下发（最炸场）

```
你说：启动 2026Q2 早春第二波 上新

agent 跑：
- 读 04_上新波段 找波段 + 关联 3 款
- 读 13_OKR 找当前周期 OKR
- 按 11 步流程模板拆解 12 任务
- 调 lark-cli task +create + +assign 真分配给 9 角色
- 同步到 05_任务清单（产品/波段/OKR 三向关联）
- 飞书 IM 卡片汇报老板群

结果：30 秒。9 个角色手机响。多维表多 12 条带关联。
```

**👉 详见 [examples/01-real-launch-demo.md](./examples/01-real-launch-demo.md)**

### 2️⃣ AI 产品分析（杀手锏 1）

```
你说：找出春夏款里售罄率不到 50% 的，按销量排序，哪些该清仓

agent 跑：6 秒
- AI 解析自然语言 → 结构化 query
- 调 lark-cli base 拉数据
- 算售罄率 + 智能识别"开发中款不是滞销"
- 生成飞书文档（含表格 + 6 项可勾选行动）
- 群里弹蓝色卡片 + 跳转按钮

结果：找到清仓候选 1 款（OUT-2024-OL，库存占用 ¥82,620），含 AI 推荐 3 步策略。
```

**👉 详见 [examples/02-ai-analysis-demo.md](./examples/02-ai-analysis-demo.md)**

### 3️⃣ 库存预警 + skill 间联动

```
你说：看下哪些款要补货

agent 跑：12 秒
- stock-replenishment skill 扫产品库
- 找到 SKT-0328-A 库存 5 件，0.4 天后售罄
- AI 算补货量 410 件 + 平台分配
- 自动调 task-collaboration 给生产主管申丽媛建紧急任务
- 群里弹红色紧急卡片 + 跳转按钮

结果：申丽媛飞书任务图标响。老板群弹红色告警。决策已被执行。
```

**👉 详见 [examples/03-stock-alert-demo.md](./examples/03-stock-alert-demo.md)**

### 4️⃣ 真朋友点完成 → 老板自动收到通知

```
朋友马萍蔓在自己飞书 App 点了"完成"

agent 检测到 task status = done
↓ 自动给老板群发完成通知卡片：

✅ 任务完成通知
马萍蔓 完成了「2026Q3 早秋第一波 5 款设计稿」
耗时：14 分 41 秒
🚀 AI 推荐下一步：通知打版师可以接手了
```

**这个闭环 30 个对手作品里 0 个人能演示。**

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│  入口：手机飞书 IM / agent CLI / 飞书 CLI Web           │
│         ↓                                               │
│  飞书 CLI 套娃（lark-cli event +subscribe 长连接）      │
│         ↓                                               │
│  多 CLI 编排：飞书 CLI + douyin-monitor + ffmpeg + ...  │
│         ↓                                               │
│  数据中枢：飞书多维表（27 张表）+ 文档 + 任务 + 日历    │
│         ↓                                               │
│  输出：IM 卡片 / 飞书文档 / 飞书白板 / 飞书任务         │
└─────────────────────────────────────────────────────────┘
```

### 集成的 12 大类飞书 CLI 原生能力

`base` / `doc` / `im` / `task` / `event` / `calendar` / `whiteboard` / `drive` / `sheets` / `wiki` / `vc` + `minutes` / `okr` / `approval`

### 数据中枢（一键搭建后用户飞书会有）

- 1 个多维表 App「lark-fashion-cockpit 数据中枢」
- 27 张业务表（产品库 / 4 平台销售 / 任务 / 选题 / 文案 / 直播 / 生产 / 客户 / 退货 / 竞品 / OKR / 审批 / 市场内容 / 竞品产品 / 等）
- 300+ 字段（含 8 个跨表 link、1 个 OKR↔任务双向关联）
- 4 个任务清单视图（本月团队总览 / 我的待办 / 按状态看板 / 截止日历）
- 1 个经营总览仪表盘（4 指标卡 + 1 饼图 + 1 环形 + 2 柱状）
- 1 个独人通知群（解决 P2P self 无推送问题）

---

## 💼 商业化路径

不只是参赛工具 — 这套 cockpit 是给**所有女装/电商品牌主**的飞书 CLI 数字化解决方案，可对外承接咨询服务：

| 客户类型 | 用法 | 报价参考 |
|---|---|---|
| 个人 / 小品牌主 | 自助 fork 使用，可改字段适配自家 | 免费（开源）|
| 中小品牌（年营收 < 1000 万）| 付费定制（角色映射、字段调整、SOP 接入）| ¥5,000-10,000 / 单 |
| MCN / 连锁品牌 | 年度服务（迭代 + 培训 + 二次开发）| ¥2-5 万 / 年 |
| 服饰行业培训机构 | 把 Skill 当案例教学 | 课程合作 |

**核心价值** — 替代品牌主一堆 SaaS（库存系统 / 任务系统 / CRM / BI / 客服工单），用飞书原生能力搭出"我的女装 AI 公司"。

---

## 📂 仓库结构

```
lark-fashion-cockpit/
├── SKILL.md                     # 主入口（路由总览 + 完整初始化 10 步）
├── README.md                    # 你正在看的
├── LICENSE
├── skills/                      # 40 个 sub-skill（self-contained）
│   ├── ⭐ task-collaboration/   # 上新一键下发
│   ├── ⭐ product-library/      # 8 维详情 + AI 分析 + 关系图
│   ├── ⭐ content-pipeline/     # 内容 5 阶段流转
│   ├── ⭐ meeting-workflow/     # 复盘会自动出纪要
│   ├── ⭐ morning-report/       # 经营晨报
│   └── ...（共 40 个）
├── lib/
│   ├── base-schema/             # 字段定义 + 视图 + 仪表盘 schema
│   ├── mock-data/               # 130 条演示数据
│   ├── prompts/                 # AI 提示词模板
│   └── team-config.json         # 团队角色 + 通知群配置
├── docs/                        # 设计文档
└── examples/                    # 真实演示日志
    ├── 01-real-launch-demo.md   # 上新一键下发
    ├── 02-ai-analysis-demo.md   # AI 产品分析
    ├── 03-stock-alert-demo.md   # 库存预警 + skill 联动
    └── 04-im-card-best-practice.md  # IM 卡片 4 坑沉淀
```

---

## 🎓 真实踩坑沉淀

本仓库已固化 4 个飞书 CLI v2 API 的实测限制 + 解法：

| 坑 | 解法 |
|---|---|
| `task +create --assignee` 静默不生效 | 分两步：`+create` 拿 guid → `+assign --add` |
| 跨租户 P2P IM 禁止（错 230038）| 走飞书原生任务通道（不受跨租户限制）|
| P2P self 无推送 | 建独人群替代 |
| markdown 链接不可点击 | 用 interactive 卡片 + button 元素 |

**详见 [examples/04-im-card-best-practice.md](./examples/04-im-card-best-practice.md)。** 后续 fork 本仓库做其他垂直行业（化妆品 / 家居 / 食品）的开发者直接受益，省 2 小时调试。

---

## ❓ 常见问题（FAQ）

### Q1：装完 skill 后机器人就能用了吗？
**A**：不能。还需要 3 步：① 配凭证（.env）② 跑 init-cockpit.py 建表 ③ 启动 event-listener.py 让机器人监听消息。

### Q2：必须装全部 40 个 skill 吗？
**A**：不必须。两种用法：① 完整应用模式（装全部）② 单 skill 模式（`npx skills add ...-s 单个 skill`，只用你需要的能力）。

### Q3：跑 cockpit 需要哪些 API key？
**A**：核心 3 个 — DOUBAO_API_KEY（豆包视觉，火山方舟免费 50w tokens）/ DEEPSEEK_API_KEY（DeepSeek 文本分析）/ DOUYIN_COOKIE（抖音爬数据，浏览器复制）。其他可选：可灵 / 阿里万相 / 阿里 ASR。

### Q4：飞书 CLI 机器人怎么 24 小时跑？
**A**：开机自启 `python scripts/event-listener.py` + `python skills/auto-scheduler/scripts/cockpit-scheduler.py`。Windows 用 Task Scheduler "At log on"，Linux 用 systemd。

### Q5：为啥多维表是 27 张但 sub-skill 是 40 个？
**A**：N:M 关系。一张表可能被多个 skill 共用（05_任务清单 同时被 task-tracker / task-lifecycle / task-collaboration / personal-mirror 4 个 skill 用）；一个 skill 也可能用 0 张表（lingo-fashion-glossary 用飞书词典不用 base）。

### Q6：跨租户能用吗？
**A**：群聊跨租户可以（已实测 3 朋友真任务真完成）。P2P 私聊跨租户飞书原生不支持。建议同租户员工用 P2P，跨租户朋友进共享群。

### Q7：mock 数据怎么换成真实数据？
**A**：详见 [`docs/REAL-DATA-ROADMAP.md`](./docs/REAL-DATA-ROADMAP.md)。Phase 1 飞书原生数据已 80% 接通，Phase 2 接抖音/淘宝/视频号 API 5-10 天/平台。

### Q8：装了之后我电脑会不会被一直占用？
**A**：event-listener + auto-scheduler 是常驻进程，CPU 占用 < 1%，内存 ~150MB。可后台跑/最小化窗口。但**不要关那个 PowerShell 黑窗口**，关了 = 机器人挂了。

### Q9：可以在 Linux/Mac 跑吗？
**A**：可以。本仓库脚本主要针对 Windows（PowerShell + Python），Mac/Linux 把 `.ps1` 改成 `.sh` 等价即可。Python 脚本完全跨平台。

### Q10：能给同行老板娘做这种系统吗？
**A**：能。复刻同套架构 1-2 天搭建即可。垂直行业（女装/男装/家居/食品/培训机构等）按客单 3000-5000 元/单是合理报价区间。本仓库就是你给同行做生意的工具包。

---

## 🤝 贡献

```bash
# 1. Fork 仓库
# 2. 做你的女装行业改造（或别的行业适配）
git checkout -b feat/your-skill
# 3. 在 skills/ 下加你的 sub-skill 文件夹
# 4. 提 PR，我会合入主仓库挂名感谢
```

---

## 📜 许可

[MIT License](./LICENSE) — 欢迎 fork / 改造 / 用于其他垂直行业。

---

## 🙏 致谢

- **飞书 CLI 团队** — 开源整个生态
- **飞书 CLI 创作者大赛社区** — 开源精神 + 公开技术分享
- **马萍蔓 / 申丽媛 / 朱健豪** — 配合实测，让真朋友真任务真完成成为可能 ❤️

---

## 📮 联系

- 作者：冯兴龙
- 仓库：[fxl1209739475-fxl/lark-fashion-cockpit](https://github.com/fxl1209739475-fxl/lark-fashion-cockpit)
- 反馈：[GitHub Issues](https://github.com/fxl1209739475-fxl/lark-fashion-cockpit/issues)

---

> **🏆 飞书 CLI 创作者大赛参赛作品** — 2026 年 4-5 月
>
> **目标**：最佳实践奖（Mac mini）— 评选标准"将 Skill 和业务结合，带来业务增效"完美对口本 Skill
