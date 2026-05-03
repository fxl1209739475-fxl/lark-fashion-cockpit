---
name: lark-fashion-cockpit-competitor-monitor
version: 1.0.0
description: "竞品 + 趋势监控 — 调 douyin-monitor 抓爆款博主 + 监控竞品品牌产品价格销量 + 趋势信号（颜色/面料/款式）。当用户说「看竞品」「同行卖什么」「爆款博主」「趋势信号」「上新速度」时使用。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 竞品 + 趋势监控

> **板块：** 🅱 商品中心  
> **调用：** `base` + `doc` + `python`(douyin-monitor)  
> **多维表依赖：** `12_竞品博主库` / `15_市场内容监控` / `16_竞品产品监控`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read base:record:create docs:document:write_only"
```

外部依赖：用户的 douyin-monitor Python CLI（可选，没有时跳过自动采集）

## 二、工作流

### 场景 A: 竞品博主监控

**触发语：** "看竞品博主" / "同行博主"

```bash
# 列已监控博主
lark-cli base +record-list \
  --base-token <APP> --table-id tblAhs8thFobg1dx

# 调 douyin-monitor 抓博主最新视频（链 content-pipeline 工作流 A）
cd ~/douyin-monitor && python main.py --bloggers ./fashion-bloggers.json
```

### 场景 B: 竞品产品监控

**触发语：** "看 X 品牌价格" / "竞品在卖啥"

```bash
# 读 16_竞品产品监控
lark-cli base +record-list \
  --base-token <APP> --table-id tblq1dZ4JNX7LPQI \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"竞品品牌","operator":"is","value":"ZARA"}
  ]}'

# 数据采集靠用户人工录入或外部爬虫脚本（写自定义 douyin-monitor 模块）
```

### 场景 C: 趋势信号

**触发语：** "看趋势" / "今年流行什么"

```
Step 1: AI 从 15_市场内容监控 + 12_竞品博主库 提取关键词
Step 2: 按维度聚合：颜色 / 面料 / 款式 / 场景
Step 3: 生成趋势报告（文档 + 词云 dashboard 已建）
```

```bash
# 拉近 30 天的市场监控数据
lark-cli base +record-list --base-token <APP> --table-id tblW888G2M8KMgZk \
  --filter '...近30天...'

# AI 提示词
# "从这批视频标题里提炼当前流行的：颜色 / 面料 / 款式 / 场景。每类输出 Top 5。"
```

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `12_竞品博主库` | 读 / 写 |
| `15_市场内容监控` | 读（content-pipeline 共享）|
| `16_竞品产品监控` | 读 / 写 |
| `01_产品库` | 关联（对标款）|

## 四、典型对话示例

```
用户：看下今年流行什么

agent：
✓ 分析近 30 天 480 条市场监控数据
🎨 颜色 Top 5：奶茶白、雾霾蓝、莓果红、燕麦杏、墨绿
🧵 面料 Top 5：醋酸缎面、莱赛尔、马海毛、雪纺、亚麻
👗 款式 Top 5：吊带、鱼尾、收腰、直筒西装、廓形
🏖️ 场景 Top 5：度假、通勤、约会、Citywalk、出游

💡 对你的建议：早春第二波建议主推「醋酸缎面 + 吊带 + 度假风」
```

## 五、与其他 skill 协作

- `content-pipeline`：共享 15_市场内容监控 数据
- `new-launch-planning`：基于趋势信号企划下波上新
- `product-library`：竞品对标款分析

## 六、参考

- [`../content-pipeline/SKILL.md`](../content-pipeline/SKILL.md)
- [`../new-launch-planning/SKILL.md`](../new-launch-planning/SKILL.md)
