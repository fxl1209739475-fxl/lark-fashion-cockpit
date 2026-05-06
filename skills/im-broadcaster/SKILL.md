---
name: lark-fashion-cockpit-im-broadcaster
version: 1.0.0
description: "跨平台消息发送 — 飞书一句话指令 → AI 理解 → 同时调用飞书 / 企业微信 / 个人微信 API → 多平台分发消息。一处发消息，不再切 3 个工具复制粘贴。当用户说「通知 ZC 工厂」「群发面料商」「发企微给客户」「跨平台广播」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["wxauto", "requests", "openai"]
    env: ["WECOM_CORP_ID", "WECOM_AGENT_SECRET", "WECOM_CONTACT_SECRET"]
---

# 跨平台消息发送 · 一处发消息，多平台收

> **🎯 痛点：** 老板娘一条"DRS-0429 加急"消息要发给：
> - 飞书内部团队（设计师 + 生产 + 内容）
> - 企业微信客户（48h 主动窗口里的）
> - 个人微信供应商（朋友型，加企微嫌正式）
>
> 三个平台手动切换复制粘贴，效率低 + 容易遗漏。

> **核心价值：** 在驾驶舱聊天框说一句话 + 指定平台 → AI 理解后调用对应 API → 一句话三端发出。

## 一、三个发送通道

### 通道 A · 飞书 IM（内部）
- `lark-cli im +messages-send` —— 发到群 / 私聊
- 0 限制，最稳

### 通道 B · 企业微信 API（合规 B 端）
- `scripts/wecom/wecom-client.py` —— 拿 access_token + 通用 API 调用
- `scripts/wecom/send-msg.py` —— 发应用消息 / 客户群发模板 / 48h 窗口回复
- `scripts/wecom/list-customers.py` —— 列客户联系人
- `scripts/wecom/sync-history.py` —— 拉客户历史会话（需会话存档 SDK）

**额度**：
- 群发模板：每客户每月 4 条
- 48h 主动窗口：客户主动联系后 48h 内 API 回复**无限制**
- 未认证企业：每员工最多 100 客户

### 通道 C · 个人微信 wxauto（朋友型供应商）
- `scripts/wxauto/send-to-supplier.py` —— 飞书指令 → wxauto 控制 PC 微信 → 发指定供应商
- `scripts/wxauto/broadcast-to-suppliers.py` —— 群发同类供应商（限速 12s 间隔）
- `scripts/wxauto/init-supplier-table.py` —— 一键建 28_供应商档案 表

**4 层风控**（防风控封号）：
1. 仅 owner 可触发（防员工冒用私号）
2. 白名单：仅 28 表 status=活跃 的供应商
3. 限速：≤ 5 条/分钟，≤ 50 条/天
4. 审计：每条记 `logs/wxauto-audit.jsonl`
5. 消息加前缀 `(老板娘 cockpit 自动消息)` 透明告知

## 二、典型用法

### 单条精准发送
```
飞书发: 通知 ZC 工厂 DRS-0429 雪纺面料下周一前能否交货

→ DEEPSEEK 解析：supplier="ZC 工厂"，channel=个微（28 表查到 ZC 在个微）
→ 路由到 scripts/wxauto/send-to-supplier.py
→ wxauto 自动给浙江老张发微信
→ 飞书回执"✓ 已发，对方已读"
```

### 批量同类供应商
```
飞书发: 问所有面料商 5 月底雪纺面料能否到货

→ 28 表查 type=面料商 + status=活跃 → 5 个面料商
→ 循环 wxauto 发，每条间隔 12 秒
→ 进度卡片"已问 5 个面料商，等回复"
```

### 跨平台同步（飞书内部 + 企微外部）
```
飞书发: 通知所有合作方 5/15 上新延期 1 周

→ AI 路由：
   ├─ 内部团队 → 飞书 IM 群
   ├─ 企微客户 → 群发模板（每客户每月 ≤ 4 条）
   └─ 个微供应商 → wxauto 限速循环
→ 一份汇报卡片"飞书 ✓ / 企微 8 个 ✓ / 个微 5 个 ✓"
```

## 三、文件清单

```
skills/im-broadcaster/
  ├─ SKILL.md
  └─ scripts/
      ├─ wxauto/                          # 个人微信桥
      │   ├─ send-to-supplier.py          # 单点发送
      │   ├─ broadcast-to-suppliers.py    # 群发同类
      │   └─ init-supplier-table.py       # 建 28 表
      └─ wecom/                            # 企业微信 API
          ├─ wecom-client.py               # access_token 拿取
          ├─ send-msg.py                   # 发消息（应用 / 客户 / 群发）
          ├─ list-customers.py             # 列客户
          └─ sync-history.py               # 拉历史（会话存档，spec only）
```

## 四、与 im-collector 互补

| skill | 角色 |
|---|---|
| **im-collector** | 一处**看**消息（多平台汇集 + AI 摘要）|
| **im-broadcaster**（本 skill）| 一处**发**消息（多平台分发 + 风控）|

跨平台 IM 板块就这两个 skill。简化设计：**收消息 / 发消息**，不再有更多。

## 五、注册流程（首次配置）

### 个人微信（wxauto 通道）
1. PC 微信 4.0+ 客户端登录
2. `pip install wxauto`（4.1.x 用 `wxauto4`）
3. `python scripts/wxauto/init-supplier-table.py` 建 28_供应商档案 表
4. 老板娘在 28 表里录入 5-20 个核心供应商 + 微信备注名

### 企业微信（API 通道）
1. https://work.weixin.qq.com 注册（不需要营业执照认证）
2. 启用"客户联系"应用
3. 拿 corpId + AgentSecret + ContactSecret 写到 .env
4. 让客户扫码加你企微（一次性社交迁移）
