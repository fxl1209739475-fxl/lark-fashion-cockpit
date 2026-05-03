---
name: lark-fashion-cockpit-knowledge-base
version: 1.0.0
description: "公司知识库 — 新品资料 / 客服话术 / 运营 SOP / 培训资料 沉淀。每次上新自动建知识库节点。当用户说「建知识库」「客服话术」「运营 SOP」「培训资料」「写新品资料」时使用。属于 lark-fashion-cockpit 公司管理板块。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 公司知识库

> **板块：** 🅴 公司管理  
> **调用：** `wiki` + `doc`  
> **多维表依赖：** `01_产品库`（拿产品信息生成知识页）

## 一、前置条件

```bash
lark-cli auth login --scope "wiki:wiki:readonly wiki:node:create wiki:node:update docs:document:write_only"
```

读 [`../../../lark-wiki/SKILL.md`](../../../lark-wiki/SKILL.md)。

## 二、工作流

### 场景 A: 新品上架自动建知识页

**触发语：** "X 款上架了，建个知识页" / "为新品建知识库"

```
Step 1: 读 01_产品库 拿产品信息（含 8 维详情）
Step 2: AI 整理成知识页结构（卖点/搭配/客户问答/搭配建议）
Step 3: lark-cli wiki +create-node 在指定知识空间建节点
Step 4: lark-cli docs +update 写入内容
```

#### Step 1+2: AI 提示词

```
基于这款产品的所有数据（产品库+8维详情），生成一份新品知识页：

# 1. 产品基本信息
款号 / 价格 / 颜色 / 尺码 / 面料

# 2. 核心卖点（3-5 条）

# 3. 搭配建议
（与本品牌其他款搭配 / 不同场景搭配）

# 4. 客户常见 Q&A（10 个）
- 这款显瘦吗
- 适合多少斤穿
- 面料会起球吗
- 怎么洗
...

# 5. 客服话术
- 推荐话术（X 客户问 X 时）
- 异议处理（不显瘦 / 偏贵 / 不耐穿）
```

#### Step 3+4: 建节点写内容

```bash
# 在知识空间建子节点
NODE_TOKEN=$(lark-cli wiki +create-node --space-id <品牌知识库 id> \
  --parent-token <新品资料根> --title "DRS-0429-FL 法式收腰碎花连衣裙" \
  --jq '.data.node.node_token')

# 写入内容（DocxXML）
lark-cli docs +update --api-version v2 --doc <node_token> --command overwrite \
  --content '<title>DRS-0429-FL 法式收腰碎花连衣裙</title>
<h1>1. 产品基本信息</h1>
...
<h1>5. 客服话术</h1>
<callout emoji="💬"><p>客户问"显瘦吗" → 答："收腰版型，腰围比胸围小 6cm，搭配同色系腰带显瘦效果加倍"</p></callout>'
```

### 场景 B: 通用 SOP 沉淀

**触发语：** "把 X 流程写进知识库"

适合做：
- 上新流程 SOP（11 步详解）
- 客服话术库（按品类）
- 退换货处理 SOP
- 主播培训手册
- 摄影规范

```bash
lark-cli wiki +create-node --space-id <id> --parent-token <运营 SOP 根> --title "X SOP"
lark-cli docs +update ... --content '...'
```

### 场景 C: 知识库搜索

**触发语：** "怎么处理 X 退货" / "X 客户问 Y 怎么答"

```bash
lark-cli docs +search --query "退货 处理" --filter '{"doc_types":["DOCX"]}'
```

## 三、涉及多维表 / 知识空间

| 资源 | 操作 |
|---|---|
| 飞书知识库（wiki space）| 读 / 写节点 |
| `01_产品库` | 读（拿信息生成页面）|

## 四、典型对话示例

```
用户：DRS-0429-FL 上架了，建个知识页

agent：
✓ 读取产品库 + 8 维详情数据
✓ AI 生成知识页内容（5 个章节，含 10 个 Q&A 和客服话术）
✓ 在知识库 [品牌资产/新品资料/2026春夏] 建节点
✓ 飞书文档已写入 → 已通知客服培训

📋 知识页：https://my.feishu.cn/wiki/<node_token>

补充建议：
- 给客服 @李四 推送培训提醒
- 把链接同步到 X 群（用户的客服群）
```

## 五、与其他 skill 协作

- `product-library`：知识页内容来源
- `meeting-workflow`：会议沉淀写入知识库
- `task-collaboration`：建客服培训任务

## 六、参考

- [`../../../lark-wiki/SKILL.md`](../../../lark-wiki/SKILL.md)
- [`../product-library/SKILL.md`](../product-library/SKILL.md)
