# 🤖 直播数据浏览器自动化部署指南

> **目标：** 抖音/视频号/小红书 商家后台 → 浏览器自动打开 → DOM 抓取 → 库存 GMV 智能匹配 → 飞书卡片
>
> **现状：** 算法完整可跑（mock 数据已端到端验证），生产部署需 1-2 小时调试 DOM 选择器

---

## 🎯 完整工作流

```
22:00 直播结束（cron 触发）
   ↓
livestream-scraper.py 启动 Playwright（headed 模式）
   ↓
依次打开 3 平台：
  ① https://fxg.jinritemai.com/ffa/buyin/dashboard/live      (抖音)
  ② https://channels.weixin.qq.com/livedata                  (视频号)
  ③ https://ark.xiaohongshu.com/livedata                     (小红书)
   ↓
每个平台：
  - 加载已保存的 cookie（首次登录后保存）
  - 等待 DOM 元素加载
  - 截屏（备份）
  - DOM 抓取销售明细 [(SKU, 产品名, 销售金额, 平台)]
   ↓
合并 N 条销售记录 → JSON 文件
   ↓
inventory-gmv-matcher.ps1 调用：
  - 款号匹配 01_产品库
  - 检查"是否库存款"字段（人工标记 / 自动判定）
  - 累计：📦 库存 GMV vs 💰 正常 GMV
   ↓
飞书卡片推老板群（含每条销售记录的匹配理由）
```

---

## 🚀 部署步骤（约 1-2 小时）

### Step 1：安装 Playwright（5 分钟）

```bash
pip install playwright
playwright install chromium
```

### Step 2：首次登录 3 平台保存 cookie（每个 5 分钟）

```bash
cd C:\Users\冯兴龙\lark-fashion-cockpit

# 抖音首登
python scripts/livestream-scraper.py --platform douyin --first-login
# 浏览器弹出 → 扫码登录 → 关闭浏览器 → cookie 保存到 cookies/douyin.json

# 视频号首登
python scripts/livestream-scraper.py --platform shipinhao --first-login

# 小红书首登
python scripts/livestream-scraper.py --platform xhs --first-login
```

### Step 3：调试 DOM 选择器（每平台 30 分钟）

我在 `livestream-scraper.py` 里写的 selectors 是**通用占位**，每个平台真实 DOM 不同。需要打开各家后台用 DevTools 找：

```python
# 抖音示例（需要你打开 fxg.jinritemai.com 用 F12 找）
"selectors": {
    "sales_table": "table.live-sales tbody tr",   # ⚠ 替换为真实 selector
    "sku": "td.sku-col",
    "name": "td.product-name",
    "amount": "td.gmv-col",
}
```

**操作：**
1. 浏览器打开商家后台直播数据页
2. F12 → Elements → 右键产品行 → Copy → Copy selector
3. 替换上面的 selectors

### Step 4：测试单平台

```bash
# 不要 --first-login，会自动加载 cookie
python scripts/livestream-scraper.py --platform douyin

# 看到 ✓ 抓到 N 条销售记录 + ✓ 截屏: screenshots/...png 即成功
```

### Step 5：3 平台一起跑 + 库存 GMV 匹配

```bash
python scripts/livestream-scraper.py --platform all

# 自动跑：
#   抓 douyin → 抓 shipinhao → 抓 xhs
#   合并销售记录 → JSON
#   调 inventory-gmv-matcher.ps1
#   推飞书卡片
```

### Step 6：cron 自动化（每天 22:00）

Windows 任务计划程序：
```
触发器：每天 22:00:00
程序：python
参数：C:\Users\冯兴龙\lark-fashion-cockpit\scripts\livestream-scraper.py --platform all
```

---

## 🛡 反爬虫 + 安全考虑

### 1. 频次控制
- 每个平台**每天只跑 1 次**（22:00）
- 避免高频访问被风控

### 2. 用户代理伪装
Playwright 默认 UA 可能被识别，可改：
```python
ctx = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
)
```

### 3. 代理 IP（可选，仅当真被封时考虑）
- 使用住宅代理（避免数据中心 IP）
- 中国境内代理服务：阿布云 / 蘑菇代理

### 4. 风险提示
- **抖音/小红书反爬严**，频次过高可能封号
- **视频号反爬最弱**，最先试视频号
- 长期方案是接 **官方 API**（需开通商家开发者账号）

---

## 📊 库存 GMV 算法详解

### 输入示例（来自浏览器抓取）
```json
[
  {"sku": "DRS-0429-FL", "name": "法式碎花连衣裙", "amount": 29900, "platform": "抖音"},
  {"sku": "KNT-0402-CD", "name": "短款焦糖针织开衫", "amount": 18900, "platform": "抖音"},
  ...
]
```

### 匹配规则（按优先级）
1. **款号精确匹配** `01_产品库.款号` 字段
2. **如未匹配** → 产品名前 4 字模糊匹配
3. **如还未匹配** → 警告进 `正常 GMV`（提示人工核对）

### 库存款判定（按优先级）
1. **人工标记 = "是"** → 直接计入库存 GMV
2. **人工标记 = "否"** → 不计入
3. **自动判定模式** → 走规则：
   - `状态 = 历史款` → 是库存款
   - `状态 = 在售 AND 售罄率 < 60%` → 是库存款（在售但卖不动）
   - `状态 = 售罄/开发中` → 否

### 输出
```
💰 正常 GMV: ¥X
📦 库存 GMV: ¥Y (Z%)
💸 合计 GMV: ¥(X+Y)
+ 每条销售的详细匹配理由
```

---

## 🔁 商业化升级路径

| 阶段 | 方案 | 工程量 |
|---|---|---|
| **当前 MVP** | Playwright + DOM 抓取 | 1-2 小时调试 |
| **稳定版** | 加 OCR 兜底（DOM 失效时用截屏 OCR） | +2 小时 |
| **生产版** | 抖音电商官方 API（fxg.jinritemai.com 开放平台）| 1-3 天申请 + 接通 |
| **企业版** | 全平台官方 API + 实时事件推送 | 1-2 周 |

---

## 🐛 故障排查

| 报错 | 原因 | 解决 |
|---|---|---|
| `playwright not installed` | 没装 | `pip install playwright && playwright install chromium` |
| `Timeout waiting for selector` | DOM 选择器过期或平台改版 | 重新 F12 找 selector，更新 PLATFORMS 配置 |
| `invalid cookie` | cookie 过期（一般 30 天）| 重新跑 `--first-login` 重新扫码 |
| `产品名 X 未匹配` | 款号不规范 | 在 01_产品库 加产品名别名 / 改抓取逻辑 |
| `被封号` | 频次过高 / 风控 | 改用代理 IP / 降低访问频率 / 切换官方 API |

---

## 📂 文件结构

```
lark-fashion-cockpit/
├── scripts/
│   ├── livestream-scraper.py        ← 浏览器自动化主脚本
│   ├── inventory-gmv-matcher.ps1   ← 库存 GMV 匹配算法（核心）
│   └── livestream-daily-report.ps1 ← 日报汇总（已有）
├── cookies/                         ← 各平台 cookie 持久化
│   ├── douyin.json
│   ├── shipinhao.json
│   └── xhs.json
└── screenshots/                     ← 每次抓取的截屏备份
    └── douyin_20260811_220000.png
```
