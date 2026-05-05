# 🤖 飞书机器人部署指南（老板娘版 · 5 分钟搞定）

> **目标：** 给老板娘部署 lark-fashion-cockpit 助手机器人。**老板娘不会用 Claude Code，只用飞书 IM 沟通。**
>
> **结果：** 老板娘在飞书私聊机器人 / 群里@机器人「巡检任务」「DRS 配什么好」「看下利润」 → 30 秒内收到卡片回复。

---

## 📋 全流程概览

```
Step 1: 飞书后台建机器人      （5 分钟，部署人员一次性做）
Step 2: 配置 lark-cli 凭证    （1 分钟）
Step 3: 在电脑/服务器跑 listener （后台 24h 跑）
Step 4: 老板娘私聊或@机器人    （永久使用）
```

---

## 🅰 Step 1：建飞书自建应用 + 机器人

### 1.1 进入飞书开发者后台

打开浏览器：[https://open.feishu.cn/app](https://open.feishu.cn/app)

用**老板娘自己的飞书账号**登录（机器人会安装在老板娘的企业里）。

### 1.2 创建自建应用

```
点右上角"创建企业自建应用"
  ↓
填写：
  应用名称：lark-fashion-cockpit 助手
  应用图标：上传一个（可以用 assets/products/DRS-0429-FL.jpg 占位）
  应用描述：女装运营驾驶舱 AI 助手 — 老板娘飞书一句话指挥
  ↓
点"创建"
```

### 1.3 添加机器人能力

```
左侧菜单 → "添加应用能力"
  ↓
找到"机器人" → 点"添加"
  ↓
机器人配置：
  机器人名称：lark-fashion-cockpit 助手
  描述：发送指令我自动跑（巡检/搭配/利润/下单等）
```

### 1.4 配置事件订阅

```
左侧菜单 → "事件与回调" → "事件订阅"
  ↓
选择订阅方式：
  ⭐ 长连接（推荐，无需公网 IP）
  ↓
点"添加事件" → 搜索：
  ✅ im.message.receive_v1（接收消息）
  ↓
保存
```

### 1.5 添加权限

```
左侧菜单 → "权限管理"
  ↓
搜索并添加：
  ✅ im:message:send_as_bot       （机器人发消息）
  ✅ im:message.group_at_msg      （群里@机器人）
  ✅ im:message.p2p_msg.readonly  （P2P 消息）
  ✅ im:resource:upload           （上传图片）
  ✅ im:chat:read                 （读取群信息）
  ↓
点"申请发布版本"
```

### 1.6 发布应用 + 安装

```
左侧菜单 → "版本管理与发布"
  ↓
"创建版本" → 填版本号 v1.0.0 → 提交审核
  ↓
（如果你是企业管理员，自审秒过；否则等管理员审批）
  ↓
审批通过后 → "可用范围管理" 添加为"全员可用"
  ↓
飞书工作台搜索 "lark-fashion-cockpit 助手" → 点"安装"
```

### 1.7 拿到凭证

```
左侧菜单 → "凭证与基础信息"
  ↓
复制：
  App ID：cli_xxxxx
  App Secret：xxxxx
  ↓
妥善保管（特别是 Secret 别泄露）
```

---

## 🅱 Step 2：配置 lark-cli 凭证

打开 PowerShell，跑：

```powershell
cd C:\Users\冯兴龙\lark-fashion-cockpit
PowerShell -File scripts/setup-bot.ps1 -AppId "cli_你的App_ID" -AppSecret "你的App_Secret"
```

脚本会做：
1. 创建一个 lark-cli profile（独立于你的 user 身份）
2. 测试机器人连接
3. 把机器人加到老板群

---

## 🅲 Step 3：跑 event-listener（24h 后台运行）

### 方式 A：手动启动（关电脑会停）

```powershell
python C:\Users\冯兴龙\lark-fashion-cockpit\scripts\event-listener.py
```

### 方式 B：后台跑（推荐 · 关闭终端不停）

```powershell
start /b python C:\Users\冯兴龙\lark-fashion-cockpit\scripts\event-listener.py > C:\Users\冯兴龙\lark-fashion-cockpit\logs\listener.log 2>&1
```

### 方式 C：开机自启（最佳 · 老板娘不用管）

```powershell
# Windows 任务计划程序：
# 1. 打开"任务计划程序"
# 2. 创建基本任务 → 名称："lark-fashion-cockpit listener"
# 3. 触发器：当计算机启动时
# 4. 操作：启动程序
#    程序：python
#    参数：C:\Users\冯兴龙\lark-fashion-cockpit\scripts\event-listener.py
# 5. 完成 → 重启电脑测试
```

### 方式 D：云服务器部署（生产终极方案）

把 lark-fashion-cockpit 放到一台 Linux 云服务器（阿里云/腾讯云 ¥30/月）：

```bash
# /etc/systemd/system/lark-cockpit.service
[Unit]
Description=lark-fashion-cockpit listener
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/lark-fashion-cockpit/scripts/event-listener.py
Restart=always
User=larkuser

[Install]
WantedBy=multi-user.target

# 启动
sudo systemctl enable lark-cockpit
sudo systemctl start lark-cockpit
```

---

## 🅳 Step 4：老板娘飞书使用

### 4.1 私聊机器人（一对一）

```
老板娘飞书：
  搜索"lark-fashion-cockpit 助手" → 打开聊天
  ↓
输入："巡检任务"
  ↓
30 秒内：
  机器人回复 → 红色任务巡检卡片（含逾期/紧急/接近截止 4 类）
```

### 4.2 群里@机器人（多人协作）

```
老板娘把机器人加到"🚀 lark-fashion-cockpit 助手"群
  ↓
群里输入："@助手 DRS-0429-FL 配什么好"
  ↓
机器人回复 → 蓝色搭配推荐卡片（含搭配图）
```

### 4.3 支持的 5 句话指令（永久有效）

| 老板娘说 | 机器人做 | 收到 |
|---|---|---|
| "巡检任务" / "看下逾期" | 跑 task-tracker | 红色任务巡检卡片 |
| "DRS-0429-FL 配什么好" | 跑 product-matching | 蓝色搭配推荐 + 搭配图 |
| "新品 DRS-2026-RM 下多少件" | 跑 launch-decision | 紫色 4 维信号建议 |
| "看下利润" / "哪些款赚钱" | 跑 profit-analysis | 橙色利润榜 |
| "为什么任务老延期" | 跑 task-retrospective | 青色复盘 + AI 反哺 |

更多指令在 [`scripts/event-listener.py`](../scripts/event-listener.py) 的 `ROUTES` 数组里随时增加。

---

## 🛡 安全提醒

1. **App Secret 别泄露**：等同于密码，泄露后任何人能假冒老板娘机器人
2. **机器人仅老板娘可用**：在权限里设"指定人员可见"
3. **公司敏感数据**：机器人能访问飞书原生任务/会议/文档，按需限制 scope
4. **Listener 服务器**：放在公司可控的电脑/云服务器上

---

## 🎯 一句话总结

```
建机器人（5 分钟一次性）
  ↓
配置 lark-cli（1 分钟一次性）
  ↓
启动 listener（设开机自启）
  ↓
老板娘飞书一句话 → 30 秒卡片回复（永久使用）
```

**这就是 lark-fashion-cockpit 真正的"老板娘飞书一句话指挥"工作方式。**
