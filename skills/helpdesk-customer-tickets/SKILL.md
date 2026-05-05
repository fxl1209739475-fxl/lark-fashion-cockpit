---
name: lark-fashion-cockpit-helpdesk-tickets
version: 1.0.0
description: "把抖音/淘宝/微信客户问题汇入飞书服务台 — 工单统一管理、AI 自动初步回复建议、客服在飞书内一站处理。基于飞书服务台 v1 API。当用户说「客户工单」「退货咨询」「客服工作台」「集成多平台客服」时使用。属于 lark-fashion-cockpit 销售增长板块。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli api GET /open-apis/helpdesk/v1/tickets"
---

# 飞书服务台 · 客户工单集成

> **🎯 老板娘的痛点：** 客户问题分散在抖音 / 淘宝 / 视频号 / 微信 4 个平台，客服切换 4 个后台，质量参差不齐，数据无法沉淀复盘。

> **载体：** 飞书服务台
> **数据沉淀：** 11_退货反馈 表（已有）+ 客户工单流水
> **客户体验：** 完全无感（客户在原平台收到回复，只是回复来自飞书机器人代发）

---

## 一、能否真集成多平台 — 实话实说

| 平台 | 飞书原生集成 | 第三方桥接 | 可行性 |
|---|---|---|---|
| 飞书内员工咨询 | ✅ 原生 | - | ⭐⭐⭐⭐⭐ |
| **抖音客户咨询** | ❌ 无原生 | ✅ OpenClaw / Coze 桥接 | ⭐⭐⭐⭐ |
| **淘宝客户咨询** | ❌ 无原生 | ⚠ 千牛 API 半开放 | ⭐⭐ |
| **视频号客户咨询** | ❌ 无原生 | ⚠ 微信 API 受限 | ⭐⭐ |
| **微信客户咨询** | ❌ 无原生 | ⚠ 通过企业微信中转 | ⭐⭐ |

**结论：** 最稳的两条路：
1. **飞书内部员工咨询**（IT/HR 客服场景）→ 原生服务台 100% 能用
2. **抖音对接**（OpenClaw 桥接）→ 第三方工具 + 1-2 天集成

**比赛建议**：先做内部员工咨询场景做 demo（"团队问题统一通过工单解决"），多平台标"商业化路线图"。

---

## 二、典型场景

### 场景 A：内部员工咨询（最稳）
```
设计师马萍蔓 → 飞书服务台 → 提问"DRS-0429 的色卡能再发我一份吗"
   → 自动建工单 → 分配给生产主管申丽媛
   → 申丽媛飞书内回复 → 工单解决 → 数据沉淀
```

### 场景 B：客户售后（多平台桥接）
```
客户在抖音问"这件能不能 39 码？"
   → OpenClaw 桥接 → 飞书服务台 自动建工单
   → AI 给初步回复建议（基于历史 11_退货反馈 + 01_产品库）
   → 客服在飞书内审核 / 修改 / 一键发送
   → OpenClaw 把回复发回抖音 IM
   → 客户在抖音收到（完全无感）
```

---

## 三、API 调用示例

```bash
# 3a. 创建工单（员工/客户提交问题）
lark-cli api POST /open-apis/helpdesk/v1/tickets/start_service \
  --data '{
    "user_id": "ou_xxx",
    "human_service": false,
    "appointed_agent_ids": []
  }' \
  --jq '.data.ticket_id'

# 3b. 列工单（客服查待处理）
lark-cli api GET /open-apis/helpdesk/v1/tickets \
  --params '{"status":1, "page": 1, "page_size": 20}'
# status: 1=新建 / 2=处理中 / 3=已解决

# 3c. 客服回复
lark-cli api POST /open-apis/helpdesk/v1/tickets/{ticket_id}/answer_user_query \
  --data '{"event_id": "msg_xxx", "faqs": [...]}'

# 3d. 工单状态更新
lark-cli api PUT /open-apis/helpdesk/v1/tickets/{ticket_id} \
  --data '{"status": 3, "tags": ["已解决", "退货"], "comments": "..."}'
```

---

## 四、与其他 skill 联动

- **feedback-returns（退货反馈）**：工单解决后自动写入 11_退货反馈 表做数据沉淀
- **boss-clone-aily**：高优工单自动调老板分身建议处理方案
- **knowledge-base / lingo**：客服回复时自动 hover 词条 / 引用 wiki 答案

---

## 五、AI 自动初步回复（核心增值）

`scripts/helpdesk-ai-suggester.py`：拉新工单 → 调 deepseek + 历史 11_退货反馈 → 给客服一份建议回复

```python
def suggest_reply(ticket):
    similar = search_similar_complaints(ticket.user_query)
    history = get_user_purchase_history(ticket.user_id)

    prompt = f"""客户问题: {ticket.user_query}
    客户历史购买: {history}
    类似历史投诉: {similar[:3]}

    请按老板娘风格给一份初步回复（先共情 + 给方案 + 不抹黑产品）"""

    return deepseek_call(prompt)
```

实证数据：响应时长 ↓ 58%，效率 ↑ 40%（参考美宜佳/海底捞案例）。

---

## 六、Demo 预览

无需部署，直接打开 `examples/helpdesk-demo.html` 看 UI 模拟（飞书服务台工单看板）。

---

## 七、卡点 / 已知风险

- 多平台真接通需要第三方 OpenClaw / Coze（独立成本约 ¥200-500/月）
- 飞书服务台**企业版才完整支持**（工单流转 / 客服技能路由），免费版受限
- 老板娘当前飞书租户类型未知 → 真上线前需要确认是否需要升级
