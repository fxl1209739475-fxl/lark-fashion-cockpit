---
name: lark-fashion-cockpit-boss-clone-aily
version: 1.0.0
description: "把老板娘的决策风格蒸馏成飞书 Aily 智能伙伴 — 员工在飞书里直接 @「老板娘 AI」就能问，老板不在场也能拿到接近真人的判断。当用户说「问老板」「老板会怎么决定」「老板分身」「该不该 X」「下单建议（AI 老板视角）」时使用。基于 26_老板语料库 200 题问答 + 飞书 Aily v1 API。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli api GET /open-apis/aily/v1/sessions"
---

# 老板分身 · 飞书 Aily 版 — 让团队在飞书里直接「问老板」

> **🎯 老板娘的痛点：** 团队下单决策、产品会、风险判断都要等老板在场。老板手机不在身边，工厂催报单、设计师卡需求、客服等审批 — 全都僵着。

> **板块：** 🅱 商品中心 / 🅴 公司管理（跨板块的"AI 数字员工"）
> **数据源：** `26_老板语料库`（200 题）+ `08_教训库` + `14_审批记录` + 历史决策对话
> **载体：** 飞书 Aily 智能伙伴应用 — 员工在飞书搜「老板娘 AI」就出来对话

---

## 一、为什么用 Aily 而不是 IM 卡片

| 维度 | 现在 ask-boss.py + IM 卡片 | 升级到飞书 Aily |
|---|---|---|
| 谁能用 | 老板娘自己（要懂关键词） | **全员可用，搜助手名字就能聊** |
| 上下文 | 单次问答，无记忆 | **多轮对话，记得你昨天问过什么** |
| 工具调用 | 只能输出文本 | **能调飞书 API**（建任务/查表/发审批） |
| 知识库 | 单表 RAG | **多表/多文档/网页** 混合 RAG |
| 维护门槛 | 改 Python 代码 | **拖拽配置**（运营自己改） |
| 比赛角度 | Python 脚本 | **飞书 2025 最新 AI 平台原生集成** |

**核心升级**：从"老板娘个人工具" → "全员可用的 AI 数字员工"。

---

## 二、前置条件

```bash
lark-cli auth login --scope "aily:session aily:message aily:run aily:skill"
```

需要权限：
- `aily:session:write` — 创建/更新会话
- `aily:message:write` — 发送消息给 Aily 助手
- `aily:run:write` — 触发 Aily 运行
- 飞书 Aily 应用一个（在 https://aily.feishu.cn 创建，详见 `docs/AILY-SETUP.md`）

---

## 三、工作流（三个使用场景）

### 场景 A：员工日常问答（最常用）

**触发语：** "问老板娘 [问题]" / "@老板娘 AI [问题]" / 在 Aily 里直接聊

```bash
# 第 1 步：创建一次会话（同一员工连续提问可复用 session_id 实现多轮记忆）
lark-cli api POST /open-apis/aily/v1/sessions \
  --data '{"channel_context": "{\"chat_id\":\"oc_xxx\",\"user_id\":\"ou_xxx\"}"}' \
  --jq '.data.session.id'
# → 返回 session_id 比如 "session_aabbcc"

# 第 2 步：发问题给 Aily
lark-cli api POST /open-apis/aily/v1/sessions/session_aabbcc/messages \
  --data '{"content": "DRS-0429-FL 这款备 500 件还是 1000 件？", "content_type": "MDX"}'

# 第 3 步：触发一次 Aily 运行（让它处理消息）
lark-cli api POST /open-apis/aily/v1/sessions/session_aabbcc/runs \
  --data '{"app_id": "spring_xxxxx"}' \
  --jq '.data.run.id'

# 第 4 步：拉取 Aily 回复
lark-cli api GET /open-apis/aily/v1/sessions/session_aabbcc/messages \
  --jq '.data.messages | last'
```

### 场景 B：直接调技能（绕过对话，要结构化输出）

**触发语：** 系统/工作流自动调用，不走人聊天

```bash
# 调用 Aily 应用预定义的"下单决策"技能
lark-cli api POST /open-apis/aily/v1/apps/spring_xxx/skills/skill_xxx/start \
  --data '{
    "input": {
      "product_id": "DRS-0429-FL",
      "season": "2026-spring",
      "fans_estimate": 1500
    }
  }'
# 同步返回：{"output": {"recommended_qty": 800, "size_ratio": "S:30 M:40 L:30", "reason": "..."}}
```

### 场景 C：知识库一键问答（语料库智能查询）

```bash
# 直接基于 26_老板语料库 + 08_教训库 做语义检索 + 回答
lark-cli api POST /open-apis/aily/v1/data_knowledge/ask \
  --data '{
    "query": "去年同款备货失败的教训",
    "data_categories": ["category_lessons"]
  }'
```

---

## 四、涉及的飞书 base 表

| 表 | 用途 |
|---|---|
| `26_老板语料库` (`tblroqP4Kuz8a1yq`) | 200 题问答 → Aily 数据知识 |
| `08_教训库` | 每次 launch-decision 反哺的教训 |
| `14_审批记录` | 历史审批决策（学习老板的审批风格） |

---

## 五、典型对话示例

```
设计师马萍蔓 →「@老板娘AI 这款印花连衣裙我想做，但是面料贵 30%」

老板娘 AI：
  根据老板娘的判断风格（基于 26_语料库 + 08_教训库 综合）：

  ⚠️ 不建议押。理由：
  1. 老板娘对印花款的容忍度低（语料 B-3 / B-37 显示）
  2. 面料贵 30% 已超过她容忍度上限（语料 A-5：" 工厂报价高 10% 是上限"）
  3. 同类爆款历史教训（08_教训库 #L-007）：印花连衣裙退货率高 22%

  💡 替代方案：改纯色试水（老板娘提过 B-3 "印花用基础色款探路"）
  📋 [一键建任务] [一键起审批]
```

老板娘真在场可以直接在 Aily 里说"我同意" / "那就照分身建议来" → Aily 自动建任务 + 起审批。

---

## 六、与其他 skill 协作

- **launch-decision**：分身代老板复审下单决策（90% 一致直接通过，反对时找真老板）
- **task-collaboration**：分身建议被采纳后自动建任务给对应角色
- **approval-flow**：分身可代起审批，老板手机一点完成
- **knowledge-base**：分身回答时自动联动 wiki 上的运营手册

---

## 七、参考

- 操作手册（5 分钟搭 Aily 应用）：[`references/AILY-SETUP.md`](./references/AILY-SETUP.md)
- 后端脚本：[`scripts/ask-boss-aily.py`](./scripts/ask-boss-aily.py)
- 原 Python 版（IM 卡片）：[`scripts/ask-boss.py`](./scripts/ask-boss.py)
- 编译人格档案：[`scripts/build-boss-persona.py`](./scripts/build-boss-persona.py)
- 灌入 200 题：[`scripts/seed-boss-qa.py`](./scripts/seed-boss-qa.py)
- 飞书 Aily 官方文档：https://open.feishu.cn/document/aily-v1
