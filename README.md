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

## 📋 45 个 skill 清单（痛点 / 解决方案 / 演示案例）

每个 skill 用 **3 行小卡片** 展示：痛点是什么、怎么解决、典型用法举例。

> 标 ⭐ 是主推 skill。⭐ skill 还配了独立的效果演示图，往下翻看 [效果演示图](#-核心-skill-效果演示)。

### 🚀 入口层（4 个）

#### ⭐ omnitask-bridge — 全员 ChatOps 驾驶舱
- **痛点**：飞书 CLI 能力强但门槛高，老板娘和员工都不会用命令行；45 个后端 skill 是"散装能力"没有产品形态
- **解决**：本地 Web 驾驶舱（FastAPI 8080）+ 常驻聊天浮窗 + DEEPSEEK 自然语言路由，把所有 skill 包装成"任何人打开浏览器跟系统说话就能用"
- **演示**：老板娘浏览器聊天框输入 `今天销售如何？` → AI 路由到 query.sales_today → 拉飞书 02 表 → 浮窗回复"今日总销售 ¥45,820，淘宝 ¥21k 占 46%"

#### natural-language-router
- **痛点**：老板娘说"扫微信群"和"看下微信谁找我"是同一意思，关键词路由覆盖不全
- **解决**：DEEPSEEK V4 Flash 把模糊指令分类到 query/task/notify/content/doc/calendar/casual 七类，再路由到对应 skill
- **演示**：员工发 `帮我看一眼今天微信里的事儿` → AI 识别 = wechat.scan → 调扫描器 → 5 秒后回卡片

#### multi-user-private-channels
- **痛点**：不同角色（老板/设计师/生产/内容）应该有不同权限，不能员工冒用老板身份触发"通知供应商"
- **解决**：role-registry 角色权限矩阵，每个 skill 标注 scopes_required，调用前校验
- **演示**：设计师马萍蔓飞书发 `通知 ZC 工厂明天交货` → 校验 designer 没有 notify.supplier 权限 → 拒绝并提示"该指令仅老板可用，请告知她"

#### workplace-block-cockpit
- **痛点**：飞书工作台缺少专门服装电商场景的"经营驾驶舱"区块
- **解决**：自定义飞书工作台 block，把日报/库存/上新进度内嵌在飞书首页
- **演示**：老板娘早上打开飞书工作台 → 第一屏看到「DRS-0429 库存 5 件，紧急补货」+ 「本周上新进度 6/10 完成」

---

### 📊 经营数据（11 个）

#### product-library
- **痛点**：服装电商一个 SKU 涉及"颜色 × 尺码 × 款式 × 平台"复合属性，普通表格描述不全
- **解决**：飞书多维表格 27 字段产品库 schema：颜色矩阵 / 尺码做货单 / 售罄率 / 退货率 / 4 平台分配 / 状态
- **演示**：设计师在 01_产品库 录入新 SKU "DRS-0501-FL" → 自动生成 5 色 × 5 码做货单（25 个子 SKU）+ 4 平台分配栏

#### product-graph
- **痛点**：产品之间的搭配关系（"上衣 A 配下装 B"）拍脑袋，没有结构化记录
- **解决**：17_产品搭配组 表 + 搭配评分 + 销售关联度统计，找出最佳搭配组合
- **演示**：老板娘问 `这件外套配什么裤子卖得最好` → 拉 17 表搭配组 → "PNT-0418-SU 黑色（搭配评分 92，关联销售 +35%）"

#### product-matching
- **痛点**：新品上线时不知道老款里哪些可以搭配卖，凭印象拍脑袋
- **解决**：基于颜色 / 风格 / 价格区间向量化匹配老款，输出"最佳搭配 Top 5"
- **演示**：上新 DRS-0501 → 自动跑 matching → 17 表新增"DRS-0501 + PNT-0418 + KNT-0402"3 个搭配组（评分 90 / 87 / 81）

#### base-extension-product-matcher
- **痛点**：product-matching 单跑要手动触发，没在飞书 base 里自动联动
- **解决**：飞书 base 字段联动公式：上新或修改 SKU 颜色/价格 → 自动重跑 matching → 17 表实时更新
- **演示**：把 KNT-0402 颜色从焦糖改奶白 → 公式触发 → 30 秒后 17 表搭配组重新计算

#### ⭐ stock-replenishment
- **痛点**：4 平台库存分散在不同后台，断货才发现已经晚了
- **解决**：03_库存预警 表 + 安全线公式 + 紧急度自动着色，库存 < 安全线立刻飞书卡片报警
- **演示**：系统每 30 分钟扫 03 表 → SKT-0328-A 库存 5 / 安全线 30 → 飞书红色卡片"🚨 紧急补货 SKT-0328-A，建议补 350"

#### platform-analytics
- **痛点**：4 平台销售数据各自有报表，老板要拼半天才看清全局
- **解决**：02_4平台销售 表 + AI 拼图分析
- **演示**：老板娘问 `今天哪个平台贡献最多` → AI 拉 02 表 → "抖音 ¥18k 占 45%，但客单价最低 ¥189，淘宝才是利润王"

#### profit-analysis
- **痛点**：销售额好不等于赚钱，光看销售忽略毛利和退货成本
- **解决**：综合销售-退货-成本-推广-人工 → 每 SKU 真实利润 + 全店日均利润趋势
- **演示**：老板娘问 `DRS-0429 真实利润` → "客单价 299，扣退货+成本+推广 87 元，毛利率 29%（行业平均 25% ✓）"

#### target-tracking
- **痛点**：季度销售目标定了之后没人盯，到月底才发现差距大
- **解决**：13_OKR 表追踪季度/月度/周目标进度，自动算"距目标还需实销 X 件"
- **演示**：每周日 9:00 系统自动报 → "本月销售目标完成 78%，距目标差 ¥120k，建议重点推 DRS-0501（毛利最高）"

#### launch-decision
- **痛点**：设计师把方案 A/B/C 摆出来，老板娘凭感觉选，事后发现 D 更好
- **解决**：给每个候选方案打综合分（成本 / 卖相 / 工艺难度 / 竞品对标）
- **演示**：上新评审 → 设计师上传 5 个候选方案 → AI 综合评分 → "推荐 B 方案：成本低 12%，竞品同款率 70%，预期毛利率 32%"

#### new-launch-planning
- **痛点**：一年 6 波上新（春夏 / 秋冬 / 节庆），节奏混乱，每次临时抓瞎
- **解决**：04_上新波段 表预排全年节奏 + 自动倒推每个 SKU 的设计 / 打版 / 生产 deadline
- **演示**：老板娘问 `5 月底前要上新哪些款` → "10 个 SKU，设计完成 6 个，打版完成 4 个，3 个卡在 ZC 工厂工艺确认"

#### production-supplier
- **痛点**：工厂任务靠微信群口头沟通，谁负责什么没记录，出问题甩锅
- **解决**：09_生产档案 表关联工厂 / 排期 / 进度 / 质量评分 + wxauto-supplier-bridge 自动通知
- **演示**：系统看 09 表 → ZC 工厂 DRS-0429 进度 80% / 还剩 2 天交期 → 自动飞书提醒 + 微信通知工厂"明天进展确认"

---

### 📱 跨平台 IM（5 个）

#### ⭐ cross-platform-im-agent
- **痛点**：客户散落在飞书 / 企微 / 个微，三个 inbox，每天切换累死
- **解决**：总指挥层：飞书一句话指令 → 同时调度三条 IM 链路
- **演示**：老板娘 `扫所有渠道 24h` → 并发拉飞书 + 企微 + 个微 → 一张大卡片汇总"飞书 12 条/企微 3 条/个微 5 条紧急消息"

#### ⭐ wechat-monitor
- **痛点**：工作微信群多消息密集，每天看不过来；wxauto 等桌面 RPA 受 Win11 焦点限制不可靠
- **解决**：4 路径覆盖：① 主窗口扫红点 ② 长截图 AI 总结 ③ 第三方导出 .txt 总结 ④ 桌面 RPA（实验性）
- **演示**：老板娘 `扫微信群` → 截图主窗口 → DOUBAO 识别 → "ZC 工厂群 [12] @你 5 条消息：DRS-0429 雪纺面料卡在染色环节，预计延 2 天"

#### ⭐ wxauto-supplier-bridge
- **痛点**：一天问 5 个面料商同样的问题手敲 5 次，切微信浪费时间
- **解决**：飞书一句话 → wxauto 控制 PC 微信 → 给指定供应商发消息（4 层风控）
- **演示**：老板娘 `通知 ZC 工厂 DRS-0429 加急` → wxauto 自动给浙江老张发微信 → 飞书回执"✓ 已发，对方已读"

#### wecom-bridge
- **痛点**：wxauto 和数据库 dump 都受微信版本兼容 + 安全告警限制，B 端通讯不够稳
- **解决**：走企业微信合规 API：注册 → 启用客户联系 → API 拉历史 + 发消息（48h 主动窗口内无限）
- **演示**：客户 X 主动咨询 → 触发 48h 窗口 → cockpit 自动用企微 API 回 5 条跟进消息（不限额度）

---

### 🎬 内容营销（7 个）

#### ⭐ blogger-monitor
- **痛点**：对标博主每天发新视频但没人盯，错过 100k+ 爆款选题
- **解决**：27_对标博主视频监控 表 + Deepseek 评分（女装关联度 / 学习价值 / 二创可行性）
- **演示**：每天 9:00 自动跑 → 抖音 48 个对标博主新视频 → DeepSeek 评分 → 飞书卡片"今日 Top 3 爆款，DRS 同款类目 2 条值得二创"

#### competitor-monitor
- **痛点**：竞品上新一波你不知道，价格调整你也不知道
- **解决**：16_竞品产品监控 表自动跑 + 飞书 IM 关键词命中报警
- **演示**：某竞品突然上 50 款春夏系列 → 16 表新增 → 飞书报警"⚠️ 莫千衣 5 月 5 日上新 50 款，4 款定价低于我们同款 30%"

#### content-pipeline
- **痛点**：选题→脚本→拍摄→剪辑→发布 5 步散在不同人手里，进度看不清
- **解决**：06_选题池 + 07_文案库 + 24_直播记录 表全链路追踪 + 卡点 alert
- **演示**：选题"DRS-0429 春夏穿搭"建立 → 5 天没动 → 自动 nudge 朱健豪 + 飞书卡片"卡 5 天，催一下？"

#### video-script-parser
- **痛点**：看到爆款想二创，但仔细分析镜头/台词/节奏要花 1 小时
- **解决**：yt-dlp 拉视频 + faster-whisper 转录 + DOUBAO 多模态拆解 5 维度
- **演示**：老板娘扔抖音链接 → 5 分钟后飞书收到完整脚本拆解 md（镜头 + 台词 + 视觉 + 声音 + 节奏 5 维度）

#### live-streaming
- **痛点**：直播场次数据 / 主推款 / 投流 / 转化分散，每场复盘要从 4 个工具拼数
- **解决**：21/22/23/24 表全链路：场次 / 主推款 / 投流 / 完整记录 + AI 复盘建议
- **演示**：老板娘 `昨晚直播怎么样` → "GMV ¥38k，主推款 KNT-0402 转化 12%（高于均值），投流 ROI 1.8（亏，建议下场降投）"

#### private-domain
- **痛点**：客户加了微信但没分层，全部当成一类发广告，转化低
- **解决**：10_客户分层 表（高价值/普通/沉睡）+ 不同分层不同消息节奏
- **演示**：新客户 A 加企微 → 系统看历史购买 → 自动打标"高价值老客户" → 推送差异化优惠码

#### opensource-radar
- **痛点**：想用 AI 工具但天天有新项目出来不知道哪些适合女装电商
- **解决**：每日 GitHub trending 抓取 + DeepSeek 评估女装电商相关性
- **演示**：每天 12:00 抓 GitHub → DEEPSEEK 评分 → 飞书"今日推荐 3 个：① wxauto4（微信桌面自动化）② DOUBAO-Vision（多模态）..."

---

### 🎯 任务协作（12 个）

#### task-collaboration
- **痛点**：跨租户朋友帮忙时飞书 P2P 私聊不通，IM API 返回 230038
- **解决**：用飞书原生任务/审批/日历通知绕开 IM 限制
- **演示**：老板娘建任务给跨租户朋友彩虹（不能 P2P 发消息）→ 走 task +create + assignee → 朱朋友收到飞书任务通知

#### task-lifecycle
- **痛点**：任务建好就忘了，没人跟进进度直到 deadline 当天才慌
- **解决**：任务全生命周期追踪：建立 → 接受 → 进行中 → 卡点 → 完成 → 复盘，自动提醒
- **演示**：任务"DRS-0429 拍摄"建立 → 设计师没接受 1 天 → 自动 nudge"还没开始？deadline 还有 3 天"

#### approval-flow
- **痛点**：报销 / 批价 / 上新审核 走线下，凭口头/微信记录，找半天找不到
- **解决**：飞书审批 API + 14_审批记录 表自动归档
- **演示**：设计师申请打样预算 ¥3000 → 飞书审批卡片 → 老板娘点同意 → 自动归档 14 表 + 飞书任务给采购

#### okr-cascade
- **痛点**：季度 OKR 定了之后没在日常工作里体现，到月底对不上
- **解决**：13_OKR 表 + 任务 / 销售 / 库存自动关联到对应 KR
- **演示**：老板娘 `Q2 OKR 进度` → "销售 KR 完成 65%，新品 KR 完成 80%，私域 KR 严重落后 30%（建议本月重点冲）"

#### ⭐ morning-report
- **痛点**：每天起床要打开 5 个工具看昨天发生了啥，浪费 30 分钟
- **解决**：早 8:00 自动跑：拉飞书 + 企微 + 个微 + 销售 + 库存 + 任务 → 一张早报卡片
- **演示**：老板娘起床打开飞书 → 一张早报卡："昨日销售 ¥45,820 ✓达标 / 库存 1 红 3 黄 / 你有 3 条 @消息 / ZC 工厂回复 DRS-0429 可加急"

#### personal-mirror
- **痛点**：员工日报敷衍了事，老板分不清真假努力
- **解决**：22:00 自动拉员工飞书一天行为 → AI 4 维分析（任务推进/沟通密度/会议参与/重点产出）
- **演示**：每晚老板娘看朱健豪今日镜像 → "完成 4 个任务（含 1 个跨部门），开会 2 次（核心议程发言），主动推动 1 个跨问题"

#### meeting-workflow
- **痛点**：会议结束没纪要，决议执行无人跟进
- **解决**：飞书妙记 + 18_会议决策 表 + 决议自动转任务 + 跟进者每周复盘
- **演示**：周一例会 → 妙记 AI 摘要 → 18 表自动入库 5 条决议 → 5 个对应任务自动分发给责任人

#### meeting-broadcaster
- **痛点**：重要会议结论想同步给没参会的人，手动转发 5 个群很麻烦
- **解决**：一键把会议纪要广播到指定的飞书群 / 个人 + AI 生成 3 句话精简版
- **演示**：老板娘评审会结束 → `广播评审决议给生产、设计、内容群` → 3 个群同时收到 AI 摘要卡片

#### meeting-clip-extractor
- **痛点**：1 小时会议视频回看太累，找具体片段要拖进度条
- **解决**：妙记 AI 章节 + 关键词锚点提取
- **演示**：老板娘 `播放上周一会议 14:30 - 16:00 关于 DRS-0429 那段` → 直接定位 + AI 给出 3 句话总结

#### feedback-returns
- **痛点**：退货反馈散在客服记录里，质量问题相同 SKU 反复出现没人发现
- **解决**：11_退货反馈 表自动聚合 + 同款 ≥ 3 退货飞书报警 + 自动通知工厂
- **演示**：3 天内 KNT-0402 退货 5 单（"针织起球"）→ 自动报警 + 微信通知 ZC 工厂质检

#### order-fulfillment
- **痛点**：4 平台订单履约状态分散，缺货 / 延迟发货后置发现
- **解决**：全平台订单状态 + 异常单自动飞书任务给客服跟进
- **演示**：抖音订单 #12345 已超 3 天未发 → 异常入库 → 飞书任务自动派给客服 + 备注"客户 3 次催单"

#### helpdesk-customer-tickets
- **痛点**：客户问题在微信 / 飞书 / 平台客服三个口同时进来，处理乱
- **解决**：飞书 helpdesk 工单 + 自动分流 + AI 自动回复常见问题 + 升级时转人
- **演示**：客户问"何时发货" → AI 看订单状态自动回 → 复杂问题（如尺码退换）才转人工

---

### 🤖 AI 大脑 + 基础设施（6 个）

#### boss-clone-aily
- **痛点**：老板出差 / 度假时同事问她"这个怎么处理"找不到答案
- **解决**：飞书 Aily 应用 + 26_老板语料库（历史决策案例 + 风格语料）→ 老板克隆 AI 替她答
- **演示**：朱健豪问 `老板娘对大码怎么看` → 26 表查到她过往 5 次决策都说"不做大码影响品牌定位" → AI 给出风格化答复

#### skill-recommender
- **痛点**：45 个 skill 用户不知道哪个解决他的问题
- **解决**：DEEPSEEK 看用户描述 → 推荐最匹配的 3 个 skill + 一行示例命令
- **演示**：员工问 `想知道竞品上新` → 推荐 competitor-monitor、blogger-monitor、market-trends + 各给一行调用示例

#### auto-scheduler
- **痛点**：12 个定时任务（早报 / 库存扫 / 博主抓 等）散在不同 cron / 手动起，状态看不清
- **解决**：APScheduler 主调度器 + config/auto-triggers.json 集中管理 + 状态可视化
- **演示**：老板娘 `定时任务状态` → "12 个任务全 OK，下次跑：早报 8:00 / 库存扫 30 分钟后 / 博主抓 9:00"

#### knowledge-base
- **痛点**：公司经验沉淀在群聊和会议纪要里，新员工查询要问 5 个人
- **解决**：19_经验沉淀库 表 + 飞书 wiki 联动 + 向量检索
- **演示**：新实习生问 `售罄率怎么算` → 19 表 → "实销/做货数 × 100%，行业基准 65%，本公司均值 58%"

#### lingo-fashion-glossary
- **痛点**：服装行业黑话（"色号 / 版型 / 安全线 / 上新波段"）跨部门理解不一致
- **解决**：飞书 lingo 服装词汇表
- **演示**：跨租户朋友看到"安全线" → 鼠标悬停 → 飞书 lingo 弹窗 → "库存预警最低限，<此值即触发补货"

#### event-router
- **痛点**：飞书事件回调（消息 / 群变更 / 反应）多种类型，每个 skill 都自己处理太重
- **解决**：统一事件路由层 + 按类型分发到对应 skill
- **演示**：用户给老板娘卡片点赞 → event-router 路由到 reaction-handler → 自动记录情感反馈到 26 表

#### doc-iterator
- **痛点**：飞书文档要批量改（比如 100 个产品 SOP 加一段免责声明），手动改累死
- **解决**：DocxXML 批量更新 API + 失败回滚 + 进度追踪
- **演示**：老板娘 `所有产品 SOP 加一段七天无理由退换条款` → 100 个文档 30 秒批量更新 + 1 个失败自动回滚

---

## 🖼 核心 skill 效果演示

下面 9 张图是核心 skill 的效果演示（聊天对话 + 飞书卡片回执 + 实际数据），让你不用跑环境就能看清每个 skill 实际长什么样：

### omnitask-bridge · 全员驾驶舱
![](./docs/images/demo-omnitask-bridge.png)

### wechat-monitor · 微信群速览
![](./docs/images/demo-wechat-monitor.png)

### morning-report · 早 8:00 跨渠道情报早报
![](./docs/images/demo-morning-report.png)

### product-library · 服装电商产品库 + AI 分析
![](./docs/images/demo-product-library.png)

### blogger-monitor · 对标博主监控
![](./docs/images/demo-blogger-monitor.png)

### wxauto-supplier-bridge · 飞书指令通知供应商
![](./docs/images/demo-wxauto-supplier.png)

### stock-replenishment · 库存预警自动报警
![](./docs/images/demo-stock-replenishment.png)

### launch-decision · AI 上新方案评分
![](./docs/images/demo-launch-decision.png)

### personal-mirror · 员工今日真实贡献镜像
![](./docs/images/demo-personal-mirror.png)

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
