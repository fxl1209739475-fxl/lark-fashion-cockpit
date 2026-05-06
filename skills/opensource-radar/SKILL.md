---
name: lark-fashion-cockpit-opensource-radar
version: 1.0.0
description: "开源雷达 Skill — 每日自动扫描 GitHub 上的新发开源项目 + 趋势项目，AI 评估和女装电商/电商运营/公司管理的相关度，给出"如何改造应用到本组织"的具体改造思路，自动建到飞书知识库文档 + 早晨汇报卡片给老板和负责人。当用户说「开源雷达」「github 上有啥新东西」「今日开源推荐」「有什么开源项目能用」「组织技术升级建议」时使用。被动型提效 — 让组织在 AI/开源生态进化中实时跟进，不靠主动搜索。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 开源雷达 — 让组织被动跟上 AI 生态进化

> **🎯 核心痛点：** AI / 开源生态每天发新东西，老板娘没时间刷 GitHub，但每错过一个能用的项目就是错过一次组织提效机会。

> **核心创新：** 不是"我把开源项目拉下来用"（重）— 而是"AI 帮我评估每个新项目能不能用 + 怎么改造适配本组织"（轻）。**改造思路驱动 > 工具堆砌**。

> **被动 vs 主动：** 这是被动型提效 skill。每天自动跑，每天交付改造建议，组织只需要"读评估 + 拍板要不要改造"，不需要主动搜索。

---

## 一、工作流（每日早 8:00 自动跑）

```
每日 8:00 cron 触发 scan-github.py
  ↓
[1] 拉 GitHub Trending 今日热门（top 25）
[2] 关键词搜索新发：ecommerce / fashion / retail / shopify / inventory / AI agent / automation / operations
[3] 去重（用 28_开源雷达 表 + url 主键过滤已扫过的）
[4] 过滤低质量（star < 10 或 30 天没更新）
[5] DeepSeek 评估每个项目（5 维输出）：
    - 项目摘要（中文翻译扩写）
    - 和女装电商/管理相关度评分 1-10
    - 应用场景（女装直接用 / 电商通用 / 管理工具 / AI 基础 / 不相关）
    - 改造思路（具体到"改哪几个字段 / 接哪几个 API / 替换什么逻辑"）
    - 工时预估（小时）
[6] 高分项目（>=6）：
    - 写入 28_开源雷达 表
    - 自动建飞书知识库文档（详细版，含改造方案）
[7] 早 9:00 发飞书 IM 卡片汇报 TOP 5 给老板和部门负责人
[8] 评估结果写回 trigger-log.jsonl 持久化
```

---

## 二、前置条件

```bash
# 1. 装依赖
pip install httpx openai

# 2. 配凭证
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxx"
export DEEPSEEK_MODEL="deepseek-v4-pro"

# 3. （可选但强烈推荐）GitHub token — 无 token 限流 60/h，有 token 5000/h
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxx"

# 4. 飞书 base / wiki 认证
lark-cli auth login --scope "bitable:app:readwrite docx:document:write_only wiki:wiki"
export LARK_FASHION_COCKPIT_BASE_TOKEN="..."
export LARK_FASHION_COCKPIT_BOSS_CHAT="oc_xxx"

# 5. 知识库 space_id（用 lark-cli wiki +list 拿）
export LARK_WIKI_SPACE_ID="..."
```

---

## 三、初始化（建 28 表 + 灌示例数据）

```bash
python scripts/init-radar-table.py
# → 建表 28_开源雷达，含 13 字段：
#    项目名 / GitHub URL / star 数 / 最近更新 / 英文描述 / 中文摘要 /
#    相关度评分 / 应用场景 / 改造思路 / 工时预估 / 状态 / wiki 文档链接 / 扫描时间
```

---

## 四、运行

### 全自动模式（cron 推荐）
```bash
# 每日早 8:00 跑
0 8 * * * cd /path/to/lark-fashion-cockpit && python skills/opensource-radar/scripts/scan-github.py
```

### 手动触发
```bash
# 全量扫一次（GitHub trending + 关键词搜索）
python scripts/scan-github.py

# 只看某关键词
python scripts/scan-github.py --keyword "ai agent"

# 调高相关度门槛（默认 6）
python scripts/scan-github.py --min-score 7

# 不发卡片只更新表
python scripts/scan-github.py --no-card
```

### 飞书群主动触发
飞书发：`「开源雷达」` / `「今日开源推荐」` → event-listener 路由 → scan-github.py

---

## 五、AI 评估提示词（DeepSeek 用）

