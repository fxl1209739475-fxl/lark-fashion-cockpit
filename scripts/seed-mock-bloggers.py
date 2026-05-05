"""一次性灌入 10 条 mock 女装博主视频数据到 27_对标博主视频监控 表

复刻 douyin-monitor AI 博主监控的字段结构 + 加上"口播文案"。
数据是 mock 但比例符合女装赛道实际（爆款 / 普通 / 弱视频混合）。
"""

import subprocess, json, os
from datetime import datetime, timedelta

BASE = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
TABLE = "tblPDTGpUiJxZwHA"
TMP = r"C:\Users\冯兴龙\AppData\Local\Temp"
LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"

now = datetime.now()
ms = lambda d: int(d.timestamp() * 1000)

# 10 条 mock：（博主, 粉丝, 标题, 发布距今天数, 点赞, 评论, 收藏, 分享, AI 评分, 推荐角度, 口播文案）
RAW = [
  # 爆款 1: 高赞粉比 + 高收藏率（典型穿搭教学）
  ("程程姐_穿搭教学", 850000,
   "150 显高显瘦秘籍 ｜ 衬衫塞进高腰裤的 3 种正确方式",
   1, 425000, 8500, 56000, 12000, 9, "教学型痛点解决",
   "嗨大家好我是程程姐。今天教你们三招衬衫塞进高腰裤的正确方式，姐妹们你们是不是经常觉得衬衫塞进去鼓鼓的不好看？我跟你们说有三个秘诀。"
   "第一个，叫法式半塞，只塞前面三分之一的衣摆，后面自然垂下来，这样既能拉高腰线又显得很慵懒不刻意。"
   "第二个叫做正面 V 字塞，把衬衫前摆往里折一下再塞进去，腰部会形成一个 V 型，超级显瘦。"
   "第三个法式蓬松塞，把衬衫塞进去之后呢用手往外拉一点点，让腰线那里有一点点蓬起来的感觉，这样就特别有 INS 那种法式高级感。"
   "记住啊姐妹们，永远不要把衬衫整个均匀塞进去，那个最显矮显胖了。学会了的话点赞收藏哦，下期教你们怎么挑高腰裤。"),

  # 爆款 2: 高分享率（小个子穿搭）
  ("Sandy小苹果", 320000,
   "155 微胖也能穿出大长腿的 5 个衣橱必备款",
   2, 186000, 5200, 28000, 22000, 9, "细分人群（小个子+微胖）",
   "我是 Sandy，今天分享 155 微胖姐妹必入的 5 件单品。第一件高腰阔腿西裤，必须是高腰，腰线越高越显腿长，西裤要选垂感面料，廉价感的不要。"
   "第二件法式娃娃领衬衫，娃娃领能视觉缩小肩宽和脸，搭配高腰裙或高腰裤都好看。"
   "第三件 V 领针织背心，V 领开得越深越显脸小，针织面料要选挺括一点的，软塌塌的不行。"
   "第四件 A 字型半身裙，长度过膝 5 公分最显腿长，裙摆有点弧度但不要太大。"
   "第五件短款外套，长度刚好到腰节，把腰线整个往上拉，配阔腿裤就是 1.7 米的视觉效果。"
   "这五件衣服姐妹们我已经穿了一年多了，复购率最高的就是这五件。"),

  # 高互动型（大码）
  ("大码姑娘子涵", 180000,
   "120 斤穿出 90 斤的视觉，真不是骗你",
   3, 88000, 6800, 9200, 1800, 8, "大码人群解决方案",
   "今天教大家 120 斤怎么穿成 90 斤的视觉效果。第一关键就是不要选紧身的衣服。我以前一直觉得紧身才显瘦，后来才发现完全反着。紧身的把所有肉都勒出来，反而显胖。"
   "应该选什么呢？版型要稍微松一点但不能松垮，叫做有型不显胖。比如直筒西装外套，肩线要正好不要太宽。还有就是利用 V 领、A 字、收腰这些视觉技巧，能瘦 10 斤的视觉效果。"),

  # 普通：法式风
  ("法式衣橱_可可", 95000,
   "Sandro 法式新款怎么搭最显气质",
   4, 12500, 580, 1200, 320, 7, "品牌测评+穿搭",
   "今天测评一下 Sandro 这件新款法式针织开衫。米白色，泡泡袖，前面是排扣设计，整体是那种很慵懒法式的感觉。我的搭配建议是配高腰直筒牛仔裤，这种穿法最日常也最显气质。"
   "面料是 50% 羊毛 50% 醋酸混纺，手感不错，价格 1290，性价比一般，但是版型很到位。"),

  # 普通：通勤
  ("通勤穿搭日记_Jenna", 240000,
   "30+ 通勤穿搭｜不踩雷的 3 套搭配",
   2, 32000, 1200, 4500, 800, 7, "细分场景（30+通勤）",
   "30+ 姐妹通勤穿搭，记住不要选太年轻的款式。第一套白色衬衫 + 黑色直筒西裤，搭配尖头细高跟，这是通勤的安全牌但永远不会出错。"
   "第二套米色针织衫 + 卡其色西装裙，温柔又不失专业感。"
   "第三套休闲点的，oversize 风衣 + 直筒牛仔裤，周五穿这套，舒服但不随便。"),

  # 普通：复古风
  ("复古阿姨_Vintage", 65000,
   "复古油画风裙子怎么穿不土气",
   5, 8200, 290, 980, 180, 7, "风格教学",
   "复古油画风很多人觉得难穿不日常，其实有诀窍。第一是颜色不要选得太鲜艳，墨绿、酒红、深咖啡这种就很高级。"
   "第二是配饰一定要现代，比如金属耳环、小方包，不要再配复古元素了，会全身用力。"
   "第三是发型干净一点，低马尾或丸子头都好看。"),

  # 普通：韩系
  ("韩系少女Lisa", 410000,
   "韩系冬日穿搭｜首尔街拍同款",
   1, 78000, 2100, 3800, 950, 7, "风格趋势",
   "首尔最近流行的几个韩系冬日穿搭。第一种是棒球帽 + 大衣 + 牛仔裤的休闲款。第二种是针织套装 + 长款大衣的温柔款。第三种是衬衫 + 西装马甲 + 西裤的学院风。"
   "韩系的精髓是 CLEAN GIRL，配色干净，整体不要超过 3 个颜色，妆容也偏自然。"),

  # 设计师款（无口播 — 纯穿搭，注意：文案空）
  ("设计师女装铺_蜜糖", 28000,
   "S/S 26 新品先睹为快｜设计师小众原创",
   3, 5600, 145, 1800, 220, 8, "原创设计欣赏",
   ""),  # 无口播 — 纯穿搭视频

  # 高分享但低粉
  ("五五分博主小马", 18000,
   "165/55kg 高级感穿搭逻辑｜被夸了一整年的搭配",
   1, 9800, 320, 2100, 1500, 8, "微胖高级感",
   "165/55 这个身材怎么穿出高级感？核心一个字：竖。所有衣服选竖向线条，垂坠感的西裤、长款风衣、高腰长裙，都能视觉上把人拉长。"
   "第二个秘诀就是配色要克制。我整个衣橱 80% 是黑白驼灰这四个色，每天搭配花的时间不超过 1 分钟，但出门永远被夸高级。"),

  # 弱视频（数据不行，会进"待评估"）
  ("婆婆我教你穿", 8500,
   "妈妈辈也能穿的法式优雅",
   6, 1200, 35, 180, 28, 5, "中老年市场",
   "今天教妈妈辈怎么穿出法式优雅。其实很简单，就是把那种花花绿绿的换成纯色，把肥大的换成有线条感的。妈妈试了一下，整个人气质完全不一样。"),
]


