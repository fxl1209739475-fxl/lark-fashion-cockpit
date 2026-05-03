# 🚀 lark-fashion-cockpit

> **女装电商运营驾驶舱 Skill** — 给电商品牌主的飞书 CLI 数字化方案
>
> 适用所有服装电商品类，化妆品 / 家居 / 食品改改字段也能跑。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![飞书 CLI 创作者大赛](https://img.shields.io/badge/%E9%A3%9E%E4%B9%A6CLI-%E5%88%9B%E4%BD%9C%E8%80%85%E5%A4%A7%E8%B5%9B-orange)](https://github.com/larksuite/cli)
[![已实测](https://img.shields.io/badge/%E5%B7%B2%E5%AE%9E%E6%B5%8B-%E7%9C%9F%E6%9C%8B%E5%8F%8B%E7%9C%9F%E4%BB%BB%E5%8A%A1%E7%9C%9F%E5%AE%8C%E6%88%90-brightgreen)](./examples/01-real-launch-demo.md)
[![19 大能力](https://img.shields.io/badge/%E8%83%BD%E5%8A%9B-19%20%E5%A4%A7%2B4%20%E6%9D%80%E6%89%8B%E9%94%8F-blue)](#-核心能力19-大--4-杀手锏)
[![13 个 lark-cli skill](https://img.shields.io/badge/lark--cli%20skill-13/23%20%E9%9B%86%E6%88%90-purple)](#-技术架构)

---

## 🎬 一句话价值

> **老板娘手机飞书一句话「启动 5 月连衣裙波段上新」 → agent 后台 30 秒搞定 12 任务下发到 9 个角色 + 仪表盘自动联动 + 群里弹卡片汇报。**
>
> **离开电脑回去休息。**

---

## 📖 为什么做这个

我做过**品牌一**、**品牌二**等多个女装项目。最痛的不是设计款式，是**每天早上的运营对账**：

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

## 🎯 核心能力（19 大 + 4 杀手锏）

### 5 大业务板块

| 板块 | 能力数 | 涵盖 |
|---|---|---|
| 🅰️ **公司经营** | 4 | 经营晨报 / 目标进度 / 利润分析 / **跨部门任务协同** ⭐ |
| 🅱️ **商品中心** | 5 | **产品库 + 8 维详情** ⭐ / 上新企划 / 库存补货 / 退货反馈 / 竞品监控 |
| 🅲 **销售增长** | 4 | 4 平台数据 / **内容 5 阶段流转** ⭐ / 营销直播 / 私域 + 服务 |
| 🅳 **供应链履约** | 2 | 生产 + 供应商 / 订单 + 物流 |
| 🅴 **公司管理** | 4 | 知识库 / **复盘会工作流** ⭐ / OKR / 审批流 |

### 4 大杀手锏

1. **🔥 飞书套娃远程指挥** — 老板手机飞书发消息 → agent 调用全部能力（基于 lark-event WebSocket 长连接，灵感来自来新璐 [Larkchannel](https://github.com/sharelab)）
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
│  数据中枢：飞书多维表（16 张表）+ 文档 + 任务 + 日历    │
│         ↓                                               │
│  输出：IM 卡片 / 飞书文档 / 飞书白板 / 飞书任务         │
└─────────────────────────────────────────────────────────┘
```

### 集成的 13 个飞书 CLI 原生 skill

`base` / `doc` / `im` / `task` / `event` / `calendar` / `whiteboard` / `drive` / `sheets` / `wiki` / `vc` + `minutes` / `okr` / `approval`

### 数据中枢（一键搭建后用户飞书会有）

- 1 个多维表 App「lark-fashion-cockpit 数据中枢」
- 16 张业务表（产品库 / 4 平台销售 / 任务 / 选题 / 文案 / 直播 / 生产 / 客户 / 退货 / 竞品 / OKR / 审批 / 市场内容 / 竞品产品 / 等）
- 118 字段（含 8 个跨表 link、1 个 OKR↔任务双向关联）
- 4 个任务清单视图（本月团队总览 / 我的待办 / 按状态看板 / 截止日历）
- 1 个经营总览仪表盘（4 指标卡 + 1 饼图 + 1 环形 + 2 柱状）
- 1 个独人通知群（解决 P2P self 无推送问题）

---

## 💼 商业化路径（参考 4/1 直播李祥瑞模式）

直播里李祥瑞老师用飞书 CLI 给"彩虹少儿美术"搭多维表教务系统，**报价 3000-5000 元/单**。本 Skill 同样可对外承接咨询：

| 客户类型 | 用法 | 报价参考 |
|---|---|---|
| 个人 / 小品牌主 | 自助 fork 使用，可改字段适配自家 | 免费（开源）|
| 中小品牌（年营收 < 1000 万）| 付费定制（角色映射、字段调整、SOP 接入）| ¥5,000-10,000 / 单 |
| MCN / 连锁品牌 | 年度服务（迭代 + 培训 + 二次开发）| ¥2-5 万 / 年 |
| 服饰行业培训机构 | 把 Skill 当案例教学 | 课程合作 |

**不只是参赛工具，还能开个咨询业务。**

---

## 📂 仓库结构

```
lark-fashion-cockpit/
├── SKILL.md                     # 主入口（路由总览 + 完整初始化 10 步）
├── README.md                    # 你正在看的
├── LICENSE
├── skills/                      # 19 个子 skill
│   ├── ⭐ task-collaboration/   # 上新一键下发
│   ├── ⭐ product-library/      # 8 维详情 + AI 分析 + 关系图
│   ├── ⭐ content-pipeline/     # 内容 5 阶段流转
│   ├── ⭐ meeting-workflow/     # 复盘会自动出纪要
│   ├── ⭐ morning-report/       # 经营晨报
│   └── ...（共 19 个）
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

## 📜 许可

[MIT License](./LICENSE) — 欢迎 fork / 改造 / 用于其他垂直行业。

---

## 🙏 致谢

- **飞书 CLI 团队** — 开源整个生态
- **4 月直播嘉宾**：张咋啦（Zara）/ AJ / 归藏 / 来新璐 — 思路启发
- **来新璐 [Larkchannel](https://github.com/sharelab)** — 套娃模式直接抄作业
- **4/20 优秀案例分享**：Larkrachel / wanna to do / commit-and-record-Lark / 飞书 CLI Web / Lark Group Sentinel — 设计灵感
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
