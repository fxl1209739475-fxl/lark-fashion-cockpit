---
name: lark-fashion-cockpit-lingo-glossary
version: 1.0.0
description: "把女装运营术语沉淀到飞书词典 Lingo —— DRS 编码规则、款式术语、客户投诉等级、工厂代号黑名单。员工在文档/聊天里 hover 词条自动看解释。配套 Wiki（长文档）使用。当用户说「沉淀术语」「DRS 编码什么意思」「行业词典」时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli api POST /open-apis/lingo/v1/entities"
---

# 飞书词典 Lingo · 女装运营术语库

> **🎯 痛点：** 新员工进店三天问"DRS 是什么意思"五次。客服碰到"显瘦"「泡泡袖」「A 字」一类术语没标准释义。沉淀到飞书词典，全员 hover 一下就懂。

> **载体：** 飞书词典 Lingo
> **配套：** 跟 Wiki 知识库（长文档手册）一起用 — 词典管短解释，Wiki 管成体系手册
> **入口：** 飞书任意文档 / 群聊里输入词典术语 → 自动浮现解释

---

## 一、为什么用 Lingo 而不是 Wiki

| 维度 | Wiki 知识库 | Lingo 词典 |
|---|---|---|
| 存储单元 | 一篇文档（几千字）| 一条词条（几句话）|
| 触发方式 | 主动打开翻 | **被动**：hover 一下自动浮现 |
| 谁建 | 管理员主导 | **全员共建**（任何人都可加） |
| 类比 | 公司内部手册 | **Wikipedia 短词条** |

**两者配套：** 词典短释义 + Wiki 详细手册。词条里挂 Wiki 链接做下钻。

---

## 二、女装店推荐沉淀的术语（首批 50 条）

### A. 产品编码规则
- DRS-XXXX-FL: Dress 连衣裙编码格式
- KNT-XXXX-XX: Knit 针织
- BLK-XXXX-XX: Blouse 衬衫
- SKT-XXXX-XX: Skirt 半身裙
- JKT-XXXX-XX: Jacket 外套
- 后两位字母 = 颜色代码（FL=花色，CD=驼色，BG=米色 ...）

### B. 款式术语（带视觉解释）
- A 字裙 / 直筒裙 / 鱼尾裙
- 法式 / 韩系 / 复古
- 阔腿 / 直筒 / 烟管
- 高腰 / 中腰 / 低腰
- 显瘦标准 / 显高标准 / 显白色

### C. 客户投诉等级
- L1: 一般咨询（24h 回复）
- L2: 退换货（4h 回复）
- L3: 投诉（1h 回复 + 老板娘介入）
- L4: 平台仲裁 / 媒体曝光（立即介入）

### D. 工厂代号
- ZC = 浙江工厂 A（合作 5 年，质量稳）
- GS = 广州工厂 B（版型新颖，交期慢一周）
- ⚠ HF = 广东工厂 C（曾跑路，已拉黑）

### E. 内部黑话
- "压不住了" → 库存清仓信号
- "all-in" → 大单押注
- "翻车" → 直播 / 营销失败
- "卷王" → 同行打价格战的形容

---

## 三、前置条件

```bash
# 飞书后台开通 Lingo 应用
# 申请权限：
# - lingo:entity:read / write （读写词条）
# - lingo:repo:read （读词库列表）
```

---

## 四、典型 API 调用

```bash
# 4a. 列已有词库
lark-cli api GET /open-apis/lingo/v1/repos --jq '.data.repos[] | {id, name}'

# 4b. 创建词条（免审版 — 直接进库）
lark-cli api POST /open-apis/lingo/v1/entities \
  --data '{
    "main_keys": [{"key": "DRS-0429-FL", "display_status": {"allow_highlight": true}}],
    "aliases": [{"key": "0429 法式连衣裙"}],
    "description": "2026 春季法式碎花连衣裙。版型: A 字。颜色: 奶茶白。面料: 醋酸缎面。客单价: ¥299",
    "related_meta": {
      "docs": [{"title": "上新企划文档", "url": "https://my.feishu.cn/wiki/xxx"}],
      "tables": [{"table_id": "tblrKzymnPPQ98ZX", "name": "01_产品库"}]
    },
    "outer_info": {"provider": "lark-fashion-cockpit", "outer_id": "DRS-0429-FL"}
  }'

# 4c. 模糊搜词条
lark-cli api POST /open-apis/lingo/v1/entities/search \
  --data '{"query": "法式连衣裙"}' \
  --jq '.data.entities[]'

# 4d. 词条高亮（识别一段文字里的所有词条）
lark-cli api POST /open-apis/lingo/v1/entities/highlight \
  --data '{"text": "DRS-0429 这款客单价高，工厂 ZC 的版要好一点"}' \
  --jq '.data.phrases'
# → 自动识别"DRS-0429"和"工厂 ZC"两个词条
```

---

## 五、批量导入脚本

`scripts/seed-fashion-glossary.py` 一次性灌入 50 条术语（见同级目录）。

```python
# 灌入女装行业术语库（50+ 条）
GLOSSARY = [
    {"key": "DRS-0429-FL", "desc": "...", "category": "产品编码"},
    {"key": "压不住了", "desc": "库存超过 60 天没动销，需清仓", "category": "内部黑话"},
    {"key": "all-in", "desc": "把可用预算全部押注一款（高风险）", "category": "内部黑话"},
    {"key": "ZC 工厂", "desc": "浙江合作 5 年的稳供应商", "category": "工厂代号"},
    {"key": "HF 工厂", "desc": "⚠ 已拉黑（曾跑路）", "category": "工厂黑名单"},
    # ... 50+ 条
]
for term in GLOSSARY:
    lark_api_post("/open-apis/lingo/v1/entities", data=build_entity(term))
```

---

## 六、与其他 skill 联动

- **boss-clone-aily（老板分身）**：分身回答时引用词典释义（"老板娘说不能 all-in，意思是..."）
- **knowledge-base / wiki**：每个词条挂对应 Wiki 长文档链接做下钻
- **task-collaboration**：任务标题/描述里的术语自动高亮帮新员工理解
- **competitor-monitor**：监控视频文案里的同行术语自动收集

---

## 七、典型对话示例

```
新员工 在飞书文档里写："这季 DRS-0429 的退货率高达 22%，工厂 HF 给的版有问题"
                               ↓ hover ↓
          [DRS-0429: 法式碎花连衣裙...]   [HF 工厂: ⚠ 已拉黑（曾跑路）]
新员工：原来如此，我去找老板娘问问换工厂
```

学习成本 = 0。术语自动浮现就是最强培训。
