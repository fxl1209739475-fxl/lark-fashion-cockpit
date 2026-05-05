---
name: lark-fashion-cockpit-base-extension-product-matcher
version: 1.0.0
description: "在飞书多维表格 01_产品库 内置 AI 一键搭配按钮 — 员工选产品行 → 点按钮 → 弹侧边栏出 5 套 AI 搭配建议。基于多维表格自动化插件（addAction）。当用户说「在多维表里点按钮搭配」「右键 AI 搭配」「多维表插件」时使用。属于 lark-fashion-cockpit 商品中心板块（多维表生态扩展）。"
metadata:
  requires:
    bins: ["lark-cli", "node"]
---

# 多维表格插件 · AI 一键搭配 — 全员可用版

> **🎯 老板娘的痛点：** 你能用 cockpit 的产品搭配 skill，但**员工只会鼠标点点**，不会发命令。

> **载体：** 飞书多维表格自动化插件（base-automation-extensions）
> **数据源：** 01_产品库（元素标签 32 选项 × 5 维）+ 17_产品搭配组
> **入口：** 多维表格右上角「插件」→「🤖 AI 一键搭配」按钮

---

## 一、为什么用多维表插件而不是 IM 卡片

| 维度 | IM 卡片版 | 多维表插件 |
|---|---|---|
| 谁能用 | 老板娘（要发命令） | **任何打开多维表的员工**（鼠标点） |
| 入口 | 飞书群关键词 | **多维表右上角扩展菜单** |
| 输入 | 文字（"DRS-0429 配什么"） | **直接选产品行 → 自动带产品 ID** |
| 输出 | 飞书卡片（看完就翻篇） | **侧边栏面板**（持续展示，可导出 / 一键写入 17_产品搭配组）|
| 学习成本 | 记关键词 | **0 学习，看到按钮就会用** |

---

## 二、前置条件

```bash
# 飞书开发者后台创建应用 → 申请权限
# 多维表格自动化插件需要的 scope：
# - bitable:app:readonly
# - bitable:record:readonly
# - bitable:field:readonly
```

需要：
- 飞书企业开发者账号
- node.js（已装 v24.15.0）
- 多维表格 base：`LWsdbVtIaa2MaDsANm3cNdYgn1j`
- 01_产品库 表：`tblrKzymnPPQ98ZX`

---

## 三、插件实现（addAction 模式）

```javascript
import { addAction, FormItem, ResultType, t } from '@base-open/automation-extensions';

addAction({
  id: 'fashion-product-matcher',
  name: t('AI 一键搭配建议'),
  description: t('选中一行产品 → 调 product-matching skill → 返回 5 套搭配'),

  formItems: [
    {
      key: 'product_id',
      label: t('产品 ID'),
      component: 'Input',
      required: true,
      componentProps: { placeholder: 'DRS-0429-FL' },
    },
    {
      key: 'season',
      label: t('季节'),
      component: 'SingleSelect',
      componentProps: {
        options: [
          { value: 'spring', label: '春' },
          { value: 'summer', label: '夏' },
          { value: 'autumn', label: '秋' },
          { value: 'winter', label: '冬' },
        ]
      },
    },
    {
      key: 'top_k',
      label: t('搭配数量'),
      component: 'SingleSelect',
      componentProps: { options: [3, 5, 8].map(n => ({ value: n, label: `${n} 套` })) },
    },
  ],

  resultType: {
    type: 'Array',
    items: {
      type: 'Object',
      properties: {
        rank: { type: 'Number', label: t('排名') },
        partner_id: { type: 'String', label: t('搭配款') },
        score: { type: 'Number', label: t('AI 评分') },
        reason: { type: 'String', label: t('搭配理由') },
        inventory_alert: { type: 'String', label: t('库存提示') },
      },
    },
  },

  async execute({ params, context }) {
    // 调用 cockpit 后端 product-matching skill
    const resp = await fetch('https://your-cockpit-host/api/product-matching', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: params.product_id,
        season: params.season,
        top_k: params.top_k,
      }),
    });
    const data = await resp.json();
    return { code: 0, data: data.matches };
  },
});
```

---

## 四、典型使用流程

```
1. 设计师打开 01_产品库 多维表
2. 选中 DRS-0429-FL 这一行
3. 右上角点「插件」→「🤖 AI 一键搭配」
4. 弹表单：
   - 产品 ID: [自动填入 DRS-0429-FL]
   - 季节: [选 春]
   - 搭配数量: [选 5 套]
   - 点「执行」
5. 等 5-10 秒
6. 弹侧边栏出 5 套搭配（按 AI 评分排序，含库存提示）
7. 设计师可一键把结果写入 17_产品搭配组 表
```

---

## 五、与其他 skill 联动

- **product-matching**：本插件的后端引擎（同样的算法换 UI 入口）
- **inventory-gmv-matcher**：库存提示靠它（"DRS-0429 仅 12 件，建议先卖再翻单"）
- **launch-decision**：搭配组确定后联动下单决策

---

## 六、部署方式

1. `cd skills/base-extension-product-matcher && npm install`
2. `npm run build` → 生成 dist 包
3. 飞书开发者后台 → 应用 → 「自动化插件」→ 上传 dist
4. 多维表格管理员一键安装到 01_产品库

---

## 七、Demo 预览

无需部署，直接打开 `examples/product-matcher-demo.html` 在浏览器看 UI 模拟（侧边栏样式 + 5 套搭配卡片）。
