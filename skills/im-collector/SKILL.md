---
name: lark-fashion-cockpit-im-collector
version: 2.0.0
description: "跨平台消息收集 — 把飞书 / 企业微信 / 个人微信三平台的群组和重要联系人消息汇集到一处，AI 分析+摘要。一处看消息，不再切换 4 个工具。当用户说「扫消息」「看下今天群里聊了啥」「跨平台摘要」「微信群速览」「重要消息汇总」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["pyautogui", "pygetwindow", "openai", "Pillow", "opencv-python", "numpy", "pyperclip", "pywin32"]
    env: ["DOUBAO_API_KEY", "DEEPSEEK_API_KEY", "LARK_FASHION_COCKPIT_BOSS_CHAT"]
---

# 跨平台消息收集 · 一处看完所有消息

> **🎯 痛点：** 老板娘的合作伙伴散落在飞书 / 企业微信 / 个人微信，每天打开 4 次切换看消息，重要的还容易漏。
>
> **核心价值：** 一句飞书指令 → 系统自动汇集三平台关键消息 → AI 分析 → 摘要早报。

## 一、三平台采集策略

| 平台 | 采集方式 | 风险 | 状态 |
|---|---|---|---|
| 飞书 | `lark-cli im` 拉 @我 / 群消息 / 待办 | 0 | ✅ |
| 企业微信 | 会话存档（认证企业）+ 客服消息接口（48h 窗口） | 0 | spec |
| 个人微信 | 截图 + AI 视觉（4 路径，详见下方） | 0 | ✅ 已跑通 |

## 二、个人微信 4 路径（核心难点）

### 路径 A · 主窗口扫红点（自动）⭐
- `scan-wechat.py` —— 截图 PC 微信主窗口 → DOUBAO 视觉识别群列表 + 未读红点 + @我 + 关键词命中
- 0 风险：OS 级截屏，腾讯不感知
- 全微信版本兼容（4.0 / 4.1 / 5.0）

### 路径 B · 长截图 AI 总结（半自动主推）⭐
- `summarize-image.py` —— 用户飞书滚动截屏一个群 30 秒 → 长图发给 cockpit 机器人 → DOUBAO 一图分析
- 实测 1076×21180 长图识别 98 条消息无漏

### 路径 C · 第三方导出文件总结（半自动）
- `summarize-export.py` —— 用第三方工具导出聊天 .txt → DEEPSEEK 文本分析
- 比图片便宜 20 倍，能装数千条消息精确按时间过滤

### 路径 D · 桌面 RPA 进群（实验性）
- `scan-person.py` —— PyAutoGUI 自动搜索 + 进群 + 滚屏 + AI 拼接长图分析
- ⚠️ Win11 焦点限制 + 微信 Qt 渲染，仅在独立 PowerShell 跑稳

## 三、典型用法

```
飞书发: 扫所有渠道 24h
  ↓
并发拉：
  ├─ 飞书：@我 + 待办（lark-im / lark-task）
  ├─ 企微：48h 主动窗口的客户消息
  └─ 个微：scan-wechat 主窗口 + 关键群 summarize-image
  ↓
DEEPSEEK 三路情报合并
  ↓
飞书卡片摘要（紧急 / @我 / 关键词命中）
```

## 四、文件清单

| 文件 | 用途 |
|---|---|
| `scripts/scan-wechat.py` | 主窗口扫红点（自动）|
| `scripts/summarize-image.py` | 长图 AI 总结（半自动主推）|
| `scripts/summarize-export.py` | 第三方导出 .txt 分析 |
| `scripts/scan-person.py` | 桌面 RPA 进群（实验性）|
| `scripts/snap-wechat.py` | 截图测试工具 |
| `scripts/wake-wechat.py` | 从托盘呼出微信 |
| `scripts/probe-wechat-uia.py` | UIA 探测工具（开发用）|

## 五、与 im-broadcaster 互补

| skill | 角色 |
|---|---|
| **im-collector**（本 skill）| 一处**看**消息（多平台汇集 + AI 摘要）|
| **im-broadcaster** | 一处**发**消息（多平台分发 + 风控）|

跨平台 IM 板块就这两个 skill。简化设计：**收消息 / 发消息**，不再有更多。
