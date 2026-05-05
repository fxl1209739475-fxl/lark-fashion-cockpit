"""Generate outfit collage: 2-3 products side-by-side with title + element tags.

Usage:
  python gen-outfit-image.py <main_sku> <pair_sku1> [pair_sku2] [--name "套装名"]
"""
import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFont

PRODUCTS_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\products"
OUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\outfits"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"

ap = argparse.ArgumentParser()
ap.add_argument("skus", nargs="+", help="product SKUs (first = main, rest = pairs)")
ap.add_argument("--name", default=None, help="outfit name")
ap.add_argument("--score", default=None, help="match score string")
ap.add_argument("--reason", default=None, help="match reason text")
ap.add_argument("--out", default=None, help="output filename (default <main>+<n>.jpg)")
args = ap.parse_args()

skus = args.skus
n = len(skus)
assert 2 <= n <= 4, "outfit needs 2-4 products"

PROD_W, PROD_H = 600, 800
GAP = 24
PAD = 40
HEADER_H = 130
FOOTER_H = 100

CANVAS_W = PROD_W * n + GAP * (n - 1) + PAD * 2
CANVAS_H = PROD_H + HEADER_H + FOOTER_H + PAD * 2

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (250, 248, 244))
draw = ImageDraw.Draw(canvas)

# 顶部 header bar
draw.rectangle([0, 0, CANVAS_W, HEADER_H + PAD], fill=(40, 38, 34))

# 标题
title = args.name or f"搭配 · {skus[0]} + {len(skus)-1} 件搭配款"
f_title = ImageFont.truetype(FONT_BOLD, 38)
draw.text((PAD, 30), title, font=f_title, fill=(255, 255, 255))

# 副标题：搭配组成
sub = " + ".join(skus)
f_sub = ImageFont.truetype(FONT_REG, 22)
draw.text((PAD, 80), sub, font=f_sub, fill=(220, 218, 210))

# 右上角分数 / brand 标记
brand_label = "lark-fashion-cockpit · 产品搭配推荐"
f_brand = ImageFont.truetype(FONT_REG, 16)
bbox = draw.textbbox((0, 0), brand_label, font=f_brand)
bw = bbox[2] - bbox[0]
draw.text((CANVAS_W - PAD - bw, 35), brand_label, font=f_brand, fill=(180, 180, 180))

if args.score:
    f_score = ImageFont.truetype(FONT_BOLD, 32)
    score_label = f"匹配 {args.score} 分"
    bbox = draw.textbbox((0, 0), score_label, font=f_score)
    sw_ = bbox[2] - bbox[0]
    draw.text((CANVAS_W - PAD - sw_, 70), score_label, font=f_score, fill=(255, 200, 50))

# 平铺产品
y0 = HEADER_H + PAD
for i, sku in enumerate(skus):
    img_path = os.path.join(PRODUCTS_DIR, f"{sku}.jpg")
    if not os.path.exists(img_path):
        print(f"WARN missing {img_path}, skipping")
        continue
    prod = Image.open(img_path)
    if prod.size != (PROD_W, PROD_H):
        prod = prod.resize((PROD_W, PROD_H))
    x = PAD + i * (PROD_W + GAP)
    canvas.paste(prod, (x, y0))

    # 主推/搭配标记
    f_role = ImageFont.truetype(FONT_BOLD, 24)
    role = "主推" if i == 0 else f"搭配 {i}"
    role_color = (220, 50, 50) if i == 0 else (50, 130, 220)
    badge_w = 100
    badge_h = 36
    draw.rectangle([x, y0, x + badge_w, y0 + badge_h], fill=role_color)
    bbox = draw.textbbox((0, 0), role, font=f_role)
    rw = bbox[2] - bbox[0]
    rh = bbox[3] - bbox[1]
    draw.text((x + badge_w//2 - rw//2, y0 + badge_h//2 - rh//2 - 2), role, font=f_role, fill=(255, 255, 255))

    # 加号 + 等号 连接
    if i < n - 1:
        plus_x = x + PROD_W + GAP // 2
        plus_y = y0 + PROD_H // 2
        f_plus = ImageFont.truetype(FONT_BOLD, 56)
        draw.text((plus_x - 16, plus_y - 36), "+", font=f_plus, fill=(120, 120, 120))

# 底部：理由
if args.reason:
    f_reason = ImageFont.truetype(FONT_REG, 20)
    fy = y0 + PROD_H + 30
    draw.text((PAD, fy), f"💡 AI 推荐理由：{args.reason}", font=f_reason, fill=(80, 80, 80))

# 底部 watermark
f_wm = ImageFont.truetype(FONT_REG, 14)
wm = "由 lark-fashion-cockpit · product-matching skill 自动生成"
bbox = draw.textbbox((0, 0), wm, font=f_wm)
wmw = bbox[2] - bbox[0]
draw.text((CANVAS_W // 2 - wmw // 2, CANVAS_H - 30), wm, font=f_wm, fill=(160, 160, 160))

# 输出
out_name = args.out or "+".join(skus) + ".jpg"
out_path = os.path.join(OUT_DIR, out_name)
canvas.save(out_path, "JPEG", quality=92)
print(f"OK -> {out_path}  ({os.path.getsize(out_path)} bytes, {CANVAS_W}x{CANVAS_H})")
