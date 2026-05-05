---
name: lark-fashion-cockpit-product-matching
version: 1.0.0
description: "产品搭配推荐 — 基于元素标签 + 历史成交权重 + 库存倾斜，给单款推荐 2-4 件搭配款。当用户说「XX 款配什么好」「XX 配什么连衣裙」「DRS-0429-FL 配什么」「给我推荐搭配」「拍视频要搭配款」时使用。也可被 content-pipeline / live-streaming / new-launch-planning 主动调用，自动给拍摄/直播任务挂搭配。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# 产品搭配推荐 — AI 让老款不睡觉

> **🎯 老板娘的灵感来源：** 「女装一波卖完总有些剩库存。直播 / 拍视频 / 主图必须穿搭。我希望一句话告诉我『这件配什么』，AI 还能帮我倾斜把老库存搭配出去。」

> **板块：** 🅱 商品中心  
> **核心数据：** `01_产品库`（元素标签）+ `17_产品搭配组`（固定 + AI + 历史）  
> **下游联动：** `task-collaboration` / `content-pipeline` / `live-streaming` / `new-launch-planning`

---

## 一、能干什么（3 个真实场景）

### 场景 A：单款推荐（最常用）

```
👩 老板娘：「DRS-0429-FL 配什么好？」

🤖 agent：6 秒后
✓ 读 01_产品库（DRS-0429-FL 元素标签 + 状态）
✓ 读 17_产品搭配组（已锁定 + 历史成交）
✓ 算法打分（元素相似 + 历史权重 + 库存倾斜）
✓ 排序输出 Top 3 推荐 → 群里弹蓝色卡片

┌─ 🛍 DRS-0429-FL 搭配推荐 ───────┐
│ 🥇 KNT-0402-CD 短款焦糖针织开衫  │
│    匹配 88分 / 库存 200（中）/ 已锁定 │
│ 🥈 KNT-2024-WL 韩系奶油针织毛衣  │
│    匹配 76分 / ⚠️ 库存 0 跳过    │
│ 🥉 SHT-0420-SP 海盐蓝防晒衬衫    │
│    匹配 71分 / 库存 250 OK       │
└──────────────────────────────────┘
```

### 场景 B：库存倾斜（清老货 / 救新款）

```
👩 老板娘：「我们刚上的 DRS-0429-FL 拍视频，配一件能带走老库存的」

🤖 agent：
✓ 元素相似度：3 个候选（KNT-0402-CD / SHT-0420-SP / SKT-0328-A）
✓ 库存倾斜（清老货 +20分）：SKT-0328-A 仅剩 5 件 但元素勉强搭
✓ 综合排序：KNT-0402-CD 88 > SHT-0420-SP 71 > SKT-0328-A 65
✓ 推荐：KNT-0402-CD（保稳）+ SKT-0328-A（带库存）

智能选择：「主推 KNT-0402-CD，叠加 SKT-0328-A 带 5 件老货」
```

### 场景 C：自动挂任务（skill 间联动）

```
content-pipeline 建拍摄任务 → 主动调用 product-matching
   → 把推荐搭配写到任务的"产品参考"字段
   → 主播/达人/老板出镜时带这套衣服
```

---

## 二、元素标签体系（5 维 32 选项）

每款产品标 4-6 个元素标签：

| 维度 | 选项（hue 颜色就是搭配视觉化） |
|---|---|
| **色** | 同色系-米白/奶油/焦糖/海盐蓝/莓果红 + 中性-黑/灰/炭黑 |
| **风** | 法式 / 韩系 / 甜辣 / 通勤 / 学院 / 度假 |
| **品** | 上衣 / 下装 / 连衣裙 / 外套 / 针织 / 配饰 |
| **料** | 雪纺 / 针织 / 牛仔 / 棉麻 / 丝缎 / 皮 |
| **景** | 约会 / 上班 / 旅行 / 度假 / 日常 / 派对 |

**字段位置：** `01_产品库.元素标签`（多选）

---

## 三、AI 评分算法（业务可调）

```
匹配总分 = 
  + 同色系 / 互补色      × 30
  + 同风格              × 25
  + 互补品类（如裙+针织）× 20
  + 同场景              × 15
  + 历史成交权重        × 10  (使用次数 / 最大值 × 10)
  + 库存倾斜            × 10  (慢销老库存 +10，新款 +5，售罄 -∞)
  - 同品类惩罚（连衣裙+连衣裙）× 30
```

### 互补品类规则（防"连衣裙配连衣裙"尴尬）

