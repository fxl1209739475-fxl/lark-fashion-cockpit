---
name: lark-fashion-cockpit-event-router
version: 1.0.0
description: "飞书 IM 套娃路由 — 老板手机飞书消息触发 agent 自动跑 skill。借鉴 4/1 直播来新璐分享的 Larkchannel 思路，做女装垂直行业的事件驱动版本。当用户说「在飞书里直接指挥」「手机上派活」「不打开电脑也能跑」时使用。属于 lark-fashion-cockpit 公司经营板块（第 23 个能力，杀手锏 1 的实现）。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
  cliHelp: "lark-cli event --help"
---

# 飞书 IM 套娃路由 — 离开电脑回去休息

> **🎯 老板娘真实痛点：** "半年来一直想迁移到飞书，因为这样我就可以离开电脑回去休息" — 来新璐原话。

> **🚀 解决：** 飞书 IM 消息流 → lark-event WebSocket 长连接 → agent 实时路由 → 自动跑 skill → 卡片回复。**老板娘咖啡店、火车上、洗手间里都能指挥 lark-fashion-cockpit。**

> **板块：** 🅰 公司经营（第 23 个能力 = 杀手锏 1「飞书套娃远程指挥」的工程实现）  
> **思路来源：** 借鉴 4/1 飞书 CLI 实战直播来新璐分享的 Larkchannel 开源思路（已注明感谢）  
> **30 对手作品里：** 只有来新璐 + 我们做了这个套娃模式

---

## 一、核心架构

```
老板手机飞书 IM 输入「巡检任务」
        ↓
lark-event WebSocket 长连接（已在 lark-cli daemon 跑）
        ↓
event-listener.py 收到 im.message.receive_v1
        ↓
路由匹配（5 关键词模式）
        ↓
执行对应 skill 脚本（task-tracker.ps1 / launch-decision.ps1 / ...）
        ↓
lark-cli im 发卡片回复
        ↓
老板手机收到卡片（飞书原生推送，5 秒内）
```

**整个链路：用户输入 → 卡片回复，平均 < 30 秒。**

---

## 二、5 条路由规则

| 关键词模式 | 路由到 | 演示 |
|---|---|---|
| `巡检任务` / `看下任务` / `任务追踪` / `逾期` | task-tracker.ps1 | 24 任务巡检，识别 2 逾期+1 紧急 |
| `任务复盘` / `为什么.*延期` / `按时率` | task-retrospective.ps1 | 按时率 87.5% + 反哺教训 |
| `配什么好` / `搭配推荐` / `主图穿搭` | product-matching-demo.ps1 | DRS+KNT 60 分推荐 |
| `新品.*多少件` / `下单建议` / `翻单` / `备货建议` | launch-decision.ps1 | DRS-2026-RM 352 件 |
| `利润` / `哪些款赚钱` / `净利率` | profit-analysis.ps1 | 视频号净利率 43% |

**未来扩展：** 增加新 skill 时只需在 `event-listener.py` 的 `ROUTES` 加一行。

---

## 三、安全机制

```python
# 只响应老板，避免死循环
if event['sender_id'] != BOSS_OPEN_ID:
    return  # 忽略其他人 / bot 自己的消息

# 防止重复触发
if event['event_id'] in seen_events:
    return  # 飞书可能重发
seen_events.add(event['event_id'])
```

---

## 四、前置条件

```bash
# 1. lark-cli 已认证 + 启用了 bot 身份
lark-cli auth login --as bot --scope "im:message.p2p_msg:readonly im:message:write"

# 2. 飞书开发者后台开启 im.message.receive_v1 事件订阅
# https://open.feishu.cn/app → 选你的应用 → 事件与回调

# 3. lark-cli event daemon 已启动（首次 consume 会自动启）
lark-cli event status
```

---

## 五、运行方式

### 方式 A：模拟模式（本地测路由 logic）

```bash
python scripts/event-listener.py --simulate "巡检任务"
# 输出：路由到 ⏰ 任务巡检 (task-tracker.ps1)

python scripts/event-listener.py --simulate "DRS 配什么好"
# 输出：路由到 🛍 产品搭配推荐
```

### 方式 B：真跑（生产模式）

```bash
# 前台跑（开终端 Ctrl+C 退出）
python scripts/event-listener.py

# 后台跑（推荐生产部署）
start /b python scripts/event-listener.py > listener.log 2>&1

# 然后老板从飞书 App 发"巡检任务"，agent 30 秒内回卡片
```

### 方式 C：cron 持续监听（生产部署）

```bash
# Windows 任务计划：开机自动启动 listener
# Linux: nohup python event-listener.py &
```

---

## 六、典型对话（套娃实战）

```
老板娘咖啡店里掏出手机
       ↓
飞书 IM 给「🚀 lark-fashion-cockpit 助手」群发：「巡检任务」
       ↓
3 秒后：agent 回 turquoise 卡片「🤖 收到 → 正在跑 ⏰ 任务巡检」
       ↓
20 秒后：agent 回 red 卡片「⏰ 任务生命周期巡检报告」
   • 24 任务全扫描
   • 🔴 逾期 2 项已升级
   • 🟠 紧急 1 项 < 24h
   • 已自动 ping 内容编辑朱健豪
       ↓
老板娘点卡片"📋 查 05_任务清单"按钮直接跳进多维表
       ↓
老板娘：「这款 DRS-2026-RM 下多少件？」
       ↓
agent 跑 launch-decision → 紫色卡片回复「352 件 / S25M40 / 备 1.4 倍」
       ↓
老板娘喝完咖啡，5 个决策搞定，电脑没碰过。
```

---

## 七、与其他 skill 的关系

```
event-router 是入口
   ├ 命中"巡检" → 调 task-lifecycle / task-tracker
   ├ 命中"搭配" → 调 product-matching
   ├ 命中"下单" → 调 launch-decision
   ├ 命中"利润" → 调 profit-analysis
   ├ 命中"复盘" → 调 task-lifecycle
   └ 命中"晨报" → 调 morning-report
```

**所有 22 个 sub-skill 都可以通过本路由触发。**

---

## 八、为什么是杀手锏 ⭐⭐⭐⭐⭐

| 维度 | 评估 |
|---|---|
| **创新性** | 30 对手只有来新璐做了同模式，我们是第 2 个 |
| **通用性** | 任何垂直行业都能套此架构（消息→agent→工具）|
| **商业价值** | 老板娘从"开电脑跑"变"飞书消息指挥"—— 真实 ROI |
| **工程深度** | 200+ 行 Python + lark-event WebSocket + 5 路由规则 |
| **演讲冲击力** | 30 秒视频镜头：飞书消息发出 → 卡片回来 → 评委秒懂 |

---

## 九、参考

- [`../../../lark-event/SKILL.md`](../../../lark-event/SKILL.md) — 飞书事件订阅原生 skill
- [`../task-lifecycle/SKILL.md`](../task-lifecycle/SKILL.md) — 被路由的目标 #1
- [`../product-matching/SKILL.md`](../product-matching/SKILL.md) — 被路由目标 #2
- [`../launch-decision/SKILL.md`](../launch-decision/SKILL.md) — 被路由目标 #3
- 4/1 飞书 CLI 实战直播 来新璐 Larkchannel 演示（妙记 token: obcnrz7a5ad1yu71n73u44r3）
