---
name: lark-fashion-cockpit-omnitask-bridge
version: 1.0.0
description: "全员 ChatOps 驾驶舱 — 一个本地前端系统，把 cockpit 41 个后端 skill + 飞书 CLI 全套能力整合在一个浏览器界面里。任何员工都能跟系统聊天 → AI 翻译 → 飞书 CLI 执行。当用户说「打开驾驶舱」「跟系统聊天」「全员可用的指挥台」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["fastapi", "uvicorn", "openai", "python-dotenv"]
    env: ["DEEPSEEK_API_KEY", "LARK_FASHION_COCKPIT_BASE_TOKEN", "LARK_FASHION_COCKPIT_BOSS_OPEN_ID"]
---

# Omnitask Bridge · 全员 ChatOps 驾驶舱

> **🎯 核心定位：** cockpit 已有 41 个后端 skill，但**之前只能通过飞书私聊触发**。
> 本 skill 把 cockpit 升级成 **完整的本地 Web 系统** —— 全公司任何人都能在浏览器里跟系统聊天、查数据、下任务。
>
> **故事：** "我们做了一个产品 — 老板和员工打开浏览器就能用，跟它聊天就能调动飞书全部能力。它的大脑是 AI，渠道是飞书 CLI，能力来自 cockpit 41 个 skill。"

---

## 一、它能做什么

### 任何员工打开 http://localhost:8080

主页是**女装电商驾驶舱**（产品库 / 销售 / 库存 / 任务 / 博主监控 / 内容 / 营销 / 供应链 五大区 20+ 模块），右下角常驻 **💬 聊天窗口**。

### 用户跟聊天窗口说话 → 系统自动办

```
"今天销售如何？"
  ↓
AI 识别 query.sales_today
  ↓ 调 lark-cli base 拉 02_4平台销售 表
  ↓
"今日总销售额 ¥45,820，订单 87 单。淘宝 ¥21k / 抖音 ¥18k / 小红书 ¥4.5k / 快手 ¥2k。"
```

```
"通知 ZC 工厂 DRS-0429 雪纺面料下周一前能不能交货"
  ↓
AI 识别 notify.supplier，提取 supplier="ZC 工厂"、message="..."
  ↓ 调 wxauto-supplier-bridge / wecom-bridge
  ↓
"⚙ 已发给 ZC 工厂的浙江老张  ✓ 对方已读"
```

```
"建一个任务给马萍蔓让她出 5 个 DRS-0429 同款方案"
  ↓
AI 识别 task.create，提取 assignee="马萍蔓"
  ↓ 调 lark-cli task +create + assign
  ↓
"✓ 任务已创建并指派给 马萍蔓"
```

```
"今天我有几个会？"
  ↓ 调 lark-cli calendar +agenda
  ↓
"今天 3 场：10:00 设计评审 / 14:00 供应商对接 / 16:30 与朱健豪 1on1"
```

---

## 二、产品架构

```
浏览器 http://localhost:8080
  │
  └──→ FastAPI server.py (Python, 8080)
         │
         ├─ /                    → web/index.html（女装驾驶舱）
         ├─ /chat.js + chat 浮窗 → 常驻聊天 UI
         ├─ /creator             → web/creator/（嵌入创作系统）
         ├─ /creator-api/*       → 反代 douyin-monitor:8000
         ├─ /api/health|skills   → 自身元数据
         │
         └─ WS /ws/chat          → 聊天 WebSocket 入口
              │
              └→ chat_router.py（DEEPSEEK V4 解析意图）
                   │
                   ├→ 关键词快速匹配 skills-registry.json
                   ├→ AI 分类：query|task|notify|content|doc|calendar|casual
                   ├→ skill_executor.py 调具体 skill
                   │    ├ subprocess 调 cockpit/skills/*/scripts/*.py
                   │    └ 流式回报执行进度（skill_log / skill_done）
                   └→ DEEPSEEK 把 skill 输出翻译成自然语言回复
```

---

## 三、文件清单