```python
PROMPT = """你是一位资深 AI/开源专家，专门为女装电商品牌主筛选 GitHub 项目。

【项目信息】
名称：{repo_name}
URL：{html_url}
描述：{description}
README 摘要：{readme_excerpt}
star 数：{stars}
语言：{language}
最近更新：{updated_at}

【组织背景】
本组织是一家女装电商品牌（lark-fashion-cockpit），核心业务：
- 4 平台运营（淘宝/抖音/小红书/视频号）
- 直播带货 / 短视频内容
- 团队协作（设计师 / 工厂 / 主播 / 客服 / 老板娘）
- 已有飞书 base 25 张表 + 32 个 sub-skill 覆盖商品/直播/审批/AI 数字员工等

【请输出 JSON】
{{
  "中文摘要": "...",
  "相关度评分": 1-10 整数,
  "应用场景": "女装直接用 | 电商通用 | 管理工具 | AI 基础设施 | 不相关",
  "改造思路": "具体到 改哪几个字段 / 接哪几个 API / 替换什么逻辑 / 联动 cockpit 哪个 skill",
  "工时预估小时": 整数,
  "判断理由": "1-2 句"
}}

注意：
- 相关度 ≥ 6 才会进飞书表，所以严格打分
- 改造思路要可执行，不要"可以参考"这种废话
- 如果是纯前端 UI / 游戏 / 区块链 等明显不相关，给 1-2 分
"""
```

---

## 六、典型输出（飞书知识库文档）

```markdown
# OpenAgentX - 开源 AI Agent 框架

**GitHub:** https://github.com/xxx/openagentx
**star:** 12,400 | **最近更新:** 2026-05-04 | **语言:** Python

## 中文摘要
轻量级 AI Agent 编排框架，支持多模态输入和工具链组合。
比 LangChain 简化 70% 代码量，专为生产环境设计。

## 为什么对女装电商有用 — 相关度 8/10
应用场景：AI 基础设施

我们 cockpit 已有 32 个 sub-skill，每个都是独立 Python 脚本。
OpenAgentX 可以替代我们的 ask-boss.py + product-matching 等 skill 内部
的 deepseek 直调代码，统一成 Agent 框架管理，好处：
1. 多 skill 之间共享上下文（老板娘问完产品搭配，下一句问"那备多少件"，AI 自动联动 launch-decision）
2. 工具调用有标准化，新 skill 接入只需 30 行代码
3. 错误重试 / 缓存 / token 监控原生支持

## 改造思路
1. **第 1 步**：把现有的 deepseek-v4-pro 直调改成 OpenAgentX agent
2. **第 2 步**：注册 cockpit 32 个 skill 为 OpenAgentX tool
3. **第 3 步**：给老板分身（boss-clone-aily）配 ReAct 循环 — 让她能多步推理
4. **第 4 步**：迁移 ask-boss.py / launch-decision.ps1 / product-matching.ps1 三个核心
5. 联动 cockpit skill：boss-clone-aily / launch-decision / product-matching / event-router

## 工时预估
**12-16 小时**（核心迁移 8h + 测试 4h + 文档 2h）

## 风险
- OpenAgentX 还在快速迭代，API 可能不稳
- 要重写测试用例
```

---

## 七、典型汇报卡片（早 9:00 发老板）

```
🛰 开源雷达 · 2026-05-05 早报

📊 今日扫描：48 个新项目 ｜ 高相关 5 个 ｜ 评估通过待审：3 个

🥇 TOP 5 推荐改造（按相关度排序）

[1] OpenAgentX · 相关度 8/10 · ⭐ 12.4k
   AI Agent 编排框架，可替代 cockpit deepseek 直调
   📋 工时 12-16h | 改造思路：[查看完整文档]

[2] FashionAttr · 相关度 8/10 · ⭐ 3.8k
   女装属性识别 ML 模型，可直接接 product-library
   📋 工时 4-6h | 改造思路：[查看]

[3] AutoLivePlanner · 相关度 7/10 · ⭐ 1.2k
   直播带货排期自动化，可联动 24_直播记录
   📋 工时 6-8h | 改造思路：[查看]

[4] ...
[5] ...

[📋 看完整 28 表] [📚 看本周开源雷达 wiki 文档]
```

---

## 八、与其他 skill 联动

- [`knowledge-base`](../knowledge-base/SKILL.md) — 高相关项目自动建 wiki 文档
- [`task-collaboration`](../task-collaboration/SKILL.md) — 老板批准改造 → 自动建任务给 CTO/技术负责人
- [`approval-flow`](../approval-flow/SKILL.md) — 涉及改造投入 > 16 小时的项目走审批

---

## 九、自演进机制

- 老板娘每次反馈"这个项目用了 / 不适合" → 写回 28 表「状态」字段
- 每周一跑 `scripts/learn-relevance.py` → 用真实反馈数据反向调 DeepSeek 评估提示词
- 越用越准

---

## 十、参考

- 主脚本：[`scripts/scan-github.py`](./scripts/scan-github.py)
- 表初始化：[`scripts/init-radar-table.py`](./scripts/init-radar-table.py)
- 改造模板：[`references/refit-template.md`](./references/refit-template.md)
- 完整示例：[`examples/sample-report.md`](./examples/sample-report.md)
- GitHub API 限流提示：[`references/github-api-tips.md`](./references/github-api-tips.md)
