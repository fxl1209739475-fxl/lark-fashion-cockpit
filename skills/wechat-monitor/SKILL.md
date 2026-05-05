---
name: lark-fashion-cockpit-wechat-monitor
version: 1.0.0
description: "微信群速览 — 截图主窗口 → DOUBAO 视觉一把梭识别未读红点+消息预览+@我 → 飞书卡片推送。0 微信感知（OS 级截屏，不动微信进程），全微信版本通用（4.0/4.1/5.0），不依赖 wxauto。当用户说「扫微信群 / 微信速览 / 看下微信谁找我了 / 微信摘要」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["pyautogui", "pygetwindow", "openai", "Pillow"]
    env: ["DOUBAO_API_KEY", "LARK_FASHION_COCKPIT_BOSS_CHAT"]
---

# 微信群速览 · 截图 + AI 视觉，0 风险

> **🎯 痛点：** 工作微信群多，每天积一堆未读，逐个点开看费时。
> **核心价值：** 一句话飞书指令 → AI 帮你扫一眼所有群，10 秒摘要"哪些群有事、谁@你、关键词命中"。

---

## 一、为什么这是当前最稳的方案

跟 [`wxauto-supplier-bridge`](../wxauto-supplier-bridge/SKILL.md) 主动发消息互补，本 skill 解决"读消息"侧。

| 路径 | 微信能感知 | 兼容 4.1.9 | 风险 |
|---|---|---|---|
| wxauto4 UIA 读取 | ⚠️ 跟手动看一样 | ❌ 仅 4.0.5 | 低 |
| 微信本地数据库 hook | ✅ 注入进程 | ⚠️ 部分 | **高（封号 + 法律）** |
| **截图 + AI 视觉** | ❌ **完全不能** | ✅ 全版本 | **0** |

**截图方案 = 你电脑上自己截屏**，跟 QQ 截图、微信自带截图、PrintScreen 没有任何区别。腾讯反作弊**根本看不到这件事在发生**。

---

## 二、原理（三步）

```
1. pygetwindow 找到微信主窗口
2. pyautogui 截屏 → DOUBAO 多模态识别
3. 输出 JSON：未读群名 / 红点数 / 预览文字 / @我 标记 / 关键词命中
4. 飞书发卡片，红色=紧急 / 橙色=有未读 / 蓝色=无事
```

**截图不写盘** —— 用完即丢（含其他群隐私），只保留 AI 识别后的脱敏摘要。

---

## 三、典型使用

### 场景 A：手动触发
```
飞书发: 扫微信群

→ 截图 → DOUBAO → 卡片回到飞书：

📱 微信群速览  ·  09:32

摘要
你有 3 个工作群有未读消息，1 条提到 DRS-0429 出货，2 个营销号已忽略。

🚨 紧急消息
🚨 ZC 工厂群：DRS-0429 雪纺面料卡在染色环节，预计延 2 天
🚨 朱健豪@你：直播脚本 V2 待审

未读群
• 老板娘合伙人群 [3]
  下周ALL HANDS 议程怎么定...
• ZC 工厂沟通群 [12] 🔔@你
  下周一上午 10 点能到货吗
```

### 场景 B：每 30 分钟自动扫（auto-scheduler）
```jsonc
// config/auto-triggers.json
{
  "wechat-scan": {
    "cron": "*/30 * * * *",
    "skill": "wechat-monitor",
    "args": ["--keywords", "DRS-0429,出货,质量,投诉"]
  }
}
```

### 场景 C：关键词命中 → 立即报警
```
飞书发: 扫微信群 关键词=DRS-0429,出货延期

→ 命中即触发红色卡片 + 老板手机震动
```

---

## 四、安全 & 隐私

- 截图**完全不写盘**（PIL 内存对象 → base64 → DOUBAO → GC）
- AI 识别后只持久化"脱敏摘要文本"到飞书
- 不上传腾讯/微信任何用户数据，仅你自己电脑屏幕的图像
- 不调微信任何接口，不读微信本地文件，不 hook 微信进程

---

## 五、漏消息边界（诚实交代）

一张主窗口截图能抓 / 抓不到：

| 类型 | 能抓到吗 |
|---|---|
| 群有未读红点 + 数字 | ✅ |
| 每个群最后一条消息预览 | ✅ |
| 谁@了我 | ✅ |
| 同一群最后一条之外的其他新消息 | ❌（但红点数字提示密度，按需 Tier 2 进群） |
| 屏幕外的群（一屏外） | ❌（要滚群列表，Tier 2 升级时支持） |
| 已读但重要的消息 | ❌（红点已清零，要靠 Tier 3 状态对比） |

**当前版本 = Tier 1（90% 工作流够用）**。Tier 2/3 见 [roadmap](#七roadmap)。

---

## 六、event-listener 路由（建议加）

```python
WECHAT_SCAN_RE = re.compile(r"^(扫微信群|微信速览|微信摘要|看下微信)(?:\s+(.+))?$")

m = WECHAT_SCAN_RE.match(text)
if m:
    if user_config["role"] != "owner":
        send_card(chat_id, "🚫 权限不足", "微信速览仅老板可用（截图含私人群）", "red")
        return
    extra = m.group(2) or ""
    args = ["python", "skills/wechat-monitor/scripts/scan-wechat.py"]
    if "关键词=" in extra:
        kws = extra.split("关键词=", 1)[1]
        args += ["--keywords", kws]
    subprocess.Popen(args)
    return
```

---

## 七、Roadmap

- **Tier 1 ✅**：每 30 分钟主窗口截图 + DOUBAO 摘要
- **Tier 2**：关键群白名单（≤ 5 个），自动进群截一屏（PyAutoGUI 双击 + 截图）
- **Tier 3**：SQLite 状态对比，红点数字突变 → 主动追溯

---

## 八、参考

- 主脚本：[`scripts/scan-wechat.py`](./scripts/scan-wechat.py)
- 截图测试：[`scripts/snap-wechat.py`](./scripts/snap-wechat.py)
- 互补 skill：[`wxauto-supplier-bridge`](../wxauto-supplier-bridge/SKILL.md)（主动发消息）
