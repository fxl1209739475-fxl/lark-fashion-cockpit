---
name: lark-fashion-cockpit-multi-user-private-channels
version: 1.0.0
description: "私聊版 cockpit — 让公司每个员工跟同一个机器人「私聊」使用 cockpit，内容只有员工和机器人可见，其他人看不到。基于飞书机器人原生 P2P 模式 + 角色权限矩阵（老板/设计师/工厂/主播/客服各自能用的 skill 不同）。当用户问「员工怎么私聊用」「权限怎么管」「不想公开问的怎么办」时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 私聊版 cockpit — 70 人各自和机器人私聊

> **🎯 痛点：** 群聊里和机器人对话**所有人都看得到**。
> - 老板娘问"今天利润多少"被全员看到 → 不合规
> - 客服问"客户赵姐之前买啥"被工厂看到 → 隐私问题
> - 员工 A 用老板分身复审被员工 B 看到 → 违和

> **解决方案：** 飞书机器人**原生支持 P2P 私聊** — 同一个 cockpit 机器人，每个员工跟它单独聊，互相完全看不到。**不需要给每人配独立机器人**。

---

## 一、飞书机器人 3 种对话模式（原生支持）

| 模式 | 特点 | 适用 |
|---|---|---|
| **群聊** | 群成员都看到对话 | 团队协作、公开汇报 |
| **P2P 私聊** | 只有用户和机器人 | **个人查询、敏感数据** |
| **专属群** | 1v1 群（机器人 + 1 个人）| P2P 升级版，可加文件 |

**P2P 私聊是飞书机器人原生功能，不需要开发。** 改 1 行 event-listener 配置就能启用全员私聊。

---

## 二、当前 event-listener.py 限制

```python
# 当前代码（只老板娘能用）
BOSS_OPEN_ID = "ou_85c9148d13c562728e60d456b60d9afc"

def handle_message(event):
    sender = event.get("sender_id", "")
    if sender != BOSS_OPEN_ID:
        return  # ❌ 其他人发消息直接忽略
    ...
```

## 三、改造（让全员私聊用，按角色权限）

```python
# 改造后
ROLE_REGISTRY = {
    # 老板娘（全部权限）
    "ou_85c9148d13c562728e60d456b60d9afc": {
        "name": "老板娘",
        "role": "owner",
        "allowed_skills": ["*"],  # 所有 skill
    },
    # 设计师马萍蔓
    "ou_0ba02adab44ecb14a6c99e869823312b": {
        "name": "马萍蔓",
        "role": "designer",
        "allowed_skills": [
            "task-tracker", "task-collaboration",
            "product-library", "product-matching", "product-graph",
            "doc-iterator", "knowledge-base",
            "natural-language-router",
        ],
    },
    # 生产主管申丽媛
    "ou_5cd0eb47d312bbbf9011b5ecdae01e07": {
        "name": "申丽媛",
        "role": "production",
        "allowed_skills": [
            "task-tracker", "production-supplier", "order-fulfillment",
            "stock-replenishment", "natural-language-router",
        ],
    },
    # 内容编辑朱健豪
    "ou_32f38bc03a052fb36120de2610f616a3": {
        "name": "朱健豪",
        "role": "content",
        "allowed_skills": [
            "content-pipeline", "video-script-parser", "blogger-monitor",
            "competitor-monitor", "natural-language-router",
        ],
    },
    # 主播（示例 — 实际填真实 open_id）
    "ou_xxx_anchor": {
        "name": "主播小马",
        "role": "anchor",
        "allowed_skills": [
            "live-streaming", "stock-replenishment", "product-matching",
            "natural-language-router",
        ],
    },
    # 客服（示例）
    "ou_xxx_cs": {
        "name": "客服小红",
        "role": "service",
        "allowed_skills": [
            "feedback-returns", "private-domain", "lingo-fashion-glossary",
            "helpdesk-customer-tickets", "natural-language-router",
        ],
    },
}

DEFAULT_ALLOWED_SKILLS = ["natural-language-router", "knowledge-base", "lingo-fashion-glossary"]


def handle_message(event):
    sender = event.get("sender_id", "")
    chat_type = event.get("chat_type", "")  # "p2p" 或 "group"
    text = extract_text(event["content"])

    # 1. 检查发送者是否注册
    user_config = ROLE_REGISTRY.get(sender)
    if not user_config:
        # 未注册员工 → 给"请联系管理员加权限"提示
        if chat_type == "p2p":
            send_card(event["chat_id"], "👋 你还没接入 cockpit",
                      "请联系老板娘加你的权限。临时只能用：知识库查询 / 词典查询",
                      "yellow")
        return

    # 2. 跑自然语言路由
    intent = route_intent(text)
    skill_id = intent.get("skill_id")

    # 3. 角色权限校验
    allowed = user_config["allowed_skills"]
    if "*" not in allowed and skill_id not in allowed:
        send_card(event["chat_id"], "🚫 权限不足",
                  f"你的角色（{user_config['name']} · {user_config['role']}）"
                  f"不能用 {skill_id}。可用：{', '.join(allowed[:5])}...",
                  "red")
        return

    # 4. 执行 skill（在 P2P chat 里回复 = 只有该员工和机器人看到）
    execute_skill(skill_id, intent.get("params", {}),
                  event["chat_id"],  # P2P chat_id
                  event["message_id"],
                  user_context=user_config)
```

