# lark-fashion-cockpit

> **女装电商运营驾驶舱 Skill** — 给电商品牌主的飞书 CLI 数字化方案
>
> 适用所有服装电商品类，化妆品/家居/食品改改字段也能跑。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![飞书 CLI 创作者大赛](https://img.shields.io/badge/%E9%A3%9E%E4%B9%A6CLI-%E5%88%9B%E4%BD%9C%E8%80%85%E5%A4%A7%E8%B5%9B-orange)](https://github.com/larksuite/cli)

---

## 📖 为什么做这个

我做过**品牌一**、**品牌二**等多个女装项目。最痛的不是设计款式，是**每天早上的运营对账**：

- ❌ 切 4 个平台后台（淘宝/抖音/小红书/视频号）抄数据，1 小时
- ❌ 库存盲区，等到客户问"还有货吗"才查，已经卖断
- ❌ 上新流程靠微信群喊话，谁做到哪步老板心里没数
- ❌ 周一开复盘会，开完忘记落地谁负责
- ❌ 选品看哪款成爆款，靠"感觉"没数据
- ❌ 想做 OKR 拆到部门，落地不下去

所以我做了 `lark-fashion-cockpit`：把上面这些痛点全部用飞书 CLI + AI 编排成自动化工作流。**老板娘手机一句话，agent 在飞书里干活。**

> **设计哲学：** 让女装老板娘**离开电脑回去休息**。

---

## 🎯 核心能力（19 大 + 4 杀手锏）

### 5 大业务板块

| 板块 | 能力数 | 涵盖 |
|---|---|---|
| 🅰️ 公司经营 | 4 | 经营晨报 / 目标进度 / 利润分析 / **跨部门任务协同** ⭐ |
| 🅱️ 商品中心 | 5 | **产品库+8维详情** ⭐ / 上新企划 / 库存补货 / 退货反馈 / 竞品监控 |
| 🅲 销售增长 | 4 | 4 平台数据 / **内容 5 阶段流转** ⭐ / 营销直播 / 私域+服务 |
| 🅳 供应链履约 | 2 | 生产+供应商 / 订单+物流 |
| 🅴 公司管理 | 4 | 知识库 / **复盘会工作流** ⭐ / OKR / 审批流 |

### 4 大杀手锏

1. **🔥 飞书套娃远程指挥** — 老板手机飞书发消息 → agent 调用全部能力（基于 lark-event WebSocket 长连接，灵感来自 [Larkchannel](https://github.com/sharelab)）
2. **🤖 AI 产品分析助手** — 自然语言问"找出售罄率<50%的春夏款排序" → AI 读多维表 → 生成飞书文档
3. **🕸️ 产品关系图** — 飞书白板自动生成"产品×SKU×内容×投流×直播×素材×元素"全维度关系图
4. **🔗 多 CLI 套娃编排** — 飞书 CLI + douyin-monitor Python CLI + 即梦 CLI + ffmpeg 串联

---

## 🚀 三种使用方式

### 🟢 路径 1：完全零代码（推荐普通老板娘）

打开 **飞书 CLI Web**（参赛同期作品）→ 登录飞书 → 直接对 AI 说：
```
帮我安装 lark-fashion-cockpit
```
然后日常用：
```
今天店铺经营怎么样？
启动 4 月连衣裙波段上新
看下哪些款要补货
```

### 🟡 路径 2：装国产 agent（5 分钟）

```bash
# 1. 装扣子 / Trae / 爱马仕（任选）
# 2. 装飞书 CLI
npm install -g @larksuite/cli

# 3. 对 agent 说
"安装 lark-fashion-cockpit Skill"
```

### 🔴 路径 3：开发者向（Claude code / Codex）

```bash
git clone https://github.com/fxl1209739475-fxl/lark-fashion-cockpit.git ~/.claude/skills/lark-fashion-cockpit
```

详见 [`SKILL.md`](SKILL.md)。

---

## 📂 仓库结构

```
lark-fashion-cockpit/
├── SKILL.md                    # 主入口（路由总览）
├── README.md                   # 你正在看的这个
├── skills/                     # 19 个子 skill
│   ├── morning-report/         # 经营晨报
│   ├── task-collaboration/     # ⭐ 上新任务一键下发
│   ├── product-library/        # ⭐ 8 维详情 + AI 分析 + 关系图
│   ├── content-pipeline/       # ⭐ 内容 5 阶段流转
│   ├── meeting-workflow/       # ⭐ 复盘会工作流
│   └── ...（共 19 个）
├── lib/
│   ├── base-schema/            # 14 张多维表 schema
│   ├── mock-data/              # 演示数据（品牌一/品牌二）
│   └── prompts/                # AI 提示词模板
├── docs/                       # 设计文档
└── examples/                   # 演示场景
```

---

## 🎬 演示场景（30 秒看懂效果）

```
👨 老板娘（手机飞书）："启动 4 月连衣裙波段上新"
        ↓
🤖 agent：分析当前波段计划，需要 5 款连衣裙
        ↓
🤖 agent：基于上新流程模板拆解 9 个角色 × 11 个步骤 = 35 个任务
        ↓
🤖 agent：批量创建飞书任务 + 自动分配给设计师/打版师/生产主管/摄影师/...
        ↓
🤖 agent：发飞书 IM 卡片汇报："已下发 35 个任务，预计 4/28 全部交付"
        ↓
👨 团队成员：飞书任务通知响起，开始干活
        ↓
👨 老板娘："谁还没动？"
        ↓
🤖 agent：3 个任务超期未启动 → 私聊提醒
```

---

## 💼 商业化路径

参考 4/1 直播 [李祥瑞老师案例](https://bytedance.larkoffice.com/docx/HWgKdWfeSoDw36xu7EYctBrUnsg)（"彩虹少儿美术"教务系统 3000-5000 元/单）：

- ✅ **个人/小品牌主**：免费开源，自助使用
- ✅ **中小品牌（年营收 < 1000 万）**：付费定制（5000-10000 元/单）
- ✅ **MCN/连锁品牌**：年度服务（2-5 万 / 年）

> 不只是参赛工具，还能开个咨询业务。

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
│  数据中枢：飞书多维表（14 张表）+ 文档 + 任务 + 日历   │
│         ↓                                               │
│  输出：IM 卡片 / 飞书文档 / 飞书白板 / 飞书任务         │
└─────────────────────────────────────────────────────────┘
```

**集成的 13 个飞书 CLI 原生 skill：**
base / doc / im / task / event / calendar / whiteboard / drive / sheets / wiki / vc + minutes / okr / approval

---

## 📜 许可

[MIT License](LICENSE) — 欢迎 fork / 改造 / 用于其他垂直行业。

---

## 🙏 致谢

- **飞书 CLI 团队** — 开源整个生态
- **4/1 直播嘉宾**：张咋啦（Zara）/ AJ / 归藏 / 来新璐 — 思路启发
- **来新璐 Larkchannel** — 套娃模式直接抄作业
- **4/20 优秀案例**：Larkrachel / wanna to do / commit-and-record-Lark / 飞书 CLI Web / Lark Group Sentinel — 设计灵感

---

## 📮 联系

- 作者：冯兴龙
- 抖音：[搜"AI 电商博主"]
- 反馈：[GitHub Issues](https://github.com/fxl1209739475-fxl/lark-fashion-cockpit/issues)

---

> **🏆 飞书 CLI 创作者大赛参赛作品** — 2026 年 4-5 月
