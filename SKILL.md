---
name: lark-fashion-cockpit
version: 0.1.0
description: "女装电商运营驾驶舱 — 给电商品牌主的飞书 CLI 数字化方案。包含 19 大能力（经营/商品/销售/供应链/管理 5 大板块）+ 4 大杀手锏（套娃远程指挥/AI 产品分析/产品关系图/多 CLI 编排）。当用户提到女装/服装/电商运营/上新/库存/选品/竞品/复盘/经营驾驶舱/品牌运营等场景时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli --help"
---

# lark-fashion-cockpit — 女装电商运营驾驶舱

> **🎯 核心定位：** 给做女装的人用的（适用所有服装电商品类，化妆品/家居/食品改改字段也能跑）
>
> **📦 集成深度：** 飞书 CLI 23 个原生 skill 中调用 13 个 + 多 CLI 套娃编排（飞书 CLI + douyin-monitor Python CLI）

## 🚦 路由总览（用户意图 → 子 skill）

读完本路由表，根据用户意图跳到对应的 `skills/<name>/SKILL.md` 读详细工作流。

### 🅰️ 公司经营（4 能力）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "今天怎么样 / 经营异常 / 健康度 / 老板早报" | [`morning-report`](skills/morning-report/SKILL.md) |
| "目标 / 进度 / 完成率 / 缺口 / 季度 / 月度" | [`target-tracking`](skills/target-tracking/SKILL.md) |
| "利润 / 哪些款赚钱 / 投放 ROI / 成本结构" | [`profit-analysis`](skills/profit-analysis/SKILL.md) |
| **"上新任务下发 / 给团队分任务 / 协同跟进"** ⭐ | [`task-collaboration`](skills/task-collaboration/SKILL.md) |

### 🅱️ 商品中心（5 能力）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| **"产品库 / 产品详情 / SKU / AI 产品分析 / 产品关系图"** ⭐ | [`product-library`](skills/product-library/SKILL.md) |
| "上新波段 / 商品企划 / 开发款式 / 上新节奏" | [`new-launch-planning`](skills/new-launch-planning/SKILL.md) |
| "库存 / 补货 / 缺货 / 滞销 / 平台库存分配" | [`stock-replenishment`](skills/stock-replenishment/SKILL.md) |
| "退货原因 / 评价反馈 / 商品反馈" | [`feedback-returns`](skills/feedback-returns/SKILL.md) |
| "竞品 / 爆款 / 趋势 / 同行" | [`competitor-monitor`](skills/competitor-monitor/SKILL.md) |

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

### 🅴 公司管理（4 能力 — 飞书 CLI 增值层）

| 用户意图关键词 | 跳到子 skill |
|---|---|
| "知识库 / SOP / 客服话术 / 培训资料" | [`knowledge-base`](skills/knowledge-base/SKILL.md) |
| **"复盘会 / 周会纪要 / 会议待办 / 自动出报告"** ⭐ | [`meeting-workflow`](skills/meeting-workflow/SKILL.md) |
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
