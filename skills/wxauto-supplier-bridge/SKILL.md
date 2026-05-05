---
name: lark-fashion-cockpit-wxauto-supplier-bridge
version: 1.0.0
description: "飞书 → 微信桥 — 老板娘飞书发指令「问 ZC工厂 有没有 DRS-0429 同款雪纺」→ wxauto 自动控制 PC 微信 → 找联系人 → 发消息 → 对方微信收到（无感）。仅老板娘 owner 可用，仅白名单供应商（28 表登记），频率限制 ≤ 5 条/分钟，防风控。当用户说「问 XX 工厂 / 问面料商 / 给 XX 发微信 / 通知供应商」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["wxauto"]
---

# 飞书 → 微信桥 · 给固定供应商发消息

> **🎯 老板娘的痛点：** 我在飞书指挥 cockpit，但跟工厂供应商沟通要切微信手敲。一天问 5 个面料商同样的问题，5 次手打。

> **核心价值：** 飞书一句话指令 → wxauto 控制 PC 微信 → 自动给指定供应商发消息。**省 80% 沟通切换成本**。

---

## 一、为什么这个 skill 风险可控

公认 wxauto 给陌生人群发会被封号。但**给固定供应商低频发送**风险极低：

| 微信风控看的 | 老板娘场景 | 风险 |
|---|---|---|
| 给陌生人群发 | ❌ 不做 | 必封 |
| 短时间发 100+ 条 | ❌ 频率限制 ≤ 5 条/分钟 | 触发 |
| 同样模板群发 | ⚠️ 每次自动加 supplier 名个性化 | 低 |
| 给固定 5-20 个老朋友/供应商发 | ✅ 你日常聊天就这么多 | **低** |
| 24h 持续运行抓数据 | ❌ 我们只在你触发时调一次 | 低 |

**核心安全机制（4 层）：**
1. **仅 owner 可触发**（role-registry.json 校验，员工冒用直接拒）
2. **白名单制**（只能给 28_供应商档案 表 status=活跃 的发）
3. **频率限制**（≤ 5 条/分钟，超过排队）
4. **审计留痕**（每条消息记 `logs/wxauto-audit.jsonl`）

---

## 二、前置条件

```bash
# 1. 装依赖（推荐 wxauto-4.0 适配新版微信）
pip install wxauto

# 2. PC 微信 4.0+ 客户端登录（重要）
# Windows 微信桌面版必须开着 + 已登录

# 3. 飞书认证（cockpit 已配）
lark-cli auth login --scope "bitable:app:readwrite im:message:send"

# 4. 配凭证（.env）
LARK_FASHION_COCKPIT_BASE_TOKEN=...
TABLE_SUPPLIERS=tblxxxxxx  # 28_供应商档案 表 id
```

---

## 三、初始化（建 28_供应商档案 表 + 灌示例）

```bash
python scripts/init-supplier-table.py
```

建出 28 表，含字段：

| 字段 | 类型 | 用途 |
|---|---|---|
| 供应商名 | text | 「ZC 工厂 / GS 工厂 / 杭州面料商」 |
| 微信备注名 | text | 你微信通讯录里的真实备注名（wxauto 找联系人用）|
| 类别 | select | 面料商 / 辅料商 / 成衣工厂 / 印花厂 / 物流 |
| 联系状态 | select | 活跃 ✅ / 备选 ⚠️ / 黑名单 ❌（曾跑路）|
| 备注 | text | 工艺特长、合作历史、注意事项 |
| 上次沟通 | datetime | 自动写入 |
| 累计消息数 | number | 自动累计 |

---

## 四、典型使用场景

