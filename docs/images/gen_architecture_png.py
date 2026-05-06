"""用 PIL 重画架构图 PNG（飞书云空间用，SVG 渐变不被 reportlab 支持所以重画）"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 820
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"

img = Image.new("RGB", (W, H), "#fafbff")
d = ImageDraw.Draw(img)

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def round_rect(x, y, w, h, r, fill, outline=None, outline_w=0):
    d.rounded_rectangle([(x, y), (x+w, y+h)], r, fill=fill, outline=outline, width=outline_w)

def text_center(x, y, w, txt, f, fill="#1e293b"):
    bbox = d.textbbox((0, 0), txt, font=f)
    tw = bbox[2] - bbox[0]
    d.text((x + (w-tw)//2, y), txt, font=f, fill=fill)

# 标题
text_center(0, 35, W, "lark-fashion-cockpit · 电商航母驾驶舱", font(30, True), "#1e293b")
text_center(0, 75, W, "飞书 CLI 创作者大赛 · 45 个 sub-skill · 从「散装能力」到「全员 ChatOps 产品」", font(13), "#64748b")

# 用户层
round_rect(380, 115, 520, 70, 35, "#ffffff", "#e0e7ff", 2)
text_center(380, 135, 520, "👥 老板 + 设计师 + 生产 + 内容 + 客服 + 主播 + …", font(14, True), "#1e293b")
text_center(380, 158, 520, "打开浏览器跟系统说话", font(11), "#64748b")

# 中央 omnitask hero（紫色）
round_rect(320, 215, 640, 125, 14, "#5b50e8")
text_center(320, 240, 640, "🚀 omnitask-bridge — 全员 ChatOps 驾驶舱", font(21, True), "#ffffff")
text_center(320, 268, 640, "本地 Web 系统（FastAPI 8080）+ 常驻聊天浮窗 + AI 路由编排", font(13), "#e0e7ff")
text_center(320, 290, 640, "\"通知 ZC 工厂\" / \"今天销售\" / \"建任务给马萍蔓\" / \"扫微信群\"", font(12), "#c7d2fe")
text_center(320, 312, 640, "↓ DEEPSEEK 解析意图 + 提取参数 → 路由到具体 skill", font(11), "#a5b4fc")

# 5 板块
panels = [
    (60,   "#0ea5e9", "📊 经营数据", "11 个 skill",
     ["product-library", "stock-replenishment", "platform-analytics", "profit-analysis", "launch-decision · …"]),
    (300,  "#10b981", "📱 跨平台 IM", "5 个 skill",
     ["cross-platform-im-agent", "wechat-monitor", "wxauto-supplier-bridge", "wecom-bridge", "multi-user-private-channels"]),
    (540,  "#f59e0b", "🎬 内容营销", "7 个 skill",
     ["blogger-monitor", "competitor-monitor", "content-pipeline", "live-streaming · private-domain", "video-script-parser · …"]),
    (780,  "#ec4899", "🎯 任务协作", "12 个 skill",
     ["task-collaboration", "approval-flow · okr-cascade", "morning-report · personal-mirror", "meeting-workflow · …", "order-fulfillment · helpdesk"]),
    (1020, "#8b5cf6", "🤖 AI 大脑", "10 个 skill",
     ["natural-language-router", "boss-clone-aily", "skill-recommender", "auto-scheduler", "knowledge-base · …"]),
]
for x, color, title, subtitle, items in panels:
    width = 200 if x == 1020 else 220
    round_rect(x, 380, width, 180, 12, color)
    text_center(x, 405, width, title, font(16, True), "#ffffff")
    text_center(x, 432, width, subtitle, font(10), "#ffffff")
    for i, line in enumerate(items):
        text_center(x, 460 + i*18, width, line, font(11), "#ffffff")

# 中央 omnitask 到各板块的箭头
for cx in [170, 410, 650, 890, 1120]:
    d.line([(640, 340), (cx, 380)], fill="#cbd5e1", width=2)

# 底层技术栈
round_rect(60, 615, 1160, 155, 14, "#1e293b")
text_center(60, 638, 1160, "数据 + 执行底座", font(14, True), "#94a3b8")

stack = [
    (120, 280, "📘 飞书多维表格 + CLI", "#60a5fa",
     ["27 张表 · base / im / task / calendar", "docs / drive / vc / minutes / approval"]),
    (420, 280, "🧠 AI 模型层", "#a78bfa",
     ["DEEPSEEK V4 Pro/Flash · 路由+总结", "DOUBAO 1.5 视觉 · 视频/截图理解"]),
    (720, 280, "🔌 外部数据源", "#34d399",
     ["抖音爬虫 · 小红书 · 视频号", "企业微信 API · 个人微信 RPA"]),
    (1020, 180, "⏰ 自动化", "#fbbf24",
     ["APScheduler 调度 12 个", "cron 任务 + 早 8 点早报"]),
]
for x, w, title, color, lines in stack:
    round_rect(x, 670, w, 80, 8, "#0f172a")
    text_center(x, 685, w, title, font(13, True), color)
    for i, ln in enumerate(lines):
        text_center(x, 710 + i*18, w, ln, font(11), "#94a3b8")

# 底部
text_center(0, 793, W,
            "所有 skill 都是 self-contained · npx skills add 一键安装 · 飞书 base 数据为底 · DEEPSEEK 自然语言路由 · 全员可用",
            font(11), "#94a3b8")

out = os.path.join(os.path.dirname(__file__), "architecture.png")
img.save(out, "PNG", optimize=True)
print(f"PNG: {os.path.getsize(out)/1024:.0f} KB → {out}")
