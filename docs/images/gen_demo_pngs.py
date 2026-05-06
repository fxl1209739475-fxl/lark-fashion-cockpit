"""为 8 个核心 skill 生成"伪截图"演示图（聊天对话 + 飞书卡片返回的 mockup）

每张图 1200x720，模拟"用户输入 → AI 路由 → skill 执行 → 飞书卡片回执"的全链路
"""

import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 720
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def make_canvas():
    img = Image.new("RGB", (W, H), "#f1f5f9")
    return img, ImageDraw.Draw(img)


def round_rect(d, x, y, w, h, r, fill, outline=None, outline_w=0):
    d.rounded_rectangle([(x, y), (x+w, y+h)], r, fill=fill, outline=outline, width=outline_w)


def text_wrap(d, x, y, max_w, txt, f, fill, line_h=None):
    """简单的文字换行"""
    line_h = line_h or (f.size + 6)
    words = list(txt)
    line = ""
    cy = y
    for ch in words:
        test = line + ch
        bbox = d.textbbox((0,0), test, font=f)
        if bbox[2] - bbox[0] > max_w:
            d.text((x, cy), line, font=f, fill=fill)
            line = ch
            cy += line_h
        else:
            line = test
    if line:
        d.text((x, cy), line, font=f, fill=fill)
        cy += line_h
    return cy


def draw_header(d, title, subtitle):
    """顶部标题条"""
    round_rect(d, 0, 0, W, 70, 0, "#4f46e5")
    d.text((30, 16), title, font=font(20, True), fill="#ffffff")
    d.text((30, 44), subtitle, font=font(12), fill="#c7d2fe")
    # 浏览器假地址栏
    round_rect(d, W-330, 16, 310, 36, 18, "#3730a3")
    d.text((W-310, 23), "🔒 http://localhost:8080  💬", font=font(13), fill="#e0e7ff")


def chat_bubble_user(d, x, y, text, max_w=600):
    """用户消息气泡（紫色右侧）"""
    f = font(14)
    bbox = d.textbbox((0,0), text, font=f)
    tw = min(bbox[2] - bbox[0] + 24, max_w)
    th = bbox[3] - bbox[1] + 18
    bx = x + 600 - tw - 60
    round_rect(d, bx, y, tw, th, 12, "#4f46e5")
    d.text((bx + 12, y + 8), text, font=f, fill="#ffffff")
    return y + th + 10


def chat_bubble_assistant(d, x, y, text, max_w=600):
    """AI 回复气泡（白色左侧）"""
    f = font(14)
    # 多行处理
    lines = text.split("\n")
    th_total = 18
    for line in lines:
        bbox = d.textbbox((0,0), line, font=f)
        th_total += max(bbox[3] - bbox[1] + 6, 22)
    tw = max_w
    round_rect(d, x, y, tw, th_total, 12, "#ffffff", "#e5e7eb", 1)
    cy = y + 10
    for line in lines:
        d.text((x + 14, cy), line, font=f, fill="#1e293b")
        cy += 22
    return y + th_total + 10


def chat_skill_event(d, x, y, text, max_w=600):
    """灰色系统事件（🧠 已识别 / ⚙ 执行 等）"""
    f = font(11)
    bbox = d.textbbox((0,0), text, font=f)
    tw = bbox[2] - bbox[0] + 16
    th = bbox[3] - bbox[1] + 8
    round_rect(d, x, y, max_w, th, 4, "#eef2ff")
    d.text((x + 12, y + 4), text, font=f, fill="#6366f1")
    return y + th + 4


def lark_card(d, x, y, w, h, header_text, header_color, body_blocks):
    """飞书卡片样式"""
    round_rect(d, x, y, w, h, 8, "#ffffff", "#e5e7eb", 1)
    # header
    round_rect(d, x, y, w, 38, 8, header_color)
    d.text((x + 16, y + 11), header_text, font=font(14, True), fill="#ffffff")
    # body
    cy = y + 50
    for kind, text in body_blocks:
        if kind == "text":
            cy = text_wrap(d, x + 16, cy, w - 32, text, font(13), "#1e293b") + 4
        elif kind == "kv":
            d.text((x + 16, cy), text, font=font(12), fill="#475569")
            cy += 22
        elif kind == "alert":
            round_rect(d, x + 16, cy, w - 32, 36, 6, "#fee2e2")
            d.text((x + 28, cy + 9), text, font=font(13, True), fill="#b91c1c")
            cy += 44


# ============================================================
# 演示图们
# ============================================================

