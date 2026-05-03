# IM 卡片最佳实践 — 4 个真实坑 + 解法

> **2026-05-03 实测踩出来的飞书 IM 工程经验**。每条都有现成可跑的命令链。

---

## 坑 1：给自己（user-id = self）发消息无推送

### 现象
```bash
lark-cli im +messages-send --as user --user-id <self_open_id> --markdown "..."
# API 返回 ok=true、message_id 正常
# 但飞书 App 不弹推送、不显示在消息列表顶部
```

### 原因
飞书 UX 设计：你不会想"自己给自己发消息打扰自己"。这是产品决策，不是 bug。

### 解法
**建一个独人群替代 P2P-self。**

```bash
NOTIFY_CHAT=$(lark-cli im +chat-create \
  --as user --type private \
  --name "🚀 lark-fashion-cockpit 助手" \
  --jq '.data.chat_id')

# 后续所有 IM 通知发到 chat-id 而不是 user-id
lark-cli im +messages-send --as user --chat-id "$NOTIFY_CHAT" --markdown "..."
```

群里发消息 = **飞书会原生推送**（小红点+角标+锁屏通知）。

---

## 坑 2：跨租户 P2P IM 直接禁止

### 现象
```bash
lark-cli im +messages-send --as user --user-id <跨租户朋友> --markdown "..."
# 错误：HTTP 400 cross tenant p2p chat operate forbid (code: 230038)
```

### 原因
飞书安全机制：跨租户的两个用户即使是好友也不能直接发 P2P IM（防止恶意营销）。

### 解法

**方案 A：用飞书原生业务通道（任务 / 审批 / 日历）**
这些通道走的是组织授权而不是 P2P，**跨租户不受限**。

```bash
# 任务通道：跨租户朋友能收到飞书原生任务通知
lark-cli task +create --summary "..." --jq '.data.task.guid' | xargs -I {} \
  lark-cli task +assign --task-id {} --add <跨租户朋友>
```

**方案 B：用 applink 短链 + 微信/邮件**
拿到 task / doc / base 的 applink，通过非飞书渠道转给对方，对方点击会自动跳到飞书 App。

```
https://applink.feishu.cn/client/todo/detail?guid=<task_guid>
https://my.feishu.cn/docx/<doc_id>
```

---

## 坑 3：跨租户用户不能拉到统一群

### 现象
```bash
lark-cli im +chat-create --as user --type private \
  --users "<跨租户朋友1>,<跨租户朋友2>"
# 错误：HTTP 400 cross-tenant chats operate forbid (code: 232033)
```

### 原因
跟坑 2 同源——飞书禁止外部联系人被拉到统一群。

### 解法
**只有同租户的团队才能群通知。** 跨租户场景下：
- 老板（自己）→ 独人群通知
- 跨租户朋友 → 走任务通道，飞书原生通知不受限
- 用 applink 兜底

---

## 坑 4：markdown 链接不可点击

### 现象
```bash
lark-cli im +messages-send --as user --chat-id $CHAT --markdown "[查看](https://...)"
# 飞书渲染只显示纯文本"查看"，链接不可点
```

### 原因
飞书 IM `--markdown` 包装的是 post 类型消息，post 对 markdown 链接的渲染有限制。

### 解法
**用 interactive 卡片 + button 元素。**

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "📊 标题"},
    "template": "blue"
  },
  "elements": [
    {"tag": "div", "text": {"tag": "lark_md", "content": "**关键数据**"}},
    {"tag": "action", "actions": [
      {"tag": "button", "text": {"tag": "plain_text", "content": "📄 查看报告"}, "type": "primary", "url": "https://..."},
      {"tag": "button", "text": {"tag": "plain_text", "content": "📊 打开多维表"}, "type": "default", "url": "https://..."}
    ]}
  ]
}
```

card template 颜色：
- `red` 紧急告警
- `orange` 提醒
- `yellow` 注意
- `green` 完成 / 正常
- `blue` 信息
- `turquoise` / `purple` / `wathet` 其他

### 子坑：PowerShell 5.x 调 lark-cli 传 JSON 双引号被吞

```powershell
# ❌ 错误：直接传 JSON 字符串
$json = '{"key":"value"}'
& lark-cli im +messages-send --content $json
# error: --content is not valid JSON: {key:value} （双引号没了）

# ✅ 正确：用 cmd /c 转义双引号成 ""
$cmdEscaped = $json -replace '"', '""'
cmd /c "lark-cli im +messages-send --content `"$cmdEscaped`""
```

---

## 综合最佳实践（用这套就稳了）

```bash
# Step 1: 初始化时建独人通知群
NOTIFY_CHAT=$(lark-cli im +chat-create --as user --type private \
  --name "🚀 lark-fashion-cockpit 助手" --jq '.data.chat_id')

# Step 2: 把 chat_id 存到 team-config.json
echo "{\"notification_chat\":{\"chat_id\":\"$NOTIFY_CHAT\"}}" > team-config.json

# Step 3: 所有 Skill 通知都用 interactive 卡片 + chat_id
function send_notification() {
  local card_json="$1"
  local cmd_escaped=$(echo "$card_json" | sed 's/"/""/g')
  cmd /c "lark-cli im +messages-send --as user --chat-id $NOTIFY_CHAT --msg-type interactive --content \"$cmd_escaped\""
}

# 用法
send_notification '{"config":{...},"header":{...},"elements":[...]}'
```

---

## 颜色 / Emoji 选择规范（写卡片时参考）

| 业务场景 | header.template | emoji | 用途 |
|---|---|---|---|
| 库存售罄风险 | red | 🔴 | 紧急止损 |
| 任务超期 | orange | 🟡 | 提醒推进 |
| 任务完成 | green | ✅ | 正反馈 |
| AI 分析报告 | blue | 🤖 | 信息类 |
| 经营晨报 | turquoise | 🌅 | 日报 |
| OKR 落后 | red | ⚠️ | 关注 |
| 上新启动 | green | 🚀 | 启动类 |
| 审批待处理 | yellow | ✍️ | 待办 |

---

## 这套经验的复用价值

写在这里**不只是给 lark-fashion-cockpit 用，给任何飞书 CLI Skill 用都受益**。

未来其他参赛者 fork 这个仓库做其他垂直行业（化妆品/家居/食品）时，**这 4 个坑+解法直接搬走，省至少 2 小时调试时间**。