---

## 四、员工首次接入流程（30 秒）

```
员工小张 → 飞书顶部搜索框 → 搜「lark-fashion-cockpit」
  ↓ 找到机器人
  ↓ 点头像 → 「发起会话」
  ↓ 飞书自动建一个 1v1 私聊窗口（只有小张和机器人）

小张 → "你能帮我做啥"
机器人识别 → 不识别身份 → 回复"还没注册请找老板娘"

老板娘 → 飞书发"加员工权限：小张 ou_xxx 设计师"
event-listener → 自动加到 ROLE_REGISTRY → 写到 lib/team-config.json

小张 → 再次问"你能帮我做啥"
机器人 → "你是 设计师 角色，可以用：任务追踪 / 产品搭配 / 文档迭代 / ..."
```

---

## 五、与群聊模式共存

| 场景 | 用群聊 | 用 P2P 私聊 |
|---|---|---|
| 老板娘看店铺总览 | ✅ 老板群（团队都能看到，激励氛围）| ✅ 老板娘私聊（敏感利润数据）|
| 设计师查任务 | ❌（同事不需要看她的任务）| ✅ |
| 工厂催报量 | ✅（工厂群对账透明）| ❌ |
| 客户问题处理 | ❌（不能让客户被全员讨论）| ✅ |
| 老板分身（私密决策）| ❌ | ✅ |
| 直播复盘 | ✅ 直播组群（团队共建复盘）| ❌ |

机器人**两边都接管** — 同一个机器人，进群在群聊里活动，私聊在 P2P 里活动。

---

## 六、权限矩阵（5 大角色 × 35 个 skill）

详见 [`references/role-permissions.md`](./references/role-permissions.md)。

简表：
```
              老板  设计师  工厂  主播  客服  通用
morning-report  ✅    ✅     ✅    ✅    ✅    -
profit-analysis ✅    ❌     ❌    ❌    ❌    -    （仅老板可见）
launch-decision ✅    ❌     ✅    ❌    ❌    -
boss-clone-aily ✅    ❌     ❌    ❌    ❌    -    （仅老板，避免员工冒用）
product-library  ✅    ✅     ✅    ✅    ✅    -
task-tracker    ✅    ✅     ✅    -     ✅    -
private-domain  ✅    ❌     ❌    ❌    ✅    -
production-supp ✅    ❌     ✅    ❌    ❌    -
live-streaming  ✅    ❌     ❌    ✅    ❌    -
content-pipeline ✅    ❌     ❌    ❌    ❌    朱健豪
video-script-parser ✅ ❌    ❌    ❌    ❌    朱健豪 + 老板娘
opensource-radar  ✅   ❌    ❌    ❌    ❌    （仅老板 + 技术负责人）
helpdesk-customer-tickets ✅ ❌  ❌    ❌    ✅    -
lingo-fashion-glossary ✅   ✅   ✅    ✅   ✅    所有员工查词典
knowledge-base    ✅    ✅    ✅    ✅    ✅    通用
```

---

## 七、审计 + 老板娘可见性

老板娘虽然不能"偷看员工和机器人的聊天内容"（飞书原生隐私），但可以通过：
- `logs/trigger-log.jsonl`：记录每次触发（who / when / which skill / params）
- 飞书 base 25 张表的"创建人"字段：所有 skill 调用结果都自动归档

如果老板娘需要审查某员工活动：
```
老板娘 → "查申丽媛本周用了哪些 skill"
NLU → trigger-log 查询 → 飞书卡片汇报
```

---

## 八、典型私聊对话