def gen_omnitask_bridge():
    img, d = make_canvas()
    draw_header(d, "🚀 omnitask-bridge — 全员 ChatOps 驾驶舱",
                "主驾驶舱：浏览器打开 → 跟系统聊天 → AI 翻译 → 调飞书 CLI 全套能力")

    # 左侧 mock 驾驶舱缩略图
    round_rect(d, 30, 100, 510, 580, 8, "#ffffff", "#e5e7eb", 1)
    d.text((50, 120), "📊 经营总览（左侧导航 + 数据 widget）", font=font(13, True), fill="#1e293b")

    # 假 widget 卡片
    widgets = [
        (50, 160, 220, 90, "今日销售", "¥45,820", "+12% vs 昨日", "#0ea5e9"),
        (290, 160, 220, 90, "库存预警", "1 红 / 3 黄", "SKT-0328-A 紧急", "#ef4444"),
        (50, 270, 220, 90, "本周上新", "6 / 10", "4 个延期", "#f59e0b"),
        (290, 270, 220, 90, "本月目标", "78%", "差 ¥120k", "#10b981"),
    ]
    for x, y, w, h, title, big, sub, color in widgets:
        round_rect(d, x, y, w, h, 8, "#f8fafc", "#e2e8f0", 1)
        d.text((x + 14, y + 12), title, font=font(11), fill="#64748b")
        d.text((x + 14, y + 32), big, font=font(20, True), fill=color)
        d.text((x + 14, y + 62), sub, font=font(11), fill="#94a3b8")

    # 假图表
    round_rect(d, 50, 380, 460, 250, 8, "#f8fafc", "#e2e8f0", 1)
    d.text((70, 400), "📈 4 平台销售趋势 (近 7 天)", font=font(12, True), fill="#1e293b")
    # 假折线
    points_x = [80, 140, 200, 260, 320, 380, 440]
    for color, base_y in [("#9c2f45", 540), ("#0f766e", 555), ("#c47a1d", 570), ("#6b5b95", 585)]:
        prev = None
        for i, x in enumerate(points_x):
            y = base_y - (i * 8) - (i % 2) * 5
            if prev:
                d.line([prev, (x, y)], fill=color, width=2)
            d.ellipse([(x-3, y-3), (x+3, y+3)], fill=color)
            prev = (x, y)

    # 右侧聊天浮窗
    round_rect(d, 580, 100, 590, 580, 12, "#ffffff", "#a5b4fc", 2)
    round_rect(d, 580, 100, 590, 50, 12, "#4f46e5")
    d.text((600, 116), "💬 跟 cockpit 对话  · 在线", font=font(13, True), fill="#ffffff")
    d.text((1130, 116), "收起", font=font(11), fill="#c7d2fe")

    cy = 170
    cy = chat_bubble_user(d, 580, cy, "今天销售如何？")
    cy = chat_skill_event(d, 600, cy, "🧠 已识别 → query.sales_today (关键词)")
    cy = chat_skill_event(d, 600, cy, "⚙ 拉飞书 02_4平台销售 表...")
    cy = chat_bubble_assistant(d, 600, cy,
        "📊 今日销售：¥45,820 · 87 单\n"
        "• 淘宝 ¥21k（46%）⭐ 利润王\n"
        "• 抖音 ¥18k（45% 单量但客单低）\n"
        "• 小红书 ¥4.5k\n"
        "• 视频号 ¥2k\n"
        "✨ 比昨日 ↑ 12%，达标")
    cy = chat_bubble_user(d, 580, cy, "再看下库存预警")
    cy = chat_skill_event(d, 600, cy, "🧠 → query.stock_alerts")
    cy = chat_bubble_assistant(d, 600, cy,
        "🚨 1 紧急 / 3 中度\n"
        "• SKT-0328-A 全 SKU 5/30 建议补 350")

    img.save(os.path.join(OUT_DIR, "demo-omnitask-bridge.png"), "PNG", optimize=True)


