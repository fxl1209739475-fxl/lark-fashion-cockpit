---
name: lark-fashion-cockpit-product-graph
version: 1.0.0
description: "产品关系图自动生成 — 从 5 张多维表（产品库/搭配组/直播/退货/销售）抽取关系，生成 Mermaid DSL → 注入飞书白板。当用户说「产品关系图」「画产品全景」「白板生成」「产品×SKU×搭配×直播总览」时使用。属于 lark-fashion-cockpit 商品中心板块（第 24 个能力 = 杀手锏 3 实体化）。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli docs +whiteboard-update --help"
---

# 产品关系图 — 杀手锏 3 落地

> **🔥 4/13 飞书 CLI 直播评委 Zara 钦点：「白板是大杀器」。** 这是把这句话变成产物。

> **🎯 一张图回答 5 个问题：**
> - 哪些款是搭配组？带哪些老款一起卖？
> - 哪些款上过直播？GMV 多少？
> - 哪些款有退货风险？
> - 哪些款滞销/售罄？
> - 哪些款在开发中？

> **板块：** 🅱 商品中心（第 24 个能力 = 杀手锏 3「产品关系图」实体化）  
> **数据源：** `01_产品库` + `17_产品搭配组` + `08_直播排期` + `11_退货反馈` + `02_4平台销售`  
> **输出载体：** 飞书白板（lark-cli docs +whiteboard-update + Mermaid DSL）

---

## 一、关系图包含什么

```
flowchart LR
  
  %% 产品节点（含状态 emoji + 价格 + 销量 + 库存）
  DRS-0429-FL["🟢 法式碎花连衣裙<br/>¥299 实销320 库存280"]
  KNT-0402-CD["⚪ 焦糖针织开衫<br/>¥189 实销300 库存200"]
  ...
  
  %% 搭配组关系（虚线 + 来源 × 使用次数）
  DRS-0429-FL -.->|人工锁定×12| KNT-0402-CD
  
  %% 直播关系（实线 → 直播节点）
  DRS-0429-FL --> LIVE_4_22["📺 春夏穿搭场<br/>GMV ¥51200"]
  
  %% 退货风险（虚线 + 红色警告）
  DRS-0429-FL -.->|风险| RET_DRS["⚠️ 退货 3 次"]
```

### 节点颜色语义

| Emoji | 含义 | 颜色 |
|---|---|---|
| 🟢 | 在售 | 米色 |
| ⚪ | 历史款 | 米色 |
| 🔴 | 售罄 | 米色 |
| 🟡 | 开发中 | 米色 |
| 📺 | 直播节点 | 浅蓝 |
| ⚠️ | 退货警告 | 浅红 |

### 边语义

| 线型 | 含义 |
|---|---|
| 虚线（dotted） | 搭配关系 / 风险关系（弱关联）|
| 实线（solid） | 直播主推 / 销售流转（强关联）|

---

## 二、自动生成流程

```
1. 拉 5 张多维表
   ↓
2. 构建 record_id → SKU 索引
   ↓
3. 生成 Mermaid 节点（每个产品 + 直播 + 退货警告）
   ↓
4. 生成 Mermaid 边（搭配 + 直播 + 退货）
   ↓
5. lark-cli docs +whiteboard-update --input_format mermaid --source @file.mmd
   ↓
6. 飞书白板渲染（自动布局 + 颜色）
```

---

## 三、运行命令

```bash
# 1. 创建空白板（首次）
lark-cli docs +create --api-version v2 --content '<whiteboard type="blank"></whiteboard>'
# 拿到 whiteboard-token (block_token)

# 2. 跑生成脚本
PowerShell -File scripts/product-graph.ps1 -WhiteboardToken <token>

# 3. 飞书 App 打开 doc URL → 看自动渲染的关系图
```

---

## 四、脚本逻辑（130 行 PowerShell）

```powershell
# scripts/product-graph.ps1
1. 加载 5 表
2. 构建 rid → SKU 映射
3. 遍历产品 → 生成节点 + 状态 emoji
4. 遍历搭配组 → 生成虚线边（带"来源×次数"标签）
5. 遍历直播 → 生成 LIVE 节点 + 实线边
6. 统计退货 → 高频款（≥2 次）生成 ⚠️ 警告节点
7. 拼接 Mermaid DSL
8. lark-cli docs +whiteboard-update 注入飞书白板
```

---

## 五、典型对话

```
👩 老板：「画一下产品关系图，白板上看一眼全局」

🤖 agent：8 秒后
✓ 拉 8 产品 + 3 搭配组 + 5 直播 + 8 退货
✓ 生成 55 行 Mermaid DSL
✓ 注入飞书白板（token CXxkwXOzJhMTUKb6ZVicFZ2cnlk）
✓ 白板自动渲染

→ 飞书 App 点开看到：
  • 8 个产品节点（按状态分色）
  • 3 条搭配虚线（带"人工锁定×12"标签）
  • 5 个直播节点（含 4/22 ¥51200 / 4/29 ¥42500 等）
  • 2 个退货警告（DRS 系列尺码偏小）

老板娘一眼看懂：DRS-0429-FL 是搭配主轴 + 直播爆品 + 退货风险款，需要上腰围放大版。
```

---

## 六、为什么是杀手锏 ⭐⭐⭐⭐⭐

| 维度 | 说明 |
|---|---|
| 评委亲点 | 4/13 直播 Zara 明确说"白板是大杀器" |
| 视觉冲击 | 一张图秒懂全公司商品全貌（评委演示秒拿分）|
| AI 价值 | 不是简单 BI，是<b>多源数据自动关系挖掘</b> |
| 通用性 | 任何垂直行业都能用此架构（"产品×渠道×订单×反馈"图都能套）|
| 工程深度 | 130 行 PowerShell + Mermaid + 5 表关系挖掘 |

---

## 七、参考

- [`../product-library/SKILL.md`](../product-library/SKILL.md) — 产品库基础数据
- [`../product-matching/SKILL.md`](../product-matching/SKILL.md) — 搭配关系数据来源
- [`../live-streaming/SKILL.md`](../live-streaming/SKILL.md) — 直播节点数据
- [`../feedback-returns/SKILL.md`](../feedback-returns/SKILL.md) — 退货警告数据
- 工具：lark-cli docs +whiteboard-update + Mermaid DSL
- 飞书白板示例：https://my.feishu.cn/docx/Pcvwd9e3qopP4ZxOSk2cTbo8nMf
