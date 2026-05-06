# 🚀 lark-fashion-cockpit · 电商航母驾驶舱

> **一句话定位：** 把"飞书 CLI 全套能力"+"AI 大脑"+"45 个垂直业务 skill"打包成**全员可用的本地驾驶舱**——任何员工打开浏览器跟系统聊天，就能查飞书数据、下达任务、通知合作方。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![飞书 CLI 创作者大赛](https://img.shields.io/badge/%E9%A3%9E%E4%B9%A6CLI-%E5%88%9B%E4%BD%9C%E8%80%85%E5%A4%A7%E8%B5%9B-orange)](https://github.com/larksuite/cli)
[![45 sub-skill](https://img.shields.io/badge/sub--skill-45%20%E4%B8%AA%E8%87%AA%E5%8C%85%E5%90%AB-blue)](#-45-个-skill-清单详细痛点--解决方案)
[![已实测](https://img.shields.io/badge/%E5%B7%B2%E5%AE%9E%E6%B5%8B-真朋友真任务真完成-brightgreen)](./examples/01-real-launch-demo.md)

![架构图](./docs/images/architecture.svg)

---

## 🤔 为什么做这个项目

### 老板娘真实痛点

> *"我每天早上 8 点起来，要看 4 个平台的销售数据（淘宝/抖音/小红书/视频号）、看库存预警、跟工厂催货、给设计师派活、看竞品博主新视频、回客户消息……每件事都在不同的工具里，光切换窗口就累死。"*

经营一家女装品牌，**信息散落在 8 个工具**：
- 飞书（团队协作）
- 个人微信（朋友型供应商）
- 企业微信（合作方）
- 4 个电商后台
- 抖音 / 小红书博主监控
- ……

她需要一个**统一指挥台**，最好长这样：

> *"打开浏览器跟系统说话，它帮我把事情办了。"*

### 为什么飞书 CLI 是答案

飞书 CLI 已经把「base / im / task / calendar / docs / drive / vc / minutes / approval / okr / mail / contact / ……」全做成命令行能力了。问题是：

- ❌ 老板娘**不会写**命令行
- ❌ 员工**没法**直接用 CLI
- ❌ 多个 CLI 命令**怎么编排**？

答案：**用 AI 翻译"人话"成 CLI 调用**。

---

## 📐 项目板块构成（一图读懂）

| 板块 | 干什么 | 包含 skill 数 |
|---|---|---|
| 🚀 **入口层** | 用户跟系统交互的界面：本地驾驶舱网页 + 常驻 AI 聊天浮窗 | 4 个 |
| 📊 **经营数据** | 产品/销售/库存/利润/上新决策的飞书 base + AI 分析 | 11 个 |
| 📱 **跨平台 IM** | 把飞书、企业微信、个人微信串起来的"统一收发系统" | 5 个 |
| 🎬 **内容营销** | 博主监控、竞品监控、二创脚本、直播、私域、视频脚本拆解 | 7 个 |
| 🎯 **任务协作** | 任务/审批/OKR/会议/早报/履约/客服工单——团队协同枢纽 | 12 个 |
| 🤖 **AI 大脑 + 基础设施** | 自然语言路由、调度、知识库、词汇表、事件路由 | 6 个 |

**合计 45 个 self-contained sub-skill**，每个都能 `npx skills add` 单独安装。

---

## 📦 安装与启动

### 快速开始

```bash
# 1. 装 lark-cli 主程序
npm install -g @larksuite/cli

# 2. 装本仓库 45 个 sub-skill（一次性）
npx skills add fxl1209739475-fxl/lark-fashion-cockpit -g -y

# 3. 配置环境变量
git clone https://github.com/fxl1209739475-fxl/lark-fashion-cockpit
cd lark-fashion-cockpit
cp .env.example .env
# 然后填 DOUBAO_API_KEY / DEEPSEEK_API_KEY / 飞书 base token / 等

# 4. 一键初始化飞书 base（建 27 张表 schema + 字段 + mock 演示数据）
python scripts/init-cockpit.py

# 5. 启动驾驶舱（本地 Web 系统 + 聊天浮窗）
./start-omnitask.bat
# 浏览器访问 http://localhost:8080
```

> ⚠️ **装 skill ≠ 自动建表**。skill 是后端处理逻辑，飞书 base 数据需要 step 4 单独初始化。

---

## 🎯 核心场景演示

### 场景 1：早 8:00 自动跨渠道情报早报

```
auto-scheduler 每天早 8:00 触发 morning-report
  ↓
并发拉：
  ├─ 飞书：昨日团队群 @我 + 待办（lark-im + lark-task）
  ├─ 企微：昨日核心客户消息（wecom-bridge → sync-history）
  └─ 个微：扫主窗口红点（wechat-monitor → scan-wechat）
  ↓
DEEPSEEK 三路情报合并 → 一张早报卡片到老板娘飞书
  ↓
"昨晚 ZC 工厂群 @你说 DRS-0429 雪纺面料卡了，朱健豪发了脚本 V2 待审..."
```

### 场景 2：跟驾驶舱说人话办事

```
老板娘在浏览器聊天框输入：
"通知 ZC 工厂 DRS-0429 雪纺面料下周一前能不能交货"

→ DEEPSEEK 识别 notify.supplier，提取 supplier="ZC 工厂"
→ 路由到 wxauto-supplier-bridge
→ 自动给 ZC 工厂发微信通知（含审计 log）
→ 飞书卡片："✓ 已发给 ZC 工厂浙江老张，对方已读"
```

### 场景 3：基于实时飞书数据的 AI 分析

```
聊天窗口："找出售罄率低于 50% 的产品，按春夏秋冬分类"

→ 路由到 query.product_analysis
→ lark-cli 拉 01_产品库 实时数据（80 条）
→ DEEPSEEK 分析

返回：
【结论】共 3 个 SKU 售罄率 < 50%：NO.008（春夏，40%）+ NO.006/007（开发中）
【数据支撑】
- NO.008 OL极简通勤西服：售罄率 40%，库存 180 件
- ...
【建议】
1. NO.008 立即启动促销 + 加强通勤场景推广
2. NO.006/007 加快开发进度，提前预售
3. 春夏 NO.001/004 控制补货节奏
```

---

## 📋 45 个 skill 清单（详细痛点 + 解决方案）

### 🚀 入口层（4 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **omnitask-bridge** ⭐ | 飞书 CLI 能力强但门槛高，老板娘和员工都不会用命令行；41 个后端 skill 是"散装能力"没有产品形态 | 本地 Web 驾驶舱（FastAPI 8080）+ 常驻聊天浮窗 + DEEPSEEK 自然语言路由，把所有 skill 包装成"任何人打开浏览器跟系统说话就能用" |
| **natural-language-router** | 老板娘飞书发"扫微信群"和"看下微信谁找我"是同一意思，关键词路由覆盖不全 | DEEPSEEK V4 Flash 把模糊指令分类到 query/task/notify/content/doc/calendar/casual 七类，路由到对应 skill |
| **multi-user-private-channels** | 不同角色（老板/设计师/生产/内容）应该有不同权限，不能员工冒用老板身份触发"通知供应商" | role-registry 角色权限矩阵，每个 skill 标注 scopes_required，调用前校验，支持"以 XX 身份"模拟测试 |
| **workplace-block-cockpit** | 飞书工作台缺少专门服装电商场景的"经营驾驶舱"区块 | 自定义飞书工作台 block，把日报/库存/上新进度内嵌在飞书首页 |

### 📊 经营数据（11 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **product-library** | 服装电商一个 SKU 涉及"颜色 × 尺码 × 款式 × 平台"复合属性，普通表格描述不全 | 飞书多维表格 27 字段产品库 schema：颜色矩阵 / 尺码做货单 / 售罄率 / 退货率 / 4 平台分配 / 状态 |
| **product-graph** | 产品之间的搭配关系（"上衣 A 配下装 B"）拍脑袋，没有结构化记录 | 17_产品搭配组 表 + 搭配评分 + 销售关联度统计，找出最佳搭配组合 |
| **product-matching** | 新品上线时不知道老款里哪些可以搭配卖，凭印象拍脑袋 | 基于颜色 / 风格 / 价格区间向量化匹配老款，输出"最佳搭配 Top 5" |
| **base-extension-product-matcher** | product-matching 的扩展能力（base 字段公式自动联动） | 飞书 base 字段联动公式：上新一个新品 → 自动跑 matching → 写入 17_搭配组 |
| **stock-replenishment** | 4 平台库存分散在不同后台，断货才发现已经晚了 | 03_库存预警 表 + 安全线公式 + 紧急度自动着色（紧急 / 中），库存 < 安全线立刻飞书卡片报警 |
| **platform-analytics** | 4 平台销售数据各自有报表，老板要拼半天才看清全局 | 02_4平台销售 表 + AI 拼图分析（"今天哪个平台贡献了利润大头"）|
| **profit-analysis** | 销售额好不等于赚钱，光看销售忽略毛利和退货成本 | 综合销售-退货-成本-推广-人工 → 每 SKU 真实利润 + 全店日均利润趋势 |
| **target-tracking** | 季度销售目标定了之后没人盯，到月底才发现差距大 | 13_OKR 表追踪季度/月度/周目标进度，自动算"距目标还需实销 X 件" |
| **launch-decision** | 设计师把方案 A/B/C 摆出来，老板娘凭感觉选，事后发现 D 更好 | 给每个候选方案打综合分（成本/卖相/工艺/竞品对标），AI 给出推荐 + 理由 |
| **new-launch-planning** | 一年 6 波上新（春夏 / 秋冬 / 节庆），节奏混乱，每次临时抓瞎 | 04_上新波段 表预排全年节奏 + 自动倒推每个 SKU 的设计 / 打版 / 生产 deadline |
| **production-supplier** | 工厂任务靠微信群口头沟通，谁负责什么没记录，出问题甩锅 | 09_生产档案 表关联工厂 / 排期 / 进度 / 质量评分 + wxauto-supplier-bridge 自动通知 |

### 📱 跨平台 IM（5 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **cross-platform-im-agent** ⭐ | 客户散落在飞书 / 企微 / 个微，三个 inbox，每天切换累死 | 总指挥层：飞书一句话指令 → 同时调度三条 IM 链路 + 跨渠道扫摘要早报 |
| **wechat-monitor** | 工作微信群多消息密集，每天看不过来；wxauto 等桌面 RPA 受 Win11 焦点限制不可靠 | 4 路径覆盖：① 主窗口扫红点（自动）② 长截图 AI 总结（半自动主推）③ 第三方导出 .txt 总结 ④ 桌面 RPA（实验性） |
| **wxauto-supplier-bridge** | 一天问 5 个面料商同样的问题手敲 5 次，切微信浪费时间 | 飞书一句话 → wxauto 控制 PC 微信 → 给指定供应商发消息（4 层风控：仅 owner / 白名单 / 限速 / 审计）|
| **wecom-bridge** | wxauto 和数据库 dump 都受微信版本兼容 + 安全告警限制，B 端通讯不够稳 | 走企业微信合规 API：注册 → 启用客户联系 → API 拉历史 + 发消息（48h 主动窗口内无限）|
| **personal-mirror** | 员工日报手动写流于形式，老板看不到真实工作流程 | 22:00 自动拉员工飞书活动（任务/IM/会议）→ AI 4 维分析 → 生成"今日真实贡献"个人镜像 |

### 🎬 内容营销（7 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **blogger-monitor** | 对标博主每天发新视频但没人盯，错过 100k+ 爆款选题 | 27_对标博主视频监控 表 + Deepseek 评分（女装关联度 / 学习价值 / 二创可行性）|
| **competitor-monitor** | 竞品上新一波你不知道，价格调整你也不知道 | 16_竞品产品监控 表自动跑 + 飞书 IM 关键词命中报警（"XX 品牌新上 50 款 春夏系列"）|
| **content-pipeline** | 选题→脚本→拍摄→剪辑→发布 5 步散在不同人手里，进度看不清 | 06_选题池 + 07_文案库 + 24_直播记录 表全链路追踪 + 卡点 alert |
| **video-script-parser** | 看到爆款想二创，但仔细分析镜头/台词/节奏要花 1 小时 | yt-dlp 拉视频 + faster-whisper 转录 + DOUBAO 多模态拆解 5 维度（镜头/台词/视觉/声音/节奏）|
| **live-streaming** | 直播场次数据 / 主推款 / 投流 / 转化分散，每场复盘要从 4 个工具拼数 | 21/22/23/24 表全链路：场次数据 / 主推款 / 投流 / 完整记录 + AI 复盘建议 |
| **private-domain** | 客户加了微信但没分层，全部当成一类发广告，转化低 | 10_客户分层 表（高价值/普通/沉睡）+ 不同分层不同消息节奏 |
| **opensource-radar** | 想用 AI 工具但天天有新项目出来不知道哪些适合女装电商 | 每日 GitHub trending 抓取 + DeepSeek 评估女装电商相关性 → 飞书卡片推荐 |

### 🎯 任务协作（12 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **task-collaboration** | 跨租户朋友帮忙时飞书 P2P 私聊不通，IM API 返回 230038 | 用飞书原生任务/审批/日历通知绕开 IM 限制，跨租户协作走任务而不是私聊 |
| **task-lifecycle** | 任务建好就忘了，没人跟进进度直到 deadline 当天才慌 | 任务全生命周期追踪：建立 → 接受 → 进行中 → 卡点 → 完成 → 复盘，自动提醒 |
| **approval-flow** | 报销 / 批价 / 上新审核 走线下，凭口头/微信记录，找半天找不到 | 飞书审批 API + 14_审批记录 表自动归档，所有决策可追溯 |
| **okr-cascade** | 季度 OKR 定了之后没在日常工作里体现，到月底对不上 | 13_OKR 表 + 任务 / 销售 / 库存自动关联到对应 KR，进度可视化 |
| **morning-report** ⭐ | 每天起床要打开 5 个工具看昨天发生了啥，浪费 30 分钟 | 早 8:00 自动跑：拉飞书 + 企微 + 个微 + 销售 + 库存 + 任务 → 一张早报卡片 |
| **personal-mirror** | 员工日报敷衍了事，老板分不清真假努力 | 22:00 自动拉员工飞书一天行为 → AI 4 维分析（任务推进/沟通密度/会议参与/重点产出）|
| **meeting-workflow** | 会议结束没纪要，决议执行无人跟进 | 飞书妙记 + 18_会议决策 表 + 决议自动转任务 + 跟进者每周复盘 |
| **meeting-broadcaster** | 重要会议结论想同步给没参会的人，手动转发 5 个群很麻烦 | 一键把会议纪要广播到指定的飞书群 / 个人，附带 AI 生成的 3 句话精简版 |
| **meeting-clip-extractor** | 1 小时会议视频回看太累，找具体片段要拖进度条 | 妙记 AI 章节 + 关键词锚点提取，"播放 14:30 - 16:00 决策那段"一句话搞定 |
| **feedback-returns** | 退货反馈散在客服记录里，质量问题相同 SKU 反复出现没人发现 | 11_退货反馈 表自动聚合 + 同款 ≥ 3 退货飞书报警 + 自动通知工厂 |
| **order-fulfillment** | 4 平台订单履约状态分散，缺货 / 延迟发货后置发现 | 全平台订单状态 + 异常单自动飞书任务给客服跟进 |
| **helpdesk-customer-tickets** | 客户问题在微信 / 飞书 / 平台客服三个口同时进来，处理乱 | 飞书 helpdesk 工单 + 自动分流 + AI 自动回复常见问题 + 升级时转人 |

### 🤖 AI 大脑 + 基础设施（6 个）

| Skill | 痛点 | 解决方案 |
|---|---|---|
| **boss-clone-aily** | 老板出差 / 度假时同事问她"这个怎么处理"找不到答案 | 飞书 Aily 应用 + 26_老板语料库（历史决策案例 + 风格语料）→ 老板克隆 AI 替她答 |
| **skill-recommender** | 45 个 skill 用户不知道哪个解决他的问题 | DEEPSEEK 看用户描述 → 推荐最匹配的 3 个 skill + 一行示例命令 |
| **auto-scheduler** | 12 个定时任务（早报 / 库存扫 / 博主抓 等）散在不同 cron / 手动起，状态看不清 | APScheduler 主调度器 + config/auto-triggers.json 集中管理 + 状态可视化 |
| **knowledge-base** | 公司经验沉淀在群聊和会议纪要里，新员工查询要问 5 个人 | 19_经验沉淀库 表 + 飞书 wiki 联动 + 向量检索 |
| **lingo-fashion-glossary** | 服装行业黑话（"色号 / 版型 / 安全线 / 上新波段"）跨部门理解不一致 | 飞书 lingo 服装词汇表，新员工 / 跨租户朋友看到术语就能查 |
| **event-router** | 飞书事件回调（消息 / 群变更 / 反应）多种类型，每个 skill 都自己处理太重 | 统一事件路由层 + 按类型分发到对应 skill，新增 skill 只需注册路由 |
| **doc-iterator** | 飞书文档要批量改（比如 100 个产品 SOP 加一段免责声明），手动改累死 | DocxXML 批量更新 API + 失败回滚 + 进度追踪 |

---

## 📂 关键架构文件

```
lark-fashion-cockpit/
  ├─ skills/                            # 45 个 sub-skill 自包含
  │   ├─ omnitask-bridge/               # ⭐ 入口：驾驶舱 + 聊天 + AI 路由
  │   │   ├─ web/                       # 前端（FastAPI serve）
  │   │   │   ├─ index.html             # 主驾驶舱
  │   │   │   ├─ chat.js                # 常驻聊天浮窗
  │   │   │   └─ creator/               # 嵌入创作系统
  │   │   ├─ scripts/
  │   │   │   ├─ server.py              # FastAPI 8080 + WebSocket
  │   │   │   ├─ chat_router.py         # DEEPSEEK 意图分类
  │   │   │   ├─ skill_executor.py      # subprocess 调 skill
  │   │   │   └─ feishu_data.py         # lark-cli 数据查询
  │   │   └─ config/skills-registry.json # 12 个可被聊天调用的 skill
  │   ├─ wechat-monitor/                # 个人微信 4 路径
  │   ├─ wecom-bridge/                  # 企业微信 API
  │   ├─ cross-platform-im-agent/       # 跨平台 IM 编排
  │   └─ ... (41 个其他 skill)
  ├─ scripts/
  │   ├─ event-listener.py              # 飞书 IM 消息监听 + 路由分发
  │   └─ init-cockpit.py                # 一键建 27 张表 + mock 数据
  ├─ docs/images/architecture.svg       # 本 README 的大图
  ├─ start-omnitask.bat                 # 一键启动驾驶舱
  └─ .env.example                       # 环境变量模板
```

---

## 🔑 必备的环境变量

参考 `.env.example`：

```bash
# AI 模型
DOUBAO_API_KEY=ark-xxxxx          # 火山方舟，视觉模型用
DOUBAO_MODEL=doubao-1-5-vision-pro-32k-250115
DEEPSEEK_API_KEY=sk-xxxxx         # DEEPSEEK，路由+总结用
DEEPSEEK_MODEL=deepseek-chat

# 飞书 base
LARK_FASHION_COCKPIT_BASE_TOKEN=...
LARK_FASHION_COCKPIT_BOSS_CHAT=oc_...
LARK_FASHION_COCKPIT_BOSS_OPEN_ID=ou_...

# 飞书表 ID（init-cockpit.py 自动建表后填）
TABLE_PRODUCT_LIBRARY=tblxxxxx
TABLE_SALES_4PLATFORMS=tblxxxxx
TABLE_STOCK_ALERT=tblxxxxx
... (共 27 张)

# 抖音爬虫
DOUYIN_COOKIE=...
```

---

## 🎬 5 分钟跑通的演示路径

1. 装好依赖（参考"安装与启动"）
2. 启动 `./start-omnitask.bat` → 浏览器打开 http://localhost:8080
3. 看到女装驾驶舱 + 右下角 💬 浮窗
4. 点 💬 浮窗，依次发送：
   - `今天销售` → 自动拉飞书销售表
   - `库存预警` → 自动列出红色 SKU
   - `今天会议` → 自动列今日日程
   - `找出售罄率低于50%的产品` → 拉产品库 + AI 结构化分析
   - `让设计师汇报本周进度` → 自动建任务 + 指派给马萍蔓
5. 每条指令的执行进度会实时流式显示在浮窗里

---

## 🤝 数据隐私声明

- 所有飞书 base 数据**保留在你自己的飞书租户**，不上传第三方
- AI 调用走 DEEPSEEK / DOUBAO 官方 API，不缓存对话内容
- 个人微信桥（wechat-monitor / wxauto）所有截图**用完即丢不写盘**
- 企业微信桥（wecom-bridge）走腾讯官方合规 API
- 审计日志统一记 `logs/`，仅本地可见

---

## 🆘 反馈 / 报问题

GitHub issues：https://github.com/fxl1209739475-fxl/lark-fashion-cockpit/issues

---

## 📜 License

MIT License — 自由商用 / 改造 / 分发。