def gen_wechat_monitor():
    img, d = make_canvas()
    draw_header(d, "📱 wechat-monitor — 微信群速览",
                "截图 PC 微信主窗口 → DOUBAO 视觉 → 摘要紧急消息 → 飞书卡片")

    # 左侧：模拟微信主窗口截图
    round_rect(d, 30, 100, 460, 580, 8, "#fafafa", "#e5e7eb", 1)
    d.text((50, 116), "📷 微信主窗口截图（被脚本捕获）", font=font(11), fill="#64748b")

    # 群列表
    groups = [
        ("文件传输助手", "今天 14:30", "图片", 0),
        ("ZC 工厂沟通群", "今天 11:20", "DRS-0429 雪纺面料卡在染色...", 12),
        ("dontbesilent 哥哥", "周三 17:30", "[图片消息]", 0),
        ("终极目标实现群", "周三 23:44", "@你 我们运营标签流量便宜", 5),
        ("MM", "周一 16:03", "宝宝你饿吗，家里还有麻婆豆腐", 0),
        ("营销-淘宝", "周一 09:00", "5月活动报名截止...", 0),
    ]
    cy = 150
    for name, time, preview, unread in groups:
        round_rect(d, 50, cy, 420, 70, 4, "#ffffff" if unread > 0 else "#f8fafc", "#e2e8f0", 1)
        d.ellipse([(60, cy + 12), (104, cy + 56)], fill="#dbeafe")
        d.text((116, cy + 12), name, font=font(13, True), fill="#1e293b")
        d.text((360, cy + 12), time, font=font(10), fill="#94a3b8")
        d.text((116, cy + 36), preview[:30], font=font(11), fill="#64748b")
        if unread:
            round_rect(d, 380, cy + 30, 70, 22, 11, "#ef4444")
            d.text((400, cy + 33), str(unread), font=font(12, True), fill="#ffffff")
        cy += 80

    # 右侧：飞书卡片
    lark_card(d, 540, 110, 630, 570, "📱 微信群速览  ·  今天 09:32",
              "#ef4444",
              [
                  ("text", "📊 8 个未读群 · 🚨 2 条紧急 · 🎭 工作密集"),
                  ("text", "—————————"),
                  ("text", "🚨 紧急:"),
                  ("alert", "ZC 工厂群：DRS-0429 雪纺卡染色，预计延 2 天"),
                  ("alert", "终极目标群：@你 标签流量很便宜（值得关注）"),
                  ("text", ""),
                  ("text", "📋 关键信息:"),
                  ("kv", "• 朱健豪发了 v2 直播脚本待审"),
                  ("kv", "• MM 周一 16:03 没回复（私事）"),
                  ("kv", "• 5 月营销活动报名将截止（淘宝群）"),
                  ("text", ""),
                  ("text", "💡 建议你处理:"),
                  ("kv", "1. 先回 ZC 工厂确认延期方案"),
                  ("kv", "2. 看朱健豪脚本 V2"),
              ])

    img.save(os.path.join(OUT_DIR, "demo-wechat-monitor.png"), "PNG", optimize=True)


def gen_morning_report():
    img, d = make_canvas()
    draw_header(d, "🌅 morning-report — 早 8:00 跨渠道情报早报",
                "auto-scheduler 触发 → 并发拉 飞书+企微+个微+销售+库存+任务 → 一张早报卡")

    # 中央卡片放大
    lark_card(d, 100, 110, 1000, 580, "🌅 老板娘的早报  ·  2026-05-06 周三",
              "#10b981",
              [
                  ("text", "📊 昨日（5/5）经营快讯"),
                  ("text", "—————————"),
                  ("kv", "• 销售 ¥48,920（达标 ✓ 较前日 +8%）"),
                  ("kv", "• 抖音 ¥22k 高于均值 / 淘宝 ¥18k 利润王"),
                  ("kv", "• 库存 1 红 SKT-0328-A 已补 350 件"),
                  ("kv", "• 退货率 4.8%（低于行业 6%）"),
                  ("text", ""),
                  ("text", "📅 今天（5/6）值得关注"),
                  ("text", "—————————"),
                  ("kv", "• 你有 3 条飞书 @消息（朱健豪 + 马萍蔓 + 申丽媛）"),
                  ("kv", "• 你有 2 个会议（10:00 设计评审 / 14:00 工厂对接）"),
                  ("kv", "• 你有 5 条未完成任务（其中 1 条 deadline 今天）"),
                  ("text", ""),
                  ("text", "🚨 跨渠道紧急（飞书 + 企微 + 个微）"),
                  ("text", "—————————"),
                  ("alert", "ZC 工厂群（个微）：DRS-0429 雪纺卡染色，需老板娘拍板"),
                  ("alert", "客户 X（企微）：48h 窗口剩 6h，未回复将丢失主动渠道"),
                  ("text", ""),
                  ("text", "💡 今日重点（AI 推荐）："),
                  ("kv", "1. 先处理 ZC 工厂的延期方案（10:00 评审会前）"),
                  ("kv", "2. 14:00 前回复客户 X，保持企微窗口"),
                  ("kv", "3. 看下 KNT-0402 退货率到 5.5% 触发了警戒"),
              ])

    img.save(os.path.join(OUT_DIR, "demo-morning-report.png"), "PNG", optimize=True)


