# 自然语言路由 — 真实员工对话集

## 场景 1：老板娘移动端飞书 app

```
老板娘 → 飞书群: "今天卖得咋样"
NLU 识别: skill=morning-report, confidence=0.92
触发: morning-report.ps1
回复: 完整经营晨报卡片（4 平台 GMV / 退货率 / 紧急任务）
```

## 场景 2：设计师马萍蔓

```
马萍蔓 → 飞书群: "DRS-0429-FL 这款想配个外套"
NLU 识别: skill=product-matching, params={product_id: "DRS-0429-FL"}, confidence=0.95
触发: product-matching-demo.ps1 --product-id DRS-0429-FL
回复: 5 套搭配建议卡片
```

## 场景 3：工厂主管申丽媛（移动端）

```
申丽媛 → 飞书群: "今天的紧急任务都有啥"
NLU 识别: skill=task-lifecycle, params={priority: "P0"}, confidence=0.88
触发: task-tracker.ps1 -PriorityFilter P0
回复: 紧急任务列表卡片
```

## 场景 4：主播小马

```
小马 → 飞书群: "晚上 8 点直播该带啥重点款"
NLU 识别: skill=live-streaming + product-matching
组合调用：先查 24 表本周计划款 → 给搭配建议
回复: 直播带款清单
```

## 场景 5：客服小红

```
小红 → 飞书群: "客户赵姐昨天的退货咋处理"
NLU 识别: skill=feedback-returns, params={customer: "赵姐"}, confidence=0.90
触发: 查 11_退货反馈表
回复: 赵姐退货详情 + 处理建议
```

## 场景 6：完全不懂 IT 的家人

```
老板娘老公 → "店里今天赚了多少"
NLU 识别: skill=profit-analysis, confidence=0.85
触发: profit-analysis.ps1 --period today
回复: 今日利润简报
```

## 场景 7：新员工小张（首次用）

```
小张 → "你能干啥"
NLU 识别: skill=null, confidence=0.30
fallback_message: "我能帮你：
  • 查今日销售（说 '今天卖得怎么样'）
  • 看任务进度（说 '看下任务'）
  • 产品搭配（说 'DRS-XXX 配什么'）
  • 拆视频脚本（说 '拆这个抖音 [URL]'）
  • 问老板娘的 AI 分身（说 '问老板这事咋办'）
  ..."
```

## 场景 8：模糊询问

```
员工 → "马萍蔓今天忙啥"
NLU 识别: skill=task-lifecycle, params={owner: "马萍蔓"}, confidence=0.78
触发: task-tracker.ps1 -Owner 马萍蔓
回复: 马萍蔓今日任务列表
```

## 场景 9：直接贴 URL

```
员工 → "https://v.douyin.com/_wC6QT4SkQE/"
NLU 识别: skill=blogger-monitor, params={url: "https://v.douyin.com/_wC6QT4SkQE/"}, confidence=0.92
触发: parse-video-script.py --url ...
回复: 视频拆解结果（30-60 秒后）
```

## 场景 10：跨 skill 复合操作

```
员工 → "DRS-0501 是新款，要不要做"
NLU 识别: 复合意图：
  primary: launch-decision
  secondary: boss-clone-aily（让老板分身复审）
触发: launch-decision.ps1 --product-id DRS-0501 --review-by-boss-clone
回复: 4 维信号 + 老板分身复审建议
```
