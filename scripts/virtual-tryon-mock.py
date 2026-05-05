"""virtual-tryon-mock.py — 虚拟试穿（最小演示版）

工作流（演示）：
  1. 拉指定 SKU 的产品图（assets/products/<SKU>.jpg）
  2. 模特占位图（assets/products/model.jpg 或自动生成）
  3. PIL 合成：产品图叠加在模特身上对应位置（hat/top/bottom/shoes）
  4. 输出 outfit_<SKU1>_<SKU2>.jpg

真生产架构（待接通）：
  - 阿里通义万相 OutfitAnyone API（推荐，电商场景训练）
  - 快手可灵 Kolors-VTON
  - 开源 OOTDiffusion / IDM-VTON（自部署，要 GPU）

用法：
  python virtual-tryon-mock.py --top DRS-0429-FL --accessory KNT-0402-CD
"""
import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

PRODUCTS_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\products"
OUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\tryon"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"


def gen_model_silhouette():
    """生成模特剪影占位图"""
    W, H = 600, 1200
    img = Image.new("RGB", (W, H), (245, 240, 235))
    draw = ImageDraw.Draw(img)

    skin = (250, 220, 195)
    body = (230, 210, 190)

    # 头
    draw.ellipse([245, 70, 355, 200], fill=skin)
    # 颈部
    draw.rectangle([285, 200, 315, 230], fill=skin)
    # 上身
    draw.rectangle([200, 230, 400, 580], fill=body, outline=(180, 160, 140), width=2)
    # 下身
    draw.rectangle([220, 580, 380, 950], fill=body, outline=(180, 160, 140), width=2)
    # 腿（分开）
    draw.rectangle([225, 950, 290, 1130], fill=body)
    draw.rectangle([310, 950, 375, 1130], fill=body)

    # 标注
    f = ImageFont.truetype(FONT_REG, 28)
    draw.text((220, 30), "lark-fashion-cockpit · 占位模特", font=f, fill=(120, 100, 90))

    return img


def overlay_product(model_img, prod_img, region):
    """把产品图叠加到模特身上对应区域"""
    x, y, w, h = region
    prod_resized = prod_img.resize((w, h))
    # 产品图按 0.6 透明度叠加（保留模特轮廓）
    blended_region = Image.blend(
        model_img.crop((x, y, x + w, y + h)).convert("RGB"),
        prod_resized.convert("RGB"),
        alpha=0.85,
    )
    model_img.paste(blended_region, (x, y))
    return model_img


def get_region(sku):
    """根据 SKU 推断身体区域"""
    prefix = sku.split("-")[0]
    return {
        "DRS": (180, 250, 240, 700),     # 连衣裙：上身+腿
        "PNT": (210, 600, 200, 380),     # 裤子：下身
        "KNT": (200, 230, 220, 360),     # 针织：上身
        "SHT": (200, 230, 220, 360),     # 衬衫：上身
        "SKT": (220, 600, 180, 340),     # 半裙：下身
        "OUT": (180, 220, 250, 380),     # 外套：上身（更宽）
    }.get(prefix, (200, 230, 220, 700))


def compose(skus, outfit_name="搭配方案"):
    # 模特图
    model_path = os.path.join(PRODUCTS_DIR, "model.jpg")
    if os.path.exists(model_path):
        model = Image.open(model_path).convert("RGB")
    else:
        model = gen_model_silhouette()

    # 复制底图
    canvas = model.copy()

    # 叠加每个产品
    used_regions = []
    for sku in skus:
        prod_path = os.path.join(PRODUCTS_DIR, f"{sku}.jpg")
        if not os.path.exists(prod_path):
            print(f"  ⚠ skip {sku}, no image at {prod_path}")
            continue
        prod = Image.open(prod_path).convert("RGB")
        region = get_region(sku)
        canvas = overlay_product(canvas, prod, region)
        used_regions.append((sku, region))
        print(f"  + {sku} 叠加在 region {region}")

    # 加边距 + 标题
    W, H = canvas.size
    final = Image.new("RGB", (W + 40, H + 200), (250, 248, 244))
    final.paste(canvas, (20, 100))
    draw = ImageDraw.Draw(final)

    # 标题
    f_title = ImageFont.truetype(FONT_BD, 38)
    draw.text((30, 25), f"👗 {outfit_name}", font=f_title, fill=(60, 50, 40))
    f_sub = ImageFont.truetype(FONT_REG, 22)
    draw.text((30, 70), f"组合: {' + '.join(skus)}", font=f_sub, fill=(120, 110, 100))

    # 底部说明
    foot = "⚠️ 这是 PIL 占位演示版。真生产接通阿里 OutfitAnyone / 可灵 Kolors-VTON 输出真实模特图"
    f_foot = ImageFont.truetype(FONT_REG, 16)
    draw.text((30, H + 130), foot, font=f_foot, fill=(160, 80, 80))
    foot2 = "lark-fashion-cockpit · virtual-tryon"
    draw.text((30, H + 165), foot2, font=f_foot, fill=(160, 160, 180))

    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", required=True, help="主推 SKU")
    ap.add_argument("--accessory", help="搭配 SKU")
    ap.add_argument("--name", default="搭配方案")
    args = ap.parse_args()

    skus = [args.top]
    if args.accessory:
        skus.append(args.accessory)

    print(f"=== virtual-tryon (mock) ===")
    print(f"组合: {' + '.join(skus)}")
    img = compose(skus, args.name)

    out_name = "+".join(skus) + ".jpg"
    out_path = os.path.join(OUT_DIR, out_name)
    img.save(out_path, "JPEG", quality=92)
    print(f"\n✅ 输出: {out_path}  ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    main()
