---
name: lark-fashion-cockpit-auto-scheduler
version: 1.0.0
description: "装即生效的自动化调度器 Skill — 接管整个 cockpit 12+ 个定时任务（早 8:00 经营晨报 / 任务巡检 / 博主监控 / 开源雷达 / 晚 22:00 个人复盘 / 23:00 直播日报 等）。用户装完 skill 后启动一次调度器，所有自动任务永久生效，飞书发"列出/停 X/启用 X"实时控制。基于 APScheduler + lark-cli。当用户说「自动任务」「定时任务」「装即生效」「停止 XX 自动跑」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 自动调度器 — 装完一次，永久自动跑

> **🎯 痛点：** 各 skill 都说"配 cron 自动跑"，但用户得自己手动配 12 个 cron，且关机就没了。

> **核心价值：** 一个主调度器接管所有定时任务。**装完启动一次，所有自动 skill 永久生效**。
> 飞书发「列出自动任务」实时看清单；发「停 morning-report」/「启用 personal-mirror」实时开关。

---

## 一、为什么需要这个 skill

| 没有这个 skill | 用了这个 skill |
|---|---|
| 用户要在 Windows Task Scheduler 配 12 个任务 | **0 配置**：装完 `python scheduler.py` 一次跑 |
| 关机或电脑重启自动任务全没 | **重启后自动恢复**（配开机启动）|
| 改时间要去 Task Scheduler 改 | 改 `config/auto-triggers.json` 重启 scheduler 即可 |
| 想停某个任务要找进程 kill | 飞书发「停 morning-report」秒停 |
| 不知道有哪些自动任务在跑 | 发「列出自动任务」一眼看到 |

---

## 二、装完即生效的 12 个自动任务

| 任务 | cron | 默认状态 |
|---|---|---|
| 📊 经营晨报 | 早 8:00 每天 | ✅ on |
| ⏰ 任务巡检日报 | 早 8:30 每天 | ✅ on |
| ⏰ 任务实时巡检 | 工作时段每小时 | ⚠️ off（按需开）|
| 👀 对标博主监控 | 早 8:00 每天 | ✅ on |
| 🛰 开源雷达 | 早 9:00 每天 | ✅ on |
| 📺 直播前预检 | 13:30 / 18:30 | ✅ on |
| 📺 直播日报 | 晚 23:00 每天 | ✅ on |
| 🪞 个人成长镜子 | 晚 22:00 每天（全员）| ✅ on |
| 🎯 skill 推荐器 | 每周一早 8:00 | ✅ on |
| 📦 库存预警实时 | 工作时段每 30 分钟 | ✅ on |
| 📈 竞品趋势周报 | 每周一早 10:00 | ⚠️ off（数据准备好后开）|
| 🎯 OKR 月度进度 | 每月 1 日早 9:00 | ✅ on |

完整配置在 [`../../config/auto-triggers.json`](../../config/auto-triggers.json)，可直接编辑。

---

## 三、前置条件

```bash
pip install apscheduler croniter
```

---

## 四、装即生效流程（用户做 30 秒）

```bash
# 用户装 cockpit 之后跑这一次：
cd lark-fashion-cockpit
python skills/auto-scheduler/scripts/cockpit-scheduler.py

# 看到：
# [scheduler] 已注册 12 个自动任务
# [scheduler] 下次触发: 📊 经营晨报 @ 2026-05-06 08:00:00
# [scheduler] 主循环开始 ...

# 这个进程要一直跑（类似 event-listener.py）
# 推荐做开机启动 → Windows: Task Scheduler 设"At log on"
```

---

## 五、飞书 IM 实时控制

启动后，给 cockpit 机器人发这些指令（owner 角色专属）：

| 飞书发 | 效果 |
|---|---|
| `列出自动任务` | 列 12 个任务 + 状态 + 下次触发时间 |
| `停 morning-report` | 立即禁用经营晨报（不再触发）|
| `启用 personal-mirror` | 启用个人复盘 |
| `自动任务 状态` | 简版概览 |
| `重新加载自动任务` | 改了 config/auto-triggers.json 后重读配置 |

---

## 六、与 event-listener 协同

```
event-listener.py（消息驱动）
   ↓ 处理 IM 消息 + 关键词路由 + 自然语言路由 + 私聊角色
auto-scheduler.py（时间驱动）
   ↓ 定时触发 cockpit 的 12 个 skill
   ↓ 触发结果走飞书 OpenAPI 回老板群 / 员工私聊
```

两个进程协同：
- event-listener 是**被动**响应消息
- auto-scheduler 是**主动**定时触发
- 控制命令也走 event-listener，再委托 scheduler

---

## 七、与所有自动 skill 解耦

每个 skill 不需要自己写 cron。**只需要把脚本入口暴露好**，scheduler 调用即可。

例：
```yaml
# config/auto-triggers.json 加一条
{
  "id": "新任务",
  "cron": "0 12 * * *",
  "command": "python skills/xxx/scripts/run.py",
  "target": "boss_chat",
  "enabled": true
}
```

不需要改任何 skill 本身。

---

## 八、监控 + 日志

- 每次触发记录到 `logs/scheduler.log`
- 失败的任务自动重试 1 次
- 连续失败 3 次发飞书警报给 owner
- 每周日发一份"本周自动任务执行报告"

---

## 九、重启自动恢复

- 推荐：Windows Task Scheduler 配置「At log on」启动 `cockpit-scheduler.py`
- 或者：用 `nssm`/`pm2` 把它做成系统服务
- 详见 [`references/auto-start-on-boot.md`](./references/auto-start-on-boot.md)

---

## 十、参考

- 主调度器脚本：[`scripts/cockpit-scheduler.py`](./scripts/cockpit-scheduler.py)
- 任务配置：[`../../config/auto-triggers.json`](../../config/auto-triggers.json)
- 开机启动配置：[`references/auto-start-on-boot.md`](./references/auto-start-on-boot.md)
- 飞书控制命令：[`references/lark-control-commands.md`](./references/lark-control-commands.md)
- 监控+告警：[`references/monitoring.md`](./references/monitoring.md)