```
连衣裙 ↔ 外套 / 针织（薄）/ 配饰
上衣   ↔ 下装 / 外套
下装   ↔ 上衣 / 外套 / 针织
针织   ↔ 下装 / 连衣裙（叠穿）
外套   ↔ 上衣+下装组合 / 连衣裙
```

### 库存倾斜（核心增量价值）

```
状态 = 在售
  库存天数 < 7    → "急清"  +20 分（最高优先级搭出去）
  库存天数 7-30   → "稳卖"  0 分
  库存天数 > 30   → "慢销"  +10 分（鼓励搭出去）

状态 = 售罄        → 跳过（库存=0 不能推荐）
状态 = 历史款      → 跳过
状态 = 开发中      → 跳过（还没上市）
```

---

## 四、工作流（5 步）

### Step 1: 读主推款元素

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblrKzymnPPQ98ZX \
  --jq '[.data.data[] | select(.[1].款号=="DRS-0429-FL") | .[1]]'
```

输出：
```json
{"款号":"DRS-0429-FL","品类":"连衣裙","状态":"在售",
 "元素标签":["色-同色系-米白","风-法式","品-连衣裙","料-雪纺","景-约会","景-度假"]}
```

### Step 2: 读已锁定搭配（17_产品搭配组）

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblHZAHcOzkcD4gC
```

如果主推款已在「人工锁定」组里 → 直接用，跳过算法。
否则进入 Step 3 AI 评分。

### Step 3: 拉所有候选 + 打分

```bash
# 拉 01_产品库 所有"在售"款，排除主推自己 + 同品类
# 在 PowerShell / Python 里跑评分公式

candidates = filter(产品库, status=='在售' and 款号!=主推款 and 品类!=主推款.品类)
for c in candidates:
    score = 元素重合度(c, 主推款) + 历史权重(c) + 库存倾斜(c)
sorted_top_n = sorted(candidates, by score desc)[:3]
```

### Step 4: 输出推荐卡片（飞书 IM）

```bash
# 推荐 Top 3 → 蓝色 interactive 卡片 → 老板群
# 每条带匹配分 + 库存数 + 跳到该款详情按钮
lark-cli im chats messages create \
  --chat-id oc_45e0995a007db9d7f1859fa17b6566f6 \
  --msg-type interactive \
  --content '<卡片 JSON>'
```

### Step 5: 写回 17_产品搭配组（学习）

```bash
# 如果用户「采纳」（点了卡片确认按钮）→
# 写一条新组到 17，来源="AI推荐"，使用次数 +1
lark-cli base +record-upsert \
  --base-token <APP> --table-id tblHZAHcOzkcD4gC \
  --json '{"搭配组名":"AI-DRS+KNT","主推款":["recviy1mBYLLnB"],
           "搭配款":["recviy1mBY3TgK"],"来源":"AI推荐","使用次数":1}'
```

下次同款再问，**采纳过的组合权重就上来了**（自学习闭环）。

---

## 五、被其他 skill 调用（内化模式）

### 从 content-pipeline 调（自动给拍摄任务挂搭配）

```bash
# content-pipeline 建拍摄任务时：
TOPIC_PRODUCT="DRS-0429-FL"
PAIR_RESULT=$(invoke product-matching --主推 $TOPIC_PRODUCT --top 2)
# 把推荐结果写入任务"产品参考"字段
lark-cli task +create --summary "拍 DRS-0429-FL 视频" \
  --description "主推：DRS-0429-FL\n搭配：${PAIR_RESULT.推荐_1}, ${PAIR_RESULT.推荐_2}"
```

### 从 live-streaming 调（直播排款 → 自动配套）

```bash
# 老板配置直播主推后，自动跑搭配推荐 → 直播排款表
for 主推 in 直播排款列表:
  搭配 = invoke product-matching --主推 $主推 --top 3 --库存倾斜=高
  写入 08_直播排期.主推套装
```

### 从 new-launch-planning 调（新款 + 老款套装）

```bash
# 上新一波时，给每个新款找 1 件老款搭配 → 提前出主图
# 直接清掉一部分老库存，新款带流量带销量
```

---

## 六、典型对话示例

