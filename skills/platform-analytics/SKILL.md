---
name: lark-fashion-cockpit-platform-analytics
version: 1.0.0
description: "多平台数据分析 — 4 平台（淘宝/抖音/小红书/视频号）销售趋势、构成、对比。当用户说「看销售数据」「4 平台对比」「抖音趋势」「平台占比」时使用。属于 lark-fashion-cockpit 销售增长板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 多平台数据分析

> **板块：** 🅲 销售增长  
> **调用：** `base` + `doc`  
> **多维表依赖：** `02_4平台销售`（核心）

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read docs:document:write_only"
```

## 二、工作流

### 场景 A: 销售趋势（折线图数据）

**触发语：** "看销售趋势" / "近 7 天销售"

```bash
SEVEN_DAYS_AGO=$(date -d '-7 day' +%s)000

lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[{"field_name":"GMV","rollup":"SUM"}],
    "group_by":[{"field_name":"日期","mode":"integrated","sort":{"type":"group","order":"asc"}}],
    "filter":{"conjunction":"and","conditions":[
      {"field_name":"日期","operator":"isGreaterEqual","value":"'$SEVEN_DAYS_AGO'"}
    ]}
  }'
```

### 场景 B: 4 平台对比

**触发语：** "4 平台对比" / "哪个平台卖得好"

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tbll7UHbL6kDxZua \
  --json '{
    "table_name":"02_4平台销售",
    "series":[
      {"field_name":"GMV","rollup":"SUM"},
      {"field_name":"订单数","rollup":"SUM"},
      {"field_name":"UV","rollup":"SUM"}
    ],
    "group_by":[{"field_name":"平台","mode":"integrated"}]
  }'
```

输出后 AI 计算客单价 / 转化率，对比 4 平台特点。

### 场景 C: 平台 × 时间矩阵

每个平台每天的 GMV → 折线图（每平台一条线）。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `02_4平台销售` | 读 |

## 四、典型对话示例

```
用户：4 平台对比

agent：
✓ 近 7 天数据：
🛒 淘宝：¥58万 / 4200单 / 客单¥138 / 转化 2.8% (规模最大)
📱 抖音：¥42万 / 3500单 / 客单¥120 / 转化 1.4% (流量大但转化低)
📕 小红书：¥18万 / 1500单 / 客单¥120 / 转化 1.9% (高质量)
🎬 视频号：¥9万 / 800单 / 客单¥112 / 转化 1.2% (起步阶段)

📊 详情图表：https://my.feishu.cn/base/<APP>?dashboard=经营总览

💡 建议：抖音流量好但转化低，建议优化主播/详情页
```

## 五、与其他 skill 协作

- `target-tracking`：平台目标进度
- `live-streaming`：直播 ROI
- `morning-report`：晨报里展示当日数据

## 六、参考

- [`../target-tracking/SKILL.md`](../target-tracking/SKILL.md)
- [`../profit-analysis/SKILL.md`](../profit-analysis/SKILL.md)