def gen_product_library():
    img, d = make_canvas()
    draw_header(d, "📦 product-library — 服装电商产品库",
                "飞书多维表格 27 字段 SKU schema：颜色矩阵 + 尺码做货单 + 4 平台分配")

    # 模拟 SKU 详情
    round_rect(d, 30, 100, 1140, 580, 8, "#ffffff", "#e5e7eb", 1)
    round_rect(d, 30, 100, 1140, 50, 8, "#1e293b")
    d.text((50, 116), "01_产品库 → DRS-0429-FL 法式收腰碎花连衣裙", font=font(15, True), fill="#ffffff")
    d.text((1000, 120), "状态：在售 ⭐", font=font(12), fill="#34d399")

    # 基本信息
    cy = 170
    info = [
        ("SKU 编号", "DRS-0429-FL"),
        ("品类 / 风格", "连衣裙 / 法式约会"),
        ("吊牌价 / 实卖", "¥299 / ¥259"),
        ("4 平台分配", "淘宝 + 抖音 + 小红书"),
        ("状态", "上架"),
    ]
    for k, v in info:
        d.text((60, cy), k, font=font(12), fill="#64748b")
        d.text((220, cy), v, font=font(13, True), fill="#1e293b")
        cy += 28

    # 颜色矩阵
    round_rect(d, 540, 170, 620, 200, 8, "#f8fafc", "#e5e7eb", 1)
    d.text((560, 184), "🎨 颜色 × 尺码 做货单", font=font(13, True), fill="#1e293b")
    headers = ["颜色", "XS", "S", "M", "L", "XL", "做货", "实销"]
    for i, h in enumerate(headers):
        d.text((560 + i * 70, 215), h, font=font(11, True), fill="#475569")
    rows = [
        ("莓果红", "60", "120", "180", "110", "50", "520", "498"),
        ("奶油白", "40", "90", "130", "80", "35", "375", "289"),
    ]
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            d.text((560 + ci * 70, 240 + ri * 28), val, font=font(11), fill="#0f172a")

    # 售罄率 / 退货率
    round_rect(d, 540, 390, 620, 80, 8, "#fef3c7", "#fcd34d", 1)
    d.text((560, 404), "📊 关键指标", font=font(12, True), fill="#92400e")
    d.text((560, 428), "售罄率 87.9%  ✓", font=font(13, True), fill="#10b981")
    d.text((760, 428), "退货率 3.2%  ✓", font=font(13, True), fill="#10b981")
    d.text((960, 428), "可售天数 14 天", font=font(13, True), fill="#1e293b")
    d.text((560, 450), "（行业均值售罄 65% / 退货 6.5%，本款两项均优）", font=font(10), fill="#92400e")

    # 底部 AI 分析
    round_rect(d, 60, 510, 1080, 150, 8, "#eef2ff", "#a5b4fc", 1)
    d.text((80, 526), "🤖 AI 产品分析（基于实时飞书数据，DEEPSEEK V4）", font=font(13, True), fill="#3730a3")
    d.text((80, 552), "用户问：找出售罄率低于 50% 的产品，按春夏秋冬分类", font=font(12), fill="#475569")
    d.text((80, 580), "【结论】3 个 SKU 命中：NO.008（春夏，40%）+ NO.006/007（开发中）", font=font(12), fill="#1e293b")
    d.text((80, 605), "【建议】NO.008 立即促销 + NO.006/007 加快开发提前预售", font=font(12), fill="#1e293b")
    d.text((80, 630), "【依据】见上方颜色矩阵的实销数据，本款是参考优秀样本", font=font(11), fill="#64748b")

    img.save(os.path.join(OUT_DIR, "demo-product-library.png"), "PNG", optimize=True)