def calc_metrics(likes, comments, collects, shares, fans, ai_score):
    """复刻 analyzer/scoring.py 的计算 + 4 路筛选"""
    zan_fen = round(likes / fans, 4) if fans else 0
    inter = round((likes + comments + shares) / fans, 4) if fans else 0
    share_rate = round(shares / likes, 4) if likes else 0
    collect_rate = round(collects / likes, 4) if likes else 0
    comment_like = round(comments / likes, 4) if likes else 0

    score = 0
    if zan_fen >= 0.5: score += 5
    elif zan_fen >= 0.2: score += 3
    elif zan_fen >= 0.05: score += 1
    if share_rate >= 0.1: score += 2
    elif share_rate >= 0.03: score += 1
    if collect_rate >= 0.1: score += 2
    elif collect_rate >= 0.05: score += 1
    if comment_like >= 0.05: score += 1

    # 4 路筛选
    p1 = ai_score >= 7
    p2 = collect_rate >= 0.10
    p3 = comment_like >= 0.08
    p4 = zan_fen >= 0.4
    selected = p1 or p2 or p3 or p4

    return {
        "赞粉比": zan_fen, "互动率": inter, "分享率": share_rate,
        "收藏率": collect_rate, "评赞比": comment_like, "爆款指数": score,
        "状态": "已选中" if selected else "待评估",
    }


FIELD_ORDER = ["博主名称", "粉丝数", "视频标题", "发布日期", "视频链接",
               "点赞数", "评论数", "收藏数", "分享数",
               "赞粉比", "互动率", "分享率", "收藏率", "评赞比",
               "爆款指数", "AI 评分", "推荐角度", "口播文案", "状态"]

rows = []
for i, (博主, 粉丝, 标题, 距今, 点赞, 评论, 收藏, 分享, ai_s, 角度, 文案) in enumerate(RAW, 1):
    pub = now - timedelta(days=距今)
    m = calc_metrics(点赞, 评论, 收藏, 分享, 粉丝, ai_s)
    # mock 视频链接
    url = f"https://www.douyin.com/video/74{(8000000000 + i * 137):010d}"
    rows.append([
        博主, 粉丝, 标题, ms(pub), url,
        点赞, 评论, 收藏, 分享,
        m["赞粉比"], m["互动率"], m["分享率"], m["收藏率"], m["评赞比"],
        m["爆款指数"], ai_s, 角度, 文案, m["状态"],
    ])

payload = {"fields": FIELD_ORDER, "rows": rows}
p = os.path.join(TMP, "bloggers-batch.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

result = subprocess.run(
    [LARK_CLI, "base", "+record-batch-create",
     "--base-token", BASE, "--table-id", TABLE,
     "--json", "@./bloggers-batch.json"],
    cwd=TMP, capture_output=True, text=True, encoding="utf-8", errors="replace",
)
if result.returncode == 0:
    print(f"✓ 灌入 {len(rows)} 条 mock 数据")
    selected = sum(1 for r in rows if r[-1] == "已选中")
    print(f"  状态分布：已选中 {selected} / 待评估 {len(rows)-selected}")
else:
    print(f"✗ rc={result.returncode}")
    print(f"  stderr: {result.stderr[:500]}")
