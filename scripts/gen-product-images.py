"""Generate placeholder product images for lark-fashion-cockpit demo.

Uses PIL to create 600x800 product cards with brand color, name, SKU, price.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\products"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"

PRODUCTS = [
    dict(sku="DRS-0429-FL", bg=(245, 240, 230), fg=(80, 50, 30),    name="法式碎花连衣裙",      brand="品牌一", price=299, tag="法式·约会"),
    dict(sku="PNT-0418-SU", bg=(35, 35, 35),    fg=(255, 255, 255), name="通勤西装裤",         brand="品牌一", price=239, tag="通勤·上班"),
    dict(sku="KNT-0402-CD", bg=(198, 134, 66),  fg=(255, 252, 240), name="短款焦糖针织开衫",   brand="品牌一", price=189, tag="学院·日常"),
    dict(sku="SHT-0420-SP", bg=(176, 224, 230), fg=(31, 78, 121),   name="海盐蓝防晒衬衫",     brand="品牌一", price=169, tag="韩系·旅行"),
    dict(sku="SKT-0328-A",  bg=(160, 160, 160), fg=(40, 40, 40),    name="高腰A字半身裙",      brand="品牌一", price=199, tag="通勤·日常"),
    dict(sku="KNT-2024-WL", bg=(255, 253, 208), fg=(120, 80, 40),   name="韩系慵懒针织毛衣",   brand="品牌二", price=259, tag="韩系·日常"),
    dict(sku="DRS-2024-LC", bg=(199, 21, 133),  fg=(255, 255, 255), name="法式蕾丝吊带连衣裙", brand="品牌二", price=329, tag="法式·派对"),
    dict(sku="OUT-2024-OL", bg=(20, 20, 20),    fg=(255, 255, 255), name="OL极简西服",         brand="品牌二", price=459, tag="通勤·上班"),
]

W, H = 600, 800

for p in PRODUCTS:
    img = Image.new("RGB", (W, H), p["bg"])
    draw = ImageDraw.Draw(img)

    # 顶部：品牌
    f_brand = ImageFont.truetype(FONT_REG, 22)
    draw.text((30, 25), p["brand"], font=f_brand, fill=p["fg"])

    # 顶部右侧：标签 pill
    f_tag = ImageFont.truetype(FONT_BOLD, 18)
    tag_text = p["tag"]
    bbox = draw.textbbox((0,0), tag_text, font=f_tag)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    pill_w = tw + 28
    pill_h = th + 16
    pill_x = W - 30 - pill_w
    pill_y = 22
    # 半透明背景 pill
    overlay = Image.new("RGBA", (pill_w, pill_h), (255, 255, 255, 80))
    img.paste(overlay, (pill_x, pill_y), overlay)
    draw.text((pill_x + 14, pill_y + 6), tag_text, font=f_tag, fill=p["fg"])

    # 中央：大圆 placeholder（代替商品视觉）
    cx, cy = W // 2, H // 2 - 40
    r = 180
    circle_color = tuple(min(255, c+25) if sum(p["bg"])<400 else max(0, c-25) for c in p["bg"])
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=circle_color)

    # 圆中央：SKU 后两段
    sku_short = p["sku"].split("-", 1)[1]
    f_sku_big = ImageFont.truetype(FONT_BOLD, 56)
    bbox = draw.textbbox((0,0), sku_short, font=f_sku_big)
    sw = bbox[2]-bbox[0]
    sh = bbox[3]-bbox[1]
    draw.text((cx - sw // 2, cy - sh // 2 - 8), sku_short, font=f_sku_big, fill=p["fg"])

    # 圆下方：品类前缀
    prefix = p["sku"].split("-")[0]
    cat_map = {"DRS": "DRESS", "PNT": "PANTS", "KNT": "KNIT", "SHT": "SHIRT",
               "SKT": "SKIRT", "OUT": "OUTER"}
    cat = cat_map.get(prefix, prefix)
    f_cat = ImageFont.truetype(FONT_REG, 20)
    bbox = draw.textbbox((0,0), cat, font=f_cat)
    cw = bbox[2]-bbox[0]
    draw.text((cx - cw // 2, cy + r//2 + 30), cat, font=f_cat, fill=p["fg"])

    # 底部：产品名 + 价格
    f_name = ImageFont.truetype(FONT_BOLD, 32)
    draw.text((30, H - 130), p["name"], font=f_name, fill=p["fg"])

    f_price = ImageFont.truetype(FONT_BOLD, 40)
    draw.text((30, H - 80), f"¥{p['price']}", font=f_price, fill=p["fg"])

    # SKU 右下
    f_sku = ImageFont.truetype(FONT_REG, 18)
    bbox = draw.textbbox((0,0), p["sku"], font=f_sku)
    skuw = bbox[2]-bbox[0]
    draw.text((W - 30 - skuw, H - 35), p["sku"], font=f_sku, fill=p["fg"])

    out_path = os.path.join(OUT_DIR, f"{p['sku']}.jpg")
    img.save(out_path, "JPEG", quality=92)
    print(f"OK {p['sku']} -> {out_path}  ({os.path.getsize(out_path)} bytes)")

print(f"\n{len(PRODUCTS)} product images generated.")
