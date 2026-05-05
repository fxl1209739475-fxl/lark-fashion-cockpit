---
name: lark-fashion-cockpit-workplace-block
version: 1.0.0
description: "在飞书工作台首页放 cockpit 仪表盘小组件 — 员工每次打开飞书工作台就看到「今日 GMV / 紧急任务 / 直播倒计时 / 库存预警」等核心数据。可点击下钻到对应表。基于飞书工作台小组件（Block）开放能力。当用户说「工作台首页」「打开飞书就看到」「全店仪表盘」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "node"]
---

# 工作台小组件 · cockpit 仪表盘 — 员工打开飞书就看到

> **🎯 老板娘的痛点：** cockpit 数据全在群卡片 / 多维表里，员工要点几下才能看到。**工作台首页**是飞书最高曝光位置，应该把核心数字直接展示。

> **板块：** 公司经营（视觉化升级版）
> **数据源：** 02_4平台销售（GMV）+ 05_任务清单（待办）+ 24_直播记录（直播倒计时）+ 03_库存预警
> **入口：** 飞书 PC / app → 左侧导航「工作台」→ 首页第一个 widget

---

## 一、为什么用工作台 widget 而不是 IM 卡片

| 维度 | IM 卡片版（现在）| 工作台 Widget |
|---|---|---|
| 曝光时机 | 卡片发出来一闪即过，滚屏找不到 | **永久驻留首页**，员工每次打开飞书都看 |
| 谁能看到 | 群成员 | **任何打开飞书的员工**（按权限） |
| 角色化 | 同一张卡片所有人看 | **不同角色看不同数据**（老板 / 设计师 / 主播） |
| 交互 | 卡片按钮跳一下 | **数字本身可点**，下钻到对应表 |
| 数据新鲜度 | 发那一刻 | **可设自动刷新**（每 5 分钟拉一次） |
| 跨设备 | 群消息要翻历史 | PC / iPad / 手机 一致 |

---

## 二、Widget 内容设计（按角色分版本）

### 老板娘版（默认）
```
┌──────────────────────────────────┐
│ 🚀 lark-fashion-cockpit          │
├──────────────────────────────────┤
│ 今日 GMV       ¥42,650 🟢 (+12%) │ ← 点击 → 02_4平台销售
│ 紧急任务       3 项🔴            │ ← 点击 → 05_任务清单 已升级视图
│ 下场直播       14:00（2 小时）    │ ← 点击 → 24_直播记录
│ 库存预警       DRS-0429 仅 12 件  │ ← 点击 → 03_库存预警
│ AI 老板分身    [一键问问]         │ ← 点击 → 跳 ask-boss-aily
└──────────────────────────────────┘
```

### 设计师版
```
┌──────────────────────────────────┐
│ 🎨 我的设计任务                   │
├──────────────────────────────────┤
│ 待交稿          3 件（最早 18:00） │
│ 已完成          12 件本周          │
│ 改稿请求        2 件（DRS-0429）  │
│ 灵感板         [打开]             │
└──────────────────────────────────┘
```

### 主播版
```
┌──────────────────────────────────┐
│ 📺 今日直播                       │
├──────────────────────────────────┤
│ 下场倒计时      14:00 (1h 47m)    │
│ 上场 GMV        ¥18,650           │
│ TOP 单品        DRS-0429（35 件）  │
│ 今日重点款      [查看 8 款]       │
│ 库存提示        [3 款补货]        │
└──────────────────────────────────┘
```

---

## 三、前置条件

```bash
# 飞书开发者后台 → 创建应用 → 类型选「网页应用」
# 申请权限：
# - bitable:app:readonly （读 base 数据）
# - workplace:block:readonly （工作台部署）
```

---

## 四、Widget 实现

### 4a. 后端（数据 API）

`scripts/cockpit-widget-api.py`：HTTP 服务暴露每个 widget 数据接口

```python
# Flask / FastAPI 实现
@app.get("/api/widget/cockpit-summary")
def cockpit_summary():
    return {
        "gmv_today": 42650,
        "gmv_growth": "+12%",
        "urgent_tasks": 3,
        "next_livestream": {"time": "14:00", "countdown_min": 117},
        "stock_alerts": [{"product": "DRS-0429", "qty": 12}],
    }

@app.get("/api/widget/designer/{user_id}")
def designer_widget(user_id):
    # 拉 05_任务清单 该设计师的任务
    return {...}
```

### 4b. 前端（Block 模板，React）

```jsx
// src/CockpitBlock.jsx
import { useEffect, useState } from 'react';

export default function CockpitBlock({ apiHost }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = () => fetch(`${apiHost}/api/widget/cockpit-summary`)
      .then(r => r.json()).then(setData);
    load();
    const t = setInterval(load, 5 * 60 * 1000);  // 5 分钟刷新
    return () => clearInterval(t);
  }, []);

  if (!data) return <div>加载中...</div>;

  return (
    <div className="cockpit-block">
      <h3>🚀 lark-fashion-cockpit</h3>
      <Row label="今日 GMV" value={`¥${data.gmv_today.toLocaleString()}`}
           growth={data.gmv_growth}
           onClick={() => openTable('tbll7UHbL6kDxZua')} />
      <Row label="紧急任务" value={`${data.urgent_tasks} 项 🔴`}
           onClick={() => openTable('tblRnB14n1xW1vou')} />
      {/* ... 其他行 ... */}
    </div>
  );
}

function Row({ label, value, growth, onClick }) {
  return (
    <div className="row" onClick={onClick}>
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {growth && <span className="growth">{growth}</span>}
    </div>
  );
}

function openTable(tableId) {
  const url = `https://my.feishu.cn/base/LWsdbVtIaa2MaDsANm3cNdYgn1j?table=${tableId}`;
  window.open(url, '_blank');
}
```

### 4c. 注册到飞书工作台

```bash
# 飞书开发者后台 → 应用 → 添加能力 → 「工作台小组件」
# 上传 build dist + 配置 widget 元信息（标题/图标/默认尺寸）
# 管理员给企业工作台添加这个 widget
```

---

## 五、与其他 skill 联动

- **morning-report**：早 8:00 触发的经营晨报数据 = widget 数据源
- **task-tracker**：紧急任务数 / 待办数据
- **livestream-daily-report**：直播倒计时和 GMV
- **launch-decision** / **product-matching**：库存预警 / 翻单提示

---

## 六、Demo 预览

无需部署，直接打开 `examples/cockpit-block-demo.html` 看 UI 模拟（PC 工作台样式）。