def gen_blogger_monitor():
    img, d = make_canvas()
    draw_header(d, "📺 blogger-monitor — 对标博主监控",
                "每天抓 48 个对标博主新视频 → DEEPSEEK 评分 → 飞书 Top N 推荐")

    # 左：博主列表
    round_rect(d, 30, 100, 460, 580, 8, "#ffffff", "#e5e7eb", 1)
    d.text((50, 120), "📋 27_对标博主视频监控  · 今日 12 条", font=font(13, True), fill="#1e293b")

    bloggers = [
        ("dontbesilent 哥哥", "DRS 同款穿搭", "187k", 92, "✓ 推荐二创"),
        ("时尚博主李姐", "春夏色系搭配", "92k", 88, "✓ 推荐二创"),
        ("法式风刘小姐", "复古约会风", "75k", 81, "✓ 推荐二创"),
        ("职场穿搭莉莉", "通勤西装裤", "54k", 75, "△ 中等"),
        ("可爱风茉茉", "甜系连衣裙", "120k", 65, "△ 风格不符"),
        ("奶茶妹妹", "校园感针织", "48k", 58, "✗ 跳过"),
    ]
    cy = 155
    for name, topic, likes, score, tag in bloggers:
        color = "#22c55e" if score >= 80 else ("#f59e0b" if score >= 70 else "#94a3b8")
        round_rect(d, 50, cy, 420, 75, 6, "#f8fafc", "#e5e7eb", 1)
        d.text((60, cy + 8), name, font=font(13, True), fill="#1e293b")
        d.text((60, cy + 30), topic, font=font(11), fill="#64748b")
        d.text((60, cy + 50), f"❤ {likes}", font=font(11), fill="#ef4444")
        round_rect(d, 360, cy + 8, 100, 26, 13, color)
        d.text((385, cy + 12), f"AI {score}", font=font(11, True), fill="#ffffff")
        d.text((360, cy + 50), tag, font=font(10), fill="#475569")
        cy += 85

    # 右：飞书卡片
    lark_card(d, 540, 110, 630, 580, "📺 今日博主爆款 Top 3  · 09:00 推送",
              "#f59e0b",
              [
                  ("text", "🏆 综合评分（女装关联 + 学习价值 + 二创可行性）"),
                  ("text", ""),
                  ("text", "1️⃣ dontbesilent 哥哥 — DRS 同款穿搭  AI 92"),
                  ("kv", "❤ 187k 👁 1.2M  发布 2h 前"),
                  ("kv", "亮点：法式收腰 × 莓果红，跟我们 DRS-0429 高度相似"),
                  ("kv", "建议：直接二创视觉模板 + 我们 SKU 替换"),
                  ("text", ""),
                  ("text", "2️⃣ 时尚博主李姐 — 春夏色系搭配  AI 88"),
                  ("kv", "❤ 92k  本月第 3 条爆款"),
                  ("kv", "亮点：色系搭配讲解，可借鉴博主话术结构"),
                  ("text", ""),
                  ("text", "3️⃣ 法式风刘小姐 — 复古约会风  AI 81"),
                  ("kv", "❤ 75k  风格契合 DRS 系列"),
                  ("text", ""),
                  ("text", "🤖 一键操作:"),
                  ("kv", "回 1 → 调 video-script-parser 自动拆解 #1"),
                  ("kv", "回 23 → 拆 #2 + #3"),
              ])

    img.save(os.path.join(OUT_DIR, "demo-blogger-monitor.png"), "PNG", optimize=True)