```
👩 老板：「DRS-0429-FL 配什么好」

🤖 agent：
正在分析...
✓ 读元素：法式 / 连衣裙 / 雪纺 / 约会
✓ 候选 5 款（排除连衣裙 + 历史款 + 售罄）
✓ 评分排序：

  🥇 KNT-0402-CD（焦糖针织开衫）   88 分
     ├ 元素重合：风格法式 + 场景约会
     ├ 历史权重：人工锁定组（+10）
     └ 库存：200 件（健康）
  🥈 SHT-0420-SP（海盐蓝防晒衬衫）  71 分
     ├ 元素重合：场景日常旅行
     ├ 历史权重：无
     └ 库存：250（健康）
  🥉 SKT-0328-A（高腰 A 字半身裙） 65 分
     ⚠️ 库存仅 5 件 但适合带库存

👉 推荐 KNT-0402-CD（稳）+ 备 SKT-0328-A（清老货）
👉 已发卡片到群里。要给朱健豪建拍摄任务吗？回复"建任务"。
```

---

## ⭐ 六半、自动生图（搭配可视化）

> **看推荐分数不直观，看图就懂。** 本 skill 自动给每个推荐组合生成「搭配平铺图」，直接落地到 17_产品搭配组的「搭配图」附件字段 + IM 卡片图片元素。

### 生图工具链

```
Top N 推荐（评分脚本）
   ↓
   gen-outfit-image.py（PIL 拼接）
   ├ 加载 8 款产品占位图（assets/products/<SKU>.jpg）
   ├ 横向平铺主推 + 1-3 件搭配款
   ├ 顶部 header（搭配组名 + SKU 列表 + 匹配分）
   ├ 主推/搭配 角色 badge（红/蓝）
   ├ + 号视觉连接
   ├ 底部 AI 推荐理由
   └ 输出 JPG（assets/outfits/<main>+<pair>.jpg）
   ↓
1. 调 lark-cli base +record-upload-attachment → 落地 17_产品搭配组.搭配图
2. 调 lark-cli im images create（as bot）→ 拿 image_key
3. 拼 IM interactive 卡片 + img 元素（mode=fit_horizontal）
```

### 关键命令

```bash
# 生成单组搭配图
python scripts/gen-outfit-image.py DRS-0429-FL KNT-0402-CD \
  --name "法式约会·连衣裙+针织开衫" \
  --score "60" \
  --reason "互补品类+20 / 已锁定+15 / 慢销+10 / 老款+15"

# 上传到飞书 base 附件字段（必须先 cd 到目录）
cd assets/outfits
lark-cli base +record-upload-attachment \
  --base-token <APP> --table-id tblHZAHcOzkcD4gC \
  --record-id <PAIR_RID> --field-id 搭配图 \
  --file ./DRS-0429-FL+KNT-0402-CD.jpg

# 上传给 IM 拿 image_key
lark-cli im images create --as bot \
  --file "image=./DRS-0429-FL+KNT-0402-CD.jpg" \
  --data '{"image_type":"message"}' \
  --jq .data.image_key
```

### 进阶：真实产品图替换

当前 `assets/products/*.jpg` 是 PIL 生成的占位图（颜色色卡 + SKU + 价格）。后续可替换为：
- 淘宝主图（人工导入）
- 即梦/可灵 AI 生图（输入产品名 + 颜色 + 风格 prompt）
- 真人模特上身图（虚拟试穿，需图生图 API）

替换路径：`assets/products/<SKU>.jpg`，gen-outfit-image.py 自动复用新图。

---

## 七、库存倾斜实战例（核心商业价值）

```
场景：DRS-0429-FL（主推新款）+ 老库存清仓

候选评分（不带库存倾斜）：
  KNT-0402-CD: 78
  SHT-0420-SP: 71
  SKT-0328-A:  55  ← 老款被拍到第三

带库存倾斜（SKT-0328-A 仅 5 件库存，急清）：
  KNT-0402-CD: 78
  SHT-0420-SP: 71
  SKT-0328-A:  55 + 20 = 75  ← 跃居第 2

→ 主播/拍摄被强烈推荐"DRS-0429-FL + SKT-0328-A 套装"
→ 主图 / 视频 / 直播间都展示这个组合
→ 5 件 SKT-0328-A 在新款流量带动下卖完
→ 节省 ¥199×5=¥995 库存占用 + 减少清仓亏损
```

**这就是产品搭配推荐对商业的核心增量价值。**

---

## 八、参考

- [`../product-library/SKILL.md`](../product-library/SKILL.md) — 产品库基础
- [`../content-pipeline/SKILL.md`](../content-pipeline/SKILL.md) — 调用方（拍摄任务挂搭配）
- [`../live-streaming/SKILL.md`](../live-streaming/SKILL.md) — 调用方（直播排款挂搭配）
- [`../new-launch-planning/SKILL.md`](../new-launch-planning/SKILL.md) — 调用方（新款 + 老款）
- 数据：`01_产品库.元素标签` + `17_产品搭配组`