### 场景 A：单点询问
```
老板娘 → 飞书发: 问 ZC工厂 有没有 DRS-0429 同款奶茶白雪纺面料

event-listener:
  ① 路由 SUPPLIER_ASK_RE 匹配
  ② 校验 role=owner ✅
  ③ 查 28 表 → 找到「ZC 工厂」微信备注名 = "浙江老张"
  ④ 调 send-to-supplier.py
     wx.ChatWith("浙江老张")
     wx.SendMsg("(老板娘 cockpit 自动消息)\n\n问下：DRS-0429 同款奶茶白雪纺面料还有吗？需求量 500m。请回复确认。")
  ⑤ 飞书回卡片"✅ 已发给 浙江老张（ZC 工厂）"
  ⑥ 写 logs/wxauto-audit.jsonl
```

### 场景 B：群发同类供应商
```
老板娘 → 飞书发: 问所有面料商 DRS-0429 雪纺面料 5 月底能到货的回我

执行：
  ① 查 28 表 type=面料商 + 状态=活跃，得到 5 个供应商
  ② 逐个发（每条间隔 12 秒，5 个 = 60 秒发完）
  ③ 飞书发汇报卡："已问 5 个面料商，等待回复"
```

### 场景 C：监听回复（高级）
```
wxauto 后台监听新消息：
  - 检测到供应商回复 → 飞书发卡片通知老板娘
  - 自动 AI 摘要回复要点
  - 写到 28 表的"上次沟通"字段
```

---

## 五、event-listener 路由（要加进 event-listener.py）

```python
# 单点询问：「问 [供应商名] [问题]」
SUPPLIER_ASK_RE = re.compile(r"^问\s*(\S+?)(?:工厂|供应商)?\s+(.+)$")

# 群发：「问所有 [类别] [问题]」
SUPPLIER_BROADCAST_RE = re.compile(r"^问所有\s*(\S+?)(?:商|工厂|供应商)?\s+(.+)$")

# 在 handle_message 里：
m_ask = SUPPLIER_ASK_RE.match(text)
if m_ask:
    if user_config["role"] != "owner":
        send_card(chat_id, "🚫 权限不足", "微信桥仅老板可用（防冒用您私号）", "red")
        return
    supplier_name = m_ask.group(1)
    question = m_ask.group(2)
    # 调 send-to-supplier.py
    subprocess.run(["python", "skills/wxauto-supplier-bridge/scripts/send-to-supplier.py",
                    "--supplier", supplier_name, "--message", question],
                   ...)
```

---

## 六、安全限制（再次强调）

| 限制 | 实现 |
|---|---|
| 仅老板娘 owner 可用 | role-registry 角色校验 |
| 仅白名单供应商 | 28 表 status=活跃 才发 |
| 频率限制 ≤ 5 条/分钟 | scripts 内 sleep 12s 间隔 |
| 单日上限 50 条 | 检查 audit.jsonl 当日累计 |
| 必须 PC 微信登录 | wxauto 启动时检测 |
| 每条记 audit | logs/wxauto-audit.jsonl |
| 重要消息草稿模式 | --dry-run 选项让 ta 飞书审核后人工点发 |

---

## 七、与其他 skill 联动

- **`production-supplier`** — 自动调本 skill 通知工厂任务变更
- **`launch-decision`** — 老板娘批准下单建议 → 自动通知对应工厂
- **`stock-replenishment`** — 库存预警触发 → 自动询面料商
- **`feedback-returns`** — 退货质量问题 → 自动跟进相关工厂
- **`task-collaboration`** — 跨租户朋友任务 → 同时微信通知（双触达）

---

## 八、参考

- 主脚本：[`scripts/send-to-supplier.py`](./scripts/send-to-supplier.py)
- 群发脚本：[`scripts/broadcast-to-suppliers.py`](./scripts/broadcast-to-suppliers.py)
- 建表脚本：[`scripts/init-supplier-table.py`](./scripts/init-supplier-table.py)
- 监听回复（赛后做）：[`scripts/listen-replies.py`](./scripts/listen-replies.py)
- 风险评估：[`references/risk-assessment.md`](./references/risk-assessment.md)
- 完整对话样例：[`examples/sample-conversations.md`](./examples/sample-conversations.md)