def gen_wxauto_supplier():
    img, d = make_canvas()
    draw_header(d, "📲 wxauto-supplier-bridge — 飞书指令通知供应商",
                "飞书一句话 → wxauto 控制 PC 微信 → 给固定供应商发消息（4 层风控）")

    # 左：聊天对话
    round_rect(d, 30, 100, 510, 580, 12, "#ffffff", "#e5e7eb", 1)
    round_rect(d, 30, 100, 510, 46, 12, "#4f46e5")
    d.text((50, 114), "💬 cockpit 聊天浮窗", font=font(13, True), fill="#ffffff")

    cy = 170
    cy = chat_bubble_user(d, 30, cy, "通知 ZC 工厂 DRS-0429 加急", max_w=460)
    cy = chat_skill_event(d, 50, cy, "🧠 → notify.supplier  conf=0.95", max_w=460)
    cy = chat_skill_event(d, 50, cy, "🛡 权限校验 (owner ✓ 白名单 ✓ 限速 ✓)", max_w=460)
    cy = chat_skill_event(d, 50, cy, "🔍 查 28_供应商档案 → ZC 工厂 → 浙江老张", max_w=460)
    cy = chat_skill_event(d, 50, cy, "⚙ wxauto 操作 PC 微信...", max_w=460)
    cy = chat_skill_event(d, 50, cy, "✓ 已发送", max_w=460)
    cy = chat_bubble_assistant(d, 50, cy,
        "✓ 已通知 ZC 工厂 浙江老张\n"
        "消息：「DRS-0429 雪纺面料能否加急到下周一？」\n"
        "📊 对方已读 · 18:32 · 等待回复\n"
        "📝 已写 logs/wxauto-audit.jsonl", max_w=460)

    # 右：模拟微信桌面端窗口
    round_rect(d, 580, 100, 590, 580, 8, "#fafafa", "#e2e8f0", 1)
    d.text((600, 116), "🖥 PC 微信桌面端（被自动操作）", font=font(11), fill="#64748b")

    # 模拟聊天窗口
    round_rect(d, 600, 145, 550, 50, 4, "#f3f4f6")
    d.ellipse([(620, 158), (660, 198)], fill="#dbeafe")
    d.text((675, 160), "浙江老张", font=font(13, True), fill="#1e293b")
    d.text((675, 178), "在线", font=font(10), fill="#22c55e")

    # 发出去的消息
    round_rect(d, 800, 220, 350, 50, 8, "#22c55e")
    d.text((815, 232), "(老板娘 cockpit 自动消息)", font=font(10), fill="#dcfce7")
    d.text((815, 248), "DRS-0429 雪纺面料能否加急到下周一？", font=font(12), fill="#ffffff")
    d.text((1090, 278), "已读  18:32", font=font(10), fill="#94a3b8")

    # 对方回复
    round_rect(d, 600, 300, 380, 50, 8, "#ffffff", "#e2e8f0", 1)
    d.text((615, 312), "好嘞，我看下排期，10 分钟回你", font=font(12), fill="#1e293b")
    d.text((615, 332), "18:33", font=font(10), fill="#94a3b8")

    # 风控提示
    round_rect(d, 600, 380, 550, 280, 8, "#fef3c7", "#fcd34d", 1)
    d.text((620, 396), "🛡 4 层风控（防风控封号）", font=font(13, True), fill="#92400e")
    d.text((620, 426), "1. 仅老板娘 owner 可触发（防员工冒用）", font=font(11), fill="#78350f")
    d.text((620, 450), "2. 白名单：仅 28 表 status=活跃 的供应商", font=font(11), fill="#78350f")
    d.text((620, 474), "3. 限速：≤ 5 条/分钟，≤ 50 条/天", font=font(11), fill="#78350f")
    d.text((620, 498), "4. 审计：每条记 logs/wxauto-audit.jsonl", font=font(11), fill="#78350f")
    d.text((620, 528), "✦ 消息加前缀 (老板娘 cockpit 自动消息)", font=font(11, True), fill="#78350f")
    d.text((620, 548), "  让对方知道是机器代发，不会困惑", font=font(11), fill="#78350f")
    d.text((620, 580), "实测：5 个核心供应商低频使用，", font=font(11), fill="#78350f")
    d.text((620, 600), "几乎不可能触发腾讯风控", font=font(11, True), fill="#92400e")

    img.save(os.path.join(OUT_DIR, "demo-wxauto-supplier.png"), "PNG", optimize=True)


def gen_stock_replenishment():
    img, d = make_canvas()
    draw_header(d, "📦 stock-replenishment — 库存预警自动报警",
                "auto-scheduler 每 30 分钟扫 03 表 → 紧急 SKU 飞书红色卡片 → 一键通知工厂")

    # 左：库存表
    round_rect(d, 30, 100, 510, 580, 8, "#ffffff", "#e5e7eb", 1)
    d.text((50, 120), "📋 03_库存预警 表（实时数据）", font=font(13, True), fill="#1e293b")

    # 表头
    cy = 155
    headers = ["SKU", "库存", "安全线", "建议补", "紧急度"]
    widths = [180, 70, 70, 70, 80]
    cx = 50
    for h, w in zip(headers, widths):
        d.text((cx, cy), h, font=font(11, True), fill="#475569")
        cx += w

    # 行
    rows = [
        ("SKT-0328-A 全 SKU", "5", "30", "350", "紧急", "#fee2e2", "#b91c1c"),
        ("PNT-0418-SU 炭黑 M", "35", "50", "200", "中", "#fef3c7", "#92400e"),
        ("KNT-0402-CD 焦糖 L", "28", "40", "150", "中", "#fef3c7", "#92400e"),
        ("SHT-0420-SP 海盐 S", "18", "30", "250", "中", "#fef3c7", "#92400e"),
        ("DRS-0429-FL 莓果 M", "180", "100", "0", "充足", "#dcfce7", "#166534"),
    ]
    cy += 24
    for sku, stock, safety, suggest, level, bg, fg in rows:
        round_rect(d, 50, cy, 460, 36, 4, bg, "#e2e8f0", 1)
        cx = 50
        for val, w in zip([sku, stock, safety, suggest], widths[:-1]):
            d.text((cx + 5, cy + 9), val, font=font(11), fill="#1e293b")
            cx += w
        round_rect(d, cx + 5, cy + 6, 70, 24, 12, fg)
        d.text((cx + 16, cy + 10), level, font=font(11, True), fill="#ffffff")
        cy += 42

    # 右：飞书报警卡片
    lark_card(d, 580, 110, 590, 570, "🚨 库存紧急预警  · 09:32 自动检测",
              "#dc2626",
              [
                  ("alert", "1 个 SKU 已断货风险（库存 < 安全线 30%）"),
                  ("text", ""),
                  ("text", "🔴 紧急（应立刻补货）"),
                  ("kv", "• SKT-0328-A 全 SKU"),
                  ("kv", "  库存 5 件 / 安全线 30 件"),
                  ("kv", "  建议补 350 件（淘宝 60% / 小红书 40%）"),
                  ("kv", "  关联款：05_06_07_08_09_10"),
                  ("text", ""),
                  ("text", "🟡 中度（建议关注）"),
                  ("kv", "• PNT-0418-SU 炭黑 M（35/50）"),
                  ("kv", "• KNT-0402-CD 焦糖 L（28/40）"),
                  ("kv", "• SHT-0420-SP 海盐 S（18/30）"),
                  ("text", ""),
                  ("text", "💡 一键操作"),
                  ("kv", "回 1 → 通知 ZC 工厂 SKT-0328-A 加急"),
                  ("kv", "回 234 → 通知所有面料商中度款"),
                  ("kv", "回 报告 → AI 给出补货优先级排序"),
              ])

    img.save(os.path.join(OUT_DIR, "demo-stock-replenishment.png"), "PNG", optimize=True)