| 文件 | 用途 | 状态 |
|---|---|---|
| `web/index.html` | 女装驾驶舱主页（含聊天浮窗注入） | ✅ |
| `web/app.js` | 主页交互逻辑（继承自 fashion-admin-demo） | ✅ |
| `web/styles.css` | 样式 + 聊天浮窗样式 | ✅ |
| `web/chat.js` | 聊天窗口前端（WebSocket 客户端） | ✅ |
| `web/creator/index.html` | 创作系统子页（继承 douyin-monitor） | ✅ |
| `scripts/server.py` | FastAPI 主服务（端口 8080） | ✅ |
| `scripts/chat_router.py` | DEEPSEEK 意图分类 + skill 路由 | ✅ |
| `scripts/skill_executor.py` | subprocess 调 skill + 流式回报 | ✅ |
| `scripts/feishu_data.py` | lark-cli 数据查询封装 | ✅ |
| `config/skills-registry.json` | 11 个可被聊天调用的 skill 注册表 | ✅ |
| `start-omnitask.bat` | 一键启动脚本 | ✅ |

---

## 四、启动方式

```bash
# 安装依赖
pip install fastapi uvicorn openai python-dotenv

# 一键启动
./start-omnitask.bat

# 或手动启动
python skills/omnitask-bridge/scripts/server.py

# 浏览器访问
http://localhost:8080
```

如果要用创作系统（/creator 路径），同时启动 douyin-monitor 后端：

```bash
# 另开 PowerShell
cd C:\Users\冯兴龙\douyin-monitor
python server.py    # 端口 8000
```

---

## 五、可被聊天调用的 11 个 skill（v1.0）

| skill_id | category | 触发词 | 调用底层 |
|---|---|---|---|
| query.sales_today | query | "今天销售" | feishu_data → 02_4平台销售 |
| query.stock_alerts | query | "库存预警" | feishu_data → 03_库存预警 |
| query.my_tasks | query | "我的待办" | lark-cli task +get-my-tasks |
| query.bloggers_top | query | "对标博主爆款" | feishu_data → 27_对标博主视频 |
| task.create | task | "建任务" | lark-cli task +create + assign |
| notify.supplier | notify | "通知 XX 工厂" | wxauto-supplier-bridge |
| notify.broadcast_supplier | notify | "问所有面料商" | wxauto-supplier-bridge |
| wechat.scan | notify | "扫微信群" | wechat-monitor |
| content.generate_script | content | "写脚本" | 跳转创作系统 |
| doc.create | doc | "建文档" | lark-cli docs +create |
| calendar.today | calendar | "今天会议" | lark-cli calendar +agenda |

后续可以**直接在 `config/skills-registry.json` 加新 skill**，不需要改代码。

---

## 六、安全 & 多用户（v1 & 后续）

**v1 当前**：单用户（owner）模式，假设跑在老板电脑上。

**v2 计划**：
- 飞书 OAuth 登录
- `config/users.json` 多角色权限矩阵（owner / designer / production / content / staff）
- skill 调用前校验 `scopes_required`
- 每条聊天落 audit log

---

## 七、与 cockpit 已有 skill 的关系

本 skill 是 **聚合层** —— 不重复实现已有能力，只编排：

```
omnitask-bridge
   │
   ├ 调用 wxauto-supplier-bridge   (主动发微信)
   ├ 调用 wechat-monitor           (扫红点 / 长图总结)
   ├ 调用 wecom-bridge             (企微 API)
   ├ 调用 cross-platform-im-agent  (跨平台编排)
   ├ 调用 task-collaboration       (跨租户任务)
   ├ 调用 morning-report           (早报)
   └ 调用 lark-cli 全套（im/base/task/calendar/docs/drive/...）
```

cockpit = 41 个 skill 的"工具箱"。omnitask-bridge = 把工具箱包装成"产品形态"。

---

## 八、为什么这是 cockpit 的"封面"

之前 cockpit 的 41 个 skill，对评委来说是"散装能力"。本 skill 把它们装进一个**任何人打开就能用的浏览器系统**：

- ✅ 不需要懂飞书 CLI
- ✅ 不需要会发指令格式（"扫微信群 关键词=DRS-0429"）—— 直接说人话
- ✅ 不只老板用，全员都能用
- ✅ 看着驾驶舱数据 + 跟聊天框说话 = 完整的"经营指挥台"体验

**这才是 cockpit 比赛能讲清楚的故事**。
