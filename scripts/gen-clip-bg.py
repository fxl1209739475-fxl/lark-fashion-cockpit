"""生成视频背景静态图（1920x1080）+ 标题 + 来源 + 主题"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\clips\bg.png"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"

W, H = 1920, 1080
img = Image.new("RGB", (W, H), (24, 24, 32))
draw = ImageDraw.Draw(img)

# 顶部装饰条
draw.rectangle([0, 0, W, 8], fill=(220, 50, 50))

# 大标题
f_title = ImageFont.truetype(FONT_BD, 90)
title = "信息上传下达"
bbox = draw.textbbox((0, 0), title, font=f_title)
tw = bbox[2] - bbox[0]
draw.text((W//2 - tw//2, 180), title, font=f_title, fill=(255, 220, 100))

# 副标题
f_sub = ImageFont.truetype(FONT_REG, 40)
sub = "lark-fashion-cockpit · 老板娘的痛点访谈"
bbox = draw.textbbox((0, 0), sub, font=f_sub)
sw = bbox[2] - bbox[0]
draw.text((W//2 - sw//2, 310), sub, font=f_sub, fill=(180, 180, 200))

# 中央 emoji / 装饰
f_emoji = ImageFont.truetype(FONT_BD, 220)
quote = "❝"
bbox = draw.textbbox((0, 0), quote, font=f_emoji)
qw = bbox[2] - bbox[0]
draw.text((W//2 - qw//2, 440), quote, font=f_emoji, fill=(80, 60, 60))

# 底部信息条
draw.rectangle([0, H-100, W, H], fill=(40, 40, 50))
f_foot = ImageFont.truetype(FONT_REG, 28)
foot = "来源：女装业务 AI 应用方案讨论 · 2026-04-29 · 飞书妙记自动剪辑"
bbox = draw.textbbox((0, 0), foot, font=f_foot)
fw = bbox[2] - bbox[0]
draw.text((W//2 - fw//2, H - 65), foot, font=f_foot, fill=(160, 160, 180))

img.save(OUT, "PNG")
print(f"Saved: {OUT} ({os.path.getsize(OUT)} bytes)")