def gen_launch_decision():
    img, d = make_canvas()
    draw_header(d, "🎯 launch-decision — AI 上新方案评分",
                "设计师上传 5 个候选方案 → AI 综合评分（成本+卖相+工艺+竞品对标）→ 推荐")

    # 5 个方案卡片
    plans = [
        (50,   "A 莓果红碎花连衣裙", 79, "成本 ¥120 · 卖相 8.5 · 工艺 6 · 竞品同款率 35%"),
        (260,  "B 奶油白法式开衫",  92, "成本 ¥85 · 卖相 9.0 · 工艺 8 · 竞品同款率 70%  ⭐"),
        (470,  "C 海盐蓝防晒衬衫",  74, "成本 ¥95 · 卖相 7.5 · 工艺 7 · 竞品同款率 25%"),
        (680,  "D 焦糖针织毛衣",    81, "成本 ¥110 · 卖相 8.0 · 工艺 8 · 竞品同款率 45%"),
        (890,  "E 极简通勤西服",    66, "成本 ¥160 · 卖相 7.0 · 工艺 9 · 竞品同款率 80%"),
    ]
    for x, title, score, detail in plans:
        is_best = score >= 90
        bg = "#fef3c7" if is_best else "#ffffff"
        border = "#f59e0b" if is_best else "#e5e7eb"
        round_rect(d, x, 100, 200, 280, 8, bg, border, 2 if is_best else 1)
        # 假图
        round_rect(d, x + 20, 120, 160, 110, 4, "#dbeafe")
        d.text((x + 60, 165), "[方案图]", font=font(13), fill="#94a3b8")
        d.text((x + 20, 245), title, font=font(13, True), fill="#1e293b")

        # 分数
        score_color = "#22c55e" if score >= 85 else ("#f59e0b" if score >= 75 else "#94a3b8")
        round_rect(d, x + 20, 275, 160, 30, 4, score_color)
        d.text((x + 70, 281), f"AI {score}", font=font(15, True), fill="#ffffff")
        if is_best:
            d.text((x + 90, 232), "⭐ 推荐", font=font(11, True), fill="#92400e")

        # 细节
        text_wrap(d, x + 20, 320, 160, detail, font(10), "#475569", line_h=15)

    # 底部 AI 分析
    round_rect(d, 30, 410, 1140, 270, 8, "#eef2ff", "#a5b4fc", 2)
    d.text((50, 426), "🤖 DEEPSEEK V4 · 综合评估推理过程", font=font(13, True), fill="#3730a3")
    d.text((50, 458), "【推荐 B 方案 · AI 92 分】", font=font(14, True), fill="#10b981")
    text_wrap(d, 50, 488, 1100,
              "• 成本最低（¥85）：比同类新品低 12%，毛利空间大",
              font(12), "#1e293b")
    text_wrap(d, 50, 510, 1100,
              "• 竞品同款率 70%：用户搜索高频，自然流量好",
              font(12), "#1e293b")
    text_wrap(d, 50, 532, 1100,
              "• 工艺难度 8/10：ZC 工厂可实现，预计交期 18 天",
              font(12), "#1e293b")
    text_wrap(d, 50, 554, 1100,
              "• 风险提示：面料供应商绍兴王哥目前订单饱和，建议提前 5 天下单锁产能",
              font(12), "#ef4444")
    d.text((50, 590), "📊 历史数据支撑：去年同类「奶油白开衫」毛利率 31%（行业均 25%）", font=font(11), fill="#64748b")
    d.text((50, 614), "🎯 老板娘选 B 方案 → 自动建任务给 production-supplier + 04_上新波段", font=font(11), fill="#64748b")
    d.text((50, 644), "⏱ 整个评估过程：1.8 秒（拉 16 表 → DEEPSEEK 推理 → 输出）", font=font(11, True), fill="#3730a3")

    img.save(os.path.join(OUT_DIR, "demo-launch-decision.png"), "PNG", optimize=True)


