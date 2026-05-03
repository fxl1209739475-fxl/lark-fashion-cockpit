---
name: lark-fashion-cockpit-private-domain
version: 1.0.0
description: "私域 + 服务体验 — 客户分层、私域来源、今日运营动作、客服体验。当用户说「看客户」「VIP 客户」「私域增长」「客服满意度」「今日运营动作」时使用。属于 lark-fashion-cockpit 销售增长板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 私域 + 服务体验

> **板块：** 🅲 销售增长  
> **调用：** `base` + `im` + `task`  
> **多维表依赖：** `10_客户分层`（核心）/ `11_退货反馈`

## 一、前置条件

```bash
lark-cli auth login --scope "base:record:read im:message:write task:task:write"
```

## 二、工作流

### 场景 A: 客户分层概览

**触发语：** "看客户" / "客户分层" / "VIP 客户"

```bash
lark-cli base +data-query \
  --base-token <APP> --table-id tblMTkWGlIlnTcMA \
  --json '{
    "table_name":"10_客户分层",
    "count_all":true,
    "group_by":[{"field_name":"层级","mode":"integrated"}]
  }'

# 总贡献 GMV
lark-cli base +data-query \
  --base-token <APP> --table-id tblMTkWGlIlnTcMA \
  --json '{
    "table_name":"10_客户分层",
    "series":[{"field_name":"总贡献","rollup":"SUM"}],
    "group_by":[{"field_name":"层级","mode":"integrated"}]
  }'
```

### 场景 B: 今日运营动作推荐

**触发语：** "今日运营做什么" / "私域运营动作"

```
Step 1: AI 基于客户分层 + 销售数据 + 上新波段，推荐今日动作
Step 2: 输出动作列表（每条含：客群/动作/预期效果）
Step 3: 建任务给运营 / 客服
```

示例输出：
- 钻石客户 12 人 → 上新预告 + 优先抢购券（@运营）
- 30 天未复购的黄金客户 → 召回礼券（@客服）
- 抖音粉丝 → 福利专场直播预告（@主播）

### 场景 C: 服务体验复盘

**触发语：** "客服满意度" / "服务体验"

```bash
# 读 11_退货反馈 算退货率 + 主因
lark-cli base +data-query \
  --base-token <APP> --table-id tblCwJGr0HTMFtXD \
  --json '{
    "table_name":"11_退货反馈",
    "count_all":true,
    "group_by":[{"field_name":"退货原因","mode":"integrated","sort":{"type":"value","order":"desc"}}]
  }'
```

AI 整理 + 给商品/运营/客服提改进建议。

## 三、涉及多维表

| 表 | 操作 |
|---|---|
| `10_客户分层` | 读 / 写 |
| `11_退货反馈` | 读 |

## 四、典型对话示例

```
用户：今日运营做什么

agent：
✓ 客户分层扫描完成：钻石 12 / 黄金 89 / 白银 234 / 普通 1450
✓ AI 推荐 3 个动作：

1. [钻石客户 12 人] 早春第一波上新预告 + 早鸟券
   预期：复购率 +20%
   建议执行：@运营 王五

2. [30 天未复购的黄金客户 18 人] 召回礼券（满 200 减 50）
   预期：回流 5-7 单
   建议执行：@客服 李四

3. [新粉丝群 30 人] 福利专场直播预告
   预期：拉新转化 +15%
   建议执行：@主播 张三

是否要批量建任务？(Y/N)
```

## 五、与其他 skill 协作

- `task-collaboration`：建运营任务
- `morning-report`：晨报展示客户层级数
- `live-streaming`：召回客户专场直播

## 六、参考

- [`../task-collaboration/SKILL.md`](../task-collaboration/SKILL.md)
- [`../live-streaming/SKILL.md`](../live-streaming/SKILL.md)
