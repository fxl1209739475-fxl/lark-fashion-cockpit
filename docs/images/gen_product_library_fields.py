"""画产品库字段全景图（5 色块分区，模仿真实电商产品库 Excel 表头风格）"""

import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1500, 1100
OUT = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


img = Image.new("RGB", (W, H), "#fafbff")
d = ImageDraw.Draw(img)


def round_rect(x, y, w, h, r, fill, outline=None, outline_w=0):
    d.rounded_rectangle([(x, y), (x+w, y+h)], r, fill=fill, outline=outline, width=outline_w)


def text_center(x, y, w, txt, f, fill="#1e293b"):
    bbox = d.textbbox((0, 0), txt, font=f)
    tw = bbox[2] - bbox[0]
    d.text((x + (w-tw)//2, y), txt, font=f, fill=fill)


# ============= 标题 =============
text_center(0, 30, W, "📦 服装电商产品库 · 50 字段全景（基于真实业务梳理）",
            font(28, True), "#1e293b")
text_center(0, 70, W, "5 大功能区 · 从产品基础到月度货盘 · 经营驾驶舱核心数据中枢",
            font(13), "#64748b")

# ============= 5 区色卡 =============
SECTIONS = [
    {
        "x": 30, "y": 130, "w": 280, "color": "#3b82f6", "bg": "#eff6ff",
        "title": "🔵 产品基础信息", "subtitle": "12 字段",
        "fields": [
            "序号", "款号", "款式图", "产品名称",
            "售价", "直播日期", "成本", "成本货值",
            "季节（如 26夏）", "二级分类（连衣裙/T恤/裤/裙）",
            "难易分类", "待定（业务标记）",
        ],
    },
    {
        "x": 320, "y": 130, "w": 270, "color": "#f59e0b", "bg": "#fffbeb",
        "title": "🟡 生产 + 到仓状态", "subtitle": "10 字段",
        "fields": [
            "计划生产件数", "首单数", "生产货值",
            "已到仓数", "到仓货值",
            "到仓状态（3 未到仓 / 1 完全到仓）",
            "未到仓数", "未到仓货值",
            "在仓库存", "库存货值",
        ],
    },
    {
        "x": 600, "y": 130, "w": 270, "color": "#fb923c", "bg": "#fff7ed",
        "title": "🟠 库存 + 占用", "subtitle": "8 字段",
        "fields": [
            "在仓+未到仓货值",
            "在仓货值占总货值售罄率",
            "订单占有", "订单占有货值",
            "共有可用数",
            "近两天发货后预估退货数",
            "实销金额", "金额售罄率",
        ],
    },
    {
        "x": 880, "y": 130, "w": 280, "color": "#10b981", "bg": "#ecfdf5",
        "title": "🟢 销售统计", "subtitle": "13 字段",
        "fields": [
            "总销量", "总销售额",
            "总退货数", "总退货额",
            "发货数", "发货金额",
            "发货后退货数", "退货金额",
            "发货后退货率", "综合退货率",
            "预估实收件数", "预估实收金额",
            "备注",
        ],
    },
    {
        "x": 1170, "y": 130, "w": 300, "color": "#8b5cf6", "bg": "#f5f3ff",
        "title": "🟣 月度货盘梳理", "subtitle": "7 个独有字段",
        "fields": [
            "产品款式划分",
            "需完成目标售罄",
            "还需实销件数", "还需实销货值",
            "目前售罄率",
            "完成对应目标所需 gmv 件数",
            "完成对应目标所需 gmv 值",
        ],
    },
]

# 画每个区
for s in SECTIONS:
    x, y, w, color, bg = s["x"], s["y"], s["w"], s["color"], s["bg"]
    # 区背景
    h_total = 100 + len(s["fields"]) * 38 + 20
    round_rect(x, y, w, h_total, 12, bg, color, 2)

    # 头
    round_rect(x, y, w, 65, 12, color)
    text_center(x, y + 12, w, s["title"], font(15, True), "#ffffff")
    text_center(x, y + 38, w, s["subtitle"], font(11), "#ffffff")

    # 字段卡
    cy = y + 80
    for i, fname in enumerate(s["fields"]):
        round_rect(x + 12, cy, w - 24, 32, 6, "#ffffff", color, 1)
        d.text((x + 22, cy + 8), f"{i+1:2}.", font=font(10, True), fill=color)
        d.text((x + 50, cy + 7), fname, font=font(12), fill="#1e293b")
        cy += 38

# ============= 底部说明 =============
note_y = 760
round_rect(30, note_y, W - 60, 90, 12, "#1e293b")
text_center(30, note_y + 14, W - 60, "💡 这是「01_产品库」表的完整 schema",
            font(15, True), "#fbbf24")
text_center(30, note_y + 40, W - 60,
            "前 4 区（43 字段）= 单 SKU 实时数据；后 1 区（7 字段）= 月度货盘视图，基于前 4 区计算得出",
            font(12), "#cbd5e1")
text_center(30, note_y + 62, W - 60,
            "cockpit 用 lark-cli base 自动建表 + 灌 mock 数据，老板娘飞书一句话「找出售罄率低于 50% 的产品」就能拉这张表 → DEEPSEEK 分析",
            font(11), "#94a3b8")

# ============= 关键计算字段说明 =============
calc_y = 880
text_center(0, calc_y, W, "🧮 5 个关键计算公式（自动派生，不用手填）", font(15, True), "#1e293b")

calc_x = 60
calcs = [
    ("售罄率", "已实销 / 计划生产", "#10b981"),
    ("退货率", "退货数 / 总销量", "#ef4444"),
    ("可售天数", "在仓库存 / 日均销售", "#f59e0b"),
    ("实收金额", "总销售额 × (1 - 综合退货率)", "#3b82f6"),
    ("库存货值占比", "在仓货值 / 总生产货值", "#8b5cf6"),
]

for i, (name, formula, color) in enumerate(calcs):
    bx = 60 + i * 280
    round_rect(bx, calc_y + 35, 260, 90, 10, "#ffffff", color, 2)
    d.text((bx + 15, calc_y + 47), name, font=font(14, True), fill=color)
    text_wrap_text = formula
    d.text((bx + 15, calc_y + 75), formula, font=font(11), fill="#475569")
    d.text((bx + 15, calc_y + 100), "自动公式字段", font=font(10), fill="#94a3b8")

# ============= 落款 =============
text_center(0, H - 40, W,
            "lark-fashion-cockpit · 基于真实服装电商运营梳理 · 50 字段一表打尽",
            font(11), "#94a3b8")

img.save(os.path.join(OUT, "product-library-fields.png"), "PNG", optimize=True)
print(f"saved: {os.path.join(OUT, 'product-library-fields.png')}")
print(f"size: {os.path.getsize(os.path.join(OUT, 'product-library-fields.png'))/1024:.0f} KB")