def gen_personal_mirror():
    img, d = make_canvas()
    draw_header(d, "🪞 personal-mirror — 员工今日真实贡献镜像",
                "22:00 自动拉员工飞书一天行为 → AI 4 维分析 → 老板娘看真实工作")

    # 左：员工日活动
    round_rect(d, 30, 100, 510, 580, 8, "#ffffff", "#e5e7eb", 1)
    d.text((50, 120), "👤 朱健豪 · 内容编辑 · 2026-05-05 镜像", font=font(13, True), fill="#1e293b")

    timeline = [
        ("09:15", "完成任务", "DRS-0429 直播脚本 V1", "#10b981"),
        ("10:30", "参会", "周一例会 · 核心议程发言 3 次", "#3b82f6"),
        ("11:50", "发起讨论", "06_选题池 提了 4 条新选题", "#10b981"),
        ("13:20", "推动", "@朱健豪、@申丽媛 跨部门对接", "#10b981"),
        ("14:10", "完成任务", "竞品博主分析报告", "#10b981"),
        ("15:30", "参会", "供应商对接（旁听 2 句话）", "#94a3b8"),
        ("16:00", "完成任务", "VIP 客户朋友圈文案 3 条", "#10b981"),
        ("17:20", "提交", "本周直播 v2 脚本（待老板娘审）", "#f59e0b"),
        ("18:30", "下班", "今日累计在线 9.3h", "#94a3b8"),
    ]
    cy = 155
    for t, kind, text, color in timeline:
        d.text((50, cy), t, font=font(11), fill="#94a3b8")
        d.ellipse([(110, cy + 2), (124, cy + 16)], fill=color)
        d.text((140, cy), kind, font=font(11, True), fill=color)
        d.text((220, cy), text, font=font(11), fill="#1e293b")
        cy += 30

    # 右：AI 4 维分析
    lark_card(d, 580, 110, 590, 580, "🪞 朱健豪 今日真实贡献镜像  · 22:00",
              "#8b5cf6",
              [
                  ("text", "🤖 DEEPSEEK 4 维度分析"),
                  ("text", "—————————"),
                  ("text", "📋 任务推进  9.0 / 10  ✓优秀"),
                  ("kv", "• 完成 4 个任务（含 1 个跨部门）"),
                  ("kv", "• 提交 1 个待审脚本"),
                  ("text", ""),
                  ("text", "💬 沟通密度  8.0 / 10  ✓良好"),
                  ("kv", "• 发起 06 表 4 条新选题"),
                  ("kv", "• 主动推动跨部门对接"),
                  ("text", ""),
                  ("text", "🎤 会议参与  8.5 / 10  ✓主动"),
                  ("kv", "• 周一例会发言 3 次（核心议程）"),
                  ("kv", "• 供应商会旁听贡献低（合理）"),
                  ("text", ""),
                  ("text", "✨ 重点产出  9.5 / 10  ✓亮点"),
                  ("kv", "• DRS-0429 直播脚本 V1 已就绪"),
                  ("kv", "• VIP 朋友圈文案，质量高"),
                  ("text", ""),
                  ("text", "📊 综合评分 8.8 / 10  · 真实努力 ✓"),
                  ("kv", "（不是日报敷衍，行为数据支撑）"),
              ])

    img.save(os.path.join(OUT_DIR, "demo-personal-mirror.png"), "PNG", optimize=True)


# 跑全部
if __name__ == "__main__":
    print("生成 8 个核心 skill 演示图...")
    gen_omnitask_bridge()
    print("  ✓ omnitask-bridge")
    gen_wechat_monitor()
    print("  ✓ wechat-monitor")
    gen_morning_report()
    print("  ✓ morning-report")
    gen_product_library()
    print("  ✓ product-library")
    gen_blogger_monitor()
    print("  ✓ blogger-monitor")
    gen_wxauto_supplier()
    print("  ✓ wxauto-supplier-bridge")
    gen_stock_replenishment()
    print("  ✓ stock-replenishment")
    gen_launch_decision()
    print("  ✓ launch-decision")
    gen_personal_mirror()
    print("  ✓ personal-mirror")
    print("\n全部 9 张完成（含 1 张备选 personal-mirror，共 9 张）。")
