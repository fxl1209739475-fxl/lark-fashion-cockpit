---
name: lark-fashion-cockpit-feedback-returns
version: 1.0.0
description: "评价退货分析 — 退货原因分类 + AI 反推改进建议（产品/详情页/客服话术/版型）。当用户说「看退货」「为啥退货多」「商品反馈」「退货原因」时使用。属于 lark-fashion-cockpit 商品中心板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 评价退货分析

> **板块：** 🅱 商品中心  
> **调用：** `base` + `doc` + AI  
> **多维表依赖：** `11_退货反馈`（核心）/ `01_产品库`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read docs:document:write_only"
```

## 二、工作流

### 场景 A: 退货原因总览

**触发语：** "看退货" / "为啥退货多" / "退货原因"

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tblCwJGr0HTMFtXD \
  --json '{
    "table_name":"11_退货反馈",
    "count_all":true,
    "group_by":[{"field_name":"退货原因","mode":"integrated","sort":{"type":"value","order":"desc"}}]
  }'
```

输出：尺码不合 45% / 色差 22% / 面料 15% / 物流 8% / 其他 10%

### 场景 B: 单 SKU 退货分析

**触发语：** "X 款为什么退货多"

```bash
lark-cli base +record-list \
  --base-token <APP> --table-id tblCwJGr0HTMFtXD \
  --filter '{"conjunction":"and","conditions":[
    {"field_name":"SKU","operator":"contains","value":"DRS-0429-FL"}
  ]}'
```

AI 读所有退货客户原话 → 提炼共性问题 → 给改进建议。

### 场景 C: AI 反推改进建议

提示词：
```
基于这批退货反馈，反推可改进的方面：
- 产品（版型/面料/工艺）
- 详情页（描述/图片/尺寸表）
- 客服话术（推荐/挽留）
- 物流（包装/速度）

输入：{退货数据}

输出每条改进建议含：
- 影响 SKU
- 优先级
- 预估降低退货率多少
```

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `11_退货反馈` | 读 |
| `01_产品库` | 读（关联款）|

## 四、典型对话示例

```
用户：看下这周退货为啥多

agent：
✓ 本周退货 87 单（上周 52 单，+67% ⚠️）
✓ 主因排序：
  1. 尺码不合 39 单（45%）→ 主要 DRS-0429-FL 偏小
  2. 色差 19 单（22%）→ 主要 SHT-0420-SP 海盐蓝偏深
  3. 面料 13 单（15%）

💡 改进建议：
- DRS-0429-FL 下批生产时放大尺码 1cm
- SHT-0420-SP 详情页加色卡说明
- 详情页统一加 "请按平时大一码"

📋 详情：https://my.feishu.cn/docx/<id>
```

## 五、与其他 skill 协作

- `product-library`：把改进意见写入产品 8 维详情
- `task-collaboration`：建给设计/客服的改进任务

## 六、参考

- [`../product-library/SKILL.md`](../product-library/SKILL.md)
- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
