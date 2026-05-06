---
name: lark-fashion-cockpit-wecom-bridge
version: 0.1.0
description: "企业微信桥 — cockpit 通过企业微信官方 API 给个人微信好友（"客户"）发消息、拉历史、48h 主动窗口对话。100% 合规、0 GUI 操作、可挂 cron。当用户说「给客户发消息」「拉客户历史」「企业微信通知」时使用。注意：本 skill 当前为 spec + 最小客户端实现，需要用户先注册企业微信并提供 corpId/secret。"
metadata:
  requires:
    bins: ["python"]
    pip: ["requests"]
    env: ["WECOM_CORP_ID", "WECOM_AGENT_SECRET", "WECOM_CONTACT_SECRET"]
---

# 企业微信桥 · 给个人微信好友合规发消息

> **🎯 痛点：** 个人微信桌面 RPA（wxauto / scan-person）受 Win11 焦点限制 + 微信 4.x 兼容问题，不可靠不安全。
> **核心价值：** 企业微信是腾讯**官方**支持的"加个人微信好友 + 发消息"渠道，0 风险 + 100% API 化。

---

## 一、为什么这条路是个人微信通讯的真正答案

| 路径 | 无人值守 | 风险 | 稳定性 |
|---|---|---|---|
| wxauto 桌面自动化 | ⚠️ 受 Win11 限制 | 低（被动 UI）但桌面应用每升级一次就坏 | 仅 4.0.5 兼容 |
| wechat-decrypt 内存 dump | ✅ | ⚠️ 4.1.x 触发"账号安全异常"告警 | 微信 4.1.7+ 大量失败 |
| **企业微信 API** | **✅ 完全** | **0** | **官方长期稳定** |

## 二、能做什么

### 2.1 客户联系（External Contact）
- 加个人微信好友为"客户"（每员工最多 100 个，未认证）
- 给单客户发消息（48h 主动咨询窗口内**无限**回复）
- 群发消息模板（每客户每月 4 条）
- 拉客户历史会话（需会话存档接口，企业版）

### 2.2 三大典型场景

**场景 A：日常通知"客户"（朋友/供应商）**
```
飞书发: 通知 ZC 工厂 DRS-0429 出货排期变更

→ cockpit 调企微 API → 客户 ZC 工厂收到企微消息
（前提：他主动联系过你触发 48h 窗口；或用群发模板，单月 ≤ 4 条）
```

**场景 B：拉客户历史聊天 → AI 总结**
```
飞书发: 扫 ZC 工厂 过去 72h

→ cockpit 调 externalcontact/get_msg → 拉结构化消息
→ DEEPSEEK 总结 → 飞书卡片
（依赖会话存档功能，认证企业可开通）
```

**场景 C：批量通知 N 个客户**
```
飞书发: 通知所有面料商 5 月底前能不能交付

→ cockpit 循环调企微 API → 5 个面料商收到消息
（每客户每月 ≤ 4 条群发 / 主动窗口内无限）
```

---

## 三、注册流程（5 分钟）

### 你需要做的

1. 打开 https://work.weixin.qq.com → 立即注册
2. 填企业名（如"冯兴龙工作室"，可以编）
3. 注册完成后进后台 → "我的企业" → 复制 **企业 ID（corpId）**
4. 应用管理 → 创建自建应用 → 复制 **AgentSecret**
5. 客户联系 → 启用"客户联系"功能 → 配置可使用员工 → 复制 **ContactSecret**
6. 给自己分配权限，扫码加你企微"客户"

### 不需要认证

- 测试场景（≤ 100 客户）完全够
- 单条发消息 / 拉历史不需要认证
- 仅"群发模板/朋友圈管理"等高级 API 需要营业执照认证

---

## 四、配置

```bash
# .env
WECOM_CORP_ID=ww_xxxxxxxxxx                # 企业 ID
WECOM_AGENT_SECRET=xxxxxxxx                # 自建应用 secret
WECOM_CONTACT_SECRET=xxxxxxxx              # 客户联系 secret（可与 agent 同）
```

---

## 五、API 路径（按场景）

### 拿 access_token（基础）
```
GET /cgi-bin/gettoken?corpid=...&corpsecret=...
返回: {"access_token": "xxx", "expires_in": 7200}
```

### 列出客户（外部联系人）
```
GET /cgi-bin/externalcontact/list?access_token=xxx&userid=自己企微id
返回: 客户 external_userid 列表
```

### 拿客户详情
```
GET /cgi-bin/externalcontact/get?external_userid=xxx
返回: 微信昵称 / 头像 / 性别 等
```

### 发消息给客户（48h 窗口内）
```
POST /cgi-bin/message/send
{
  "touser": "external_userid_xxx",
  "msgtype": "text",
  "agentid": 1000002,
  "text": {"content": "DRS-0429 雪纺面料 5 月底能到货吗？"}
}
```

### 群发模板（每客户每月 ≤ 4 条）
```
POST /cgi-bin/externalcontact/add_msg_template
{
  "external_userid": ["client1", "client2"],
  "text": {"content": "..."}
}
```

### 拉历史消息（需会话存档，认证企业）
```
POST /cgi-bin/msgaudit/check_single_agree
GET  /cgi-bin/msgaudit/get_permit_user_list
... （走会话存档 SDK）
```

---

## 六、文件清单

| 文件 | 状态 | 说明 |
|---|---|---|
| `scripts/wecom-client.py` | ✅ 实现 | 拿 access_token + 缓存 + 通用 API 调用封装 |
| `scripts/sync-history.py` | 🟡 spec | 拉客户历史会话（需用户配会话存档 SDK） |
| `scripts/send-msg.py` | ✅ 实现 | 给单客户/批量客户发消息（48h 窗口内）|
| `scripts/list-customers.py` | ✅ 实现 | 列出当前账号的客户联系人 |

---

## 七、与 cockpit 其他 skill 的协作

| 联动 | 触发链 |
|---|---|
| `morning-report` | 早 8:00 → 调 sync-history 拉昨日核心客户消息 → 摘要进早报 |
| `wxauto-supplier-bridge` | wxauto 是个人微信路径，**wecom-bridge 是企业微信路径，互补** |
| `cross-platform-im-agent` | 父级 skill 统一指挥三条 IM 链路（飞书 / 企微 / 个微）|
| `feedback-returns` | 退货客户企微通知 + 回单跟进 |

---

## 八、限制 & 注意

| 限制 | 数值 | 备注 |
|---|---|---|
| 未认证企业客户上限 | 100 / 员工 | 测试够 |
| 群发模板 | 每客户每月 4 条 | 不算群发 = 个性化文案就不限 |
| 主动咨询窗口 | 客户主动 → 48h | 期间无限回复 |
| API 调用频率 | 5000/分钟（access_token 有效期内）| 充足 |
| 会话存档 | 仅认证企业 | 需采购会话存档服务 |

---

## 九、与 wechat-monitor 的取舍

```
朋友/家人个人聊天      → wechat-monitor 半自动（截图 → AI）
工作群 / 工作朋友      → 引导他们加你企微 → wecom-bridge（API 全自动）
供应商 / 客户          → 必须 wecom-bridge（专业 + 合规）
```

老板娘案例：把 5 个核心供应商引导到企微 → 后续 cockpit 自动指挥企微跟他们沟通。一次性社交迁移成本，长期收益。
