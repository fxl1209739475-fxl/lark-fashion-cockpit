---
name: lark-fashion-cockpit-cross-platform-im-agent
version: 1.0.0
description: "跨平台 IM 智能体 — 飞书做指挥中心，统一调度 飞书 / 企业微信 / 个人微信 三条 IM 链路。当用户说「跨平台通知」「统一指挥三个微信」「老板娘要在飞书指挥所有沟通」时使用。这是一个综合 skill，下挂 wechat-monitor / wecom-bridge / 飞书原生能力。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    skills: ["wechat-monitor", "wecom-bridge"]
---

# 跨平台 IM 智能体 · 飞书一句话指挥三条沟通链路

> **🎯 老板娘的痛点：**
> - 飞书：内部团队（设计师、生产、运营）→ 已有
> - **企业微信**：B 端供应商、客户 → 0 风险，合规
> - **个人微信**：朋友、家人、未迁移到企微的供应商 → 需要兜底方案
>
> 三个 IM 工具，三套操作习惯，三个未读队列。**老板娘飞书一句话 → cockpit 自动指挥三条链路。**

---

## 一、三条链路一图说清

```
              飞书（指挥中心）
                   ↑
                   │ 老板娘飞书发指令 / event-listener 路由
                   │
              cockpit 智能体
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   ┌──────┐  ┌──────────┐  ┌──────────┐
   │ 飞书  │  │ 企业微信  │  │ 个人微信  │
   │ 自有  │  │  API     │  │  半自动   │
   │  ✅  │  │ (合规)   │  │ (兜底)    │
   └──────┘  └──────────┘  └──────────┘
       │           │           │
       │           │           ├─ scan-wechat ✅ 主窗口扫红点
       │           │           ├─ summarize-image ✅ 长图 → AI
       │           │           ├─ summarize-export ✅ 导出文件 → AI
       │           │           └─ scan-person ⚠️ 桌面 RPA（实验性）
       │           │
       │           ├─ wecom-client ✅ access_token
       │           ├─ list-customers ✅ 列客户
       │           ├─ send-msg ✅ 发消息（48h 窗口/群发模板）
       │           └─ sync-history 🟡 spec（需会话存档）
       │
       └─ lark-cli + 现有 cockpit skills（早报/任务/库存/...）
```

---

## 二、典型组合场景

### 场景 A：早 8:00 跨平台情报早报

```
auto-scheduler 触发 morning-report
  ↓
并行：
  ├─ 飞书：拉昨日团队群 @我 + 待办（lark-im + lark-task）
  ├─ 企微：拉昨日核心客户消息（wecom-bridge → sync-history）
  └─ 个微：扫主窗口红点（wechat-monitor → scan-wechat）
  ↓
DEEPSEEK 三路情报合并 → 一张早报卡片
```

### 场景 B：飞书一句话通知全平台

```
飞书发: 通知所有合作方 5/15 上新延期 1 周

→ event-listener 路由
→ 三路并发：
  ├─ 飞书：发到内部团队群 + @相关人
  ├─ 企微：群发 8 个企微客户（每客户每月 ≤ 4 条）
  └─ 个微：scan-wechat 已加白名单的 5 个朋友型供应商，半自动通知（用户最后确认发送）
→ 飞书发汇报卡："已通知 X 飞书 + Y 企微 + Z 个微"
```

### 场景 C：老板娘要看"过去 24h 所有重要消息"

```
飞书发: 扫所有渠道 24h

→ 三路并发拉摘要：
  ├─ 飞书：lark-im 拉 @我 + 群 @我
  ├─ 企微：sync-history 拉 5 个核心客户
  └─ 个微：用户 30 秒手动飞书滚动截屏 4 个核心群 → summarize-image AI 总结
→ 一张大卡片汇总三路重要消息
```

---

## 三、决策矩阵：消息发到哪条链路？

| 对方在哪 | 用什么 | 为什么 |
|---|---|---|
| 内部员工 | 飞书 | 已有，最稳 |
| 跨租户朋友 | 飞书原生任务/审批/日历（cockpit 已实现）| 不能直接 P2P IM |
| **企微客户**（已加你企微） | **wecom-bridge** | 0 风险，合规，可挂 cron |
| **个人微信好友 / 家人** | **wechat-monitor 半自动**（飞书滚动截屏 → AI）| 兜底，不强求 |
| **批量供应商**（未在企微） | 引导他们扫码加企微 → 切换到 wecom-bridge | 一次性社交迁移成本 |

---

## 四、event-listener 路由示例

```python
# scripts/event-listener.py 中

# 跨渠道扫描
CROSS_SCAN_RE = re.compile(r"^扫所有渠道(?:\s+(\d+)h?)?$")
m = CROSS_SCAN_RE.match(text)
if m:
    hours = int(m.group(1) or 24)
    # 并发调三个 skill
    threading.Thread(target=lambda: subprocess.run(
        ["python", "skills/wechat-monitor/scripts/scan-wechat.py", "--keywords", ""])).start()
    threading.Thread(target=lambda: subprocess.run(
        ["python", "skills/wecom-bridge/scripts/sync-history.py", "--hours", str(hours)])).start()
    # 飞书侧用 lark-cli 直接拉
    ...

# 跨渠道通知
CROSS_NOTIFY_RE = re.compile(r"^通知所有合作方\s+(.+)$")
# ... 类似逻辑
```

---

## 五、与已有 cockpit skill 的关系

本 skill 是**总控**，不重复实现已有能力，而是编排：

| 已有 skill | 本 skill 怎么用 |
|---|---|
| `wechat-monitor` | 个人微信侧能力（截图 / 长图 AI / 导出 AI / 扫红点） |
| `wecom-bridge` | 企业微信侧能力（API 拉历史/发消息）|
| `lark-im` | 飞书内部消息收发 |
| `task-collaboration` | 跨租户任务（朋友通知走飞书任务）|
| `morning-report` | 早报集成本 skill 的"扫所有渠道"产物 |
| `auto-scheduler` | 调度本 skill 跑定时跨渠道扫描 |

---

## 六、为什么这个设计有竞争力

跟"只能控制飞书"或"只能控制微信"的单一智能体相比：

- ✅ **真正贴合老板娘真实工作流**：她的合作伙伴**散落在三个 IM**，不可能强制全部迁移
- ✅ **风险分级**：核心 B 端走企微（0 风险），朋友型走个微（半自动），内部走飞书（无风险）
- ✅ **持续演进**：今天个微靠半自动，明天客户都迁移到企微就升级到全自动
- ✅ **可观测**：所有跨渠道动作落 `logs/` 审计日志，谁说了什么、机器人代发了什么都有记录

---

## 七、文件清单

| 文件 | 类型 | 状态 |
|---|---|---|
| `SKILL.md` | 本文档（总览） | ✅ |
| 实现位于子 skill：[`wechat-monitor`](../wechat-monitor/SKILL.md) | 个人微信侧 | ✅ |
| 实现位于子 skill：[`wecom-bridge`](../wecom-bridge/SKILL.md) | 企业微信侧 | ✅ |

本 skill 不存独立 scripts —— 完全靠**编排**已有 skill 实现。