```
设计师马萍蔓（自己手机飞书）→ 私聊机器人
"我这周交了几张稿"

NLU 识别: skill=task-tracker, params={owner: 我自己, period: this_week}
权限校验: ✅ 设计师可用 task-tracker
执行: lark-cli base +record-list 过滤 owner=马萍蔓 + 本周
回复: 个人卡片（只马萍蔓和机器人看到）

→ "本周您交付 12 张稿，平均交付 14m41s 提前。3 张被改稿..."
```

```
客服小红 → 私聊机器人
"赵姐昨天投诉那事咋办"

NLU 识别: skill=helpdesk-customer-tickets, params={customer: 赵姐}
权限校验: ✅ 客服可用 helpdesk
执行: 查 11_退货反馈 + 12_客户档案
回复: 赵姐档案 + 历史投诉 + AI 建议回复
```

---

## 九、身份模拟测试机制（owner 专属）

老板娘想测员工体验时不用真去找员工的飞书账号。直接发：

```
以XX身份 [指令]
以马萍蔓身份 我这周交了几张稿        → designer 视角
以申丽媛身份 巡检任务                → production 视角
以朱健豪身份 写文案                  → content 视角
```

机制：
- listener 解析 `^以(\S+)身份\s+(.+)$` → 切 user_config 成目标员工 + 该角色 allowed_skills
- 后续整套权限校验、夸夸称呼、trigger-log 都按目标员工身份处理
- **仅 owner 角色能用此模拟功能**（防员工冒用其他人身份）

## 十、夸夸文案动态称呼

PRAISE_OPENERS / FOOTERS / DONE 模板里"老板娘"是占位词，运行时按身份替换：
- `owner` → 保留"老板娘"
- `designer` (马萍蔓) → "萍蔓姐"
- `production` (申丽媛) → "丽媛姐"
- `content` (朱健豪) → "健豪"
- 其他 → 角色名（"工厂主管"/"主播"/...）

实现：`personalize_praise(text, user_config)` 函数 — listener 调用 send_card 前拦截替换。

## 十一、踩过的坑（比赛截止前一晚解决）

### 坑 1：listener 偷偷死掉 → 机器人无响应
**症状**：飞书发消息没回 + listener.log 没记录新消息
**原因**：你不小心关了那个跑 listener 的 PowerShell 黑窗口
**修复**：只能重启。**不要关那个黑窗口**（最小化 OK，关 X 就死了）

### 坑 2：JSON 解析 "Expecting value: line 1 column 1"
**症状**：自然语言路由一直回"识别异常"
**原因**：DeepSeek max_tokens=400 太短导致 JSON 截断
**修复**：max_tokens=800 + 加空响应检查 + raw_decode 容错

### 坑 3：PowerShell 5.1 调 native exe 时 JSON 引号被吃
**症状**：lark-cli 报"--content is not valid JSON: {tag:div,...}"（key 没引号）
**原因**：PowerShell 5.1 native command 处理 argv 时 strip 引号（已知 bug）
**修复**：用 `cmd /c "lark-cli ... --content `"$($cardJson -replace '"','""')`""` 让 cmd shell 处理引号转义

### 坑 4：skill_id 跟脚本名不一致
**症状**：发"配什么好" → product-matching-demo.ps1 → 但 role-registry 登记的是 product-matching → 设计师被错拒
**原因**：脚本命名不规范（带 -demo 后缀）
**修复**：listener 加 `SCRIPT_TO_SKILL_ID` 映射表，权限校验时标准化

### 坑 5：复制建议指令带额外文字 → 模拟身份失效
**症状**：发"现在测"以马萍蔓身份 ..." → 系统识别成 owner 不是 designer
**原因**：impersonate 正则要求消息**以**"以XX身份"开头
**修复**：教用户只复制纯指令，不带前后文

### 坑 6：早期 PoC 脚本只 print 不发卡片
**症状**：product-matching-demo.ps1 跑通但飞书私聊看不到具体推荐
**原因**：早期 PoC 脚本设计为"控制台 print"，没接 IM 卡片
**修复**：加 `-ReplyChatId` 参数 + 末尾用 cmd /c 包装的 lark-cli 发卡片

## 十二、参考

- 角色配置文件：[`scripts/role-registry.json`](./scripts/role-registry.json)
- 权限矩阵详细：[`references/role-permissions.md`](./references/role-permissions.md)
- 员工接入手册（30 秒图文）：[`examples/employee-onboarding.md`](./examples/employee-onboarding.md)
- event-listener 改造 patch：[`references/event-listener-p2p-patch.md`](./references/event-listener-p2p-patch.md)
