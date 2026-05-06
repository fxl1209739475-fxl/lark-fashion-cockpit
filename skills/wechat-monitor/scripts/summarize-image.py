"""微信群消息长截图 AI 总结（半自动 — 高 ROI）

适用场景：
  用户用飞书滚动截屏 / Snagit / 任何第三方工具截一张紧凑长图
  → 把图发给 cockpit 飞书机器人（或本地路径）→ DOUBAO 自动总结 → 飞书卡片回执

为什么这条路最稳：
  - 跳过 Win11 焦点限制 / Cursor 子窗口遮挡 / wxauto 兼容性等坑
  - 飞书滚动截屏的拼接质量极高（OCR + 像素对齐）
  - DOUBAO 视觉对中文密集聊天识别准确（实测一张 1076×21180 长图识别 98 条消息无漏）

用法：
  python summarize-image.py --image C:\\path\\to\\screenshot.png
  python summarize-image.py --image ... --hint "微信终极目标群 5/4 12:00 - 5/5 23:59"
  python summarize-image.py --image ... --no-send   # 不发飞书，只终端打印
"""

import os, sys, json, base64, argparse, subprocess, io, tempfile
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PIL import Image
from openai import OpenAI

try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass


DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "doubao-1-5-vision-pro-32k-250115")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BOSS_CHAT = os.environ.get("LARK_FASHION_COCKPIT_BOSS_CHAT", "")


def split_long_image(img: Image.Image, seg_h: int = 3500, overlap: int = 200) -> list:
    """长图按高度切段（保持宽度），段间留 overlap 防消息切断"""
    W, H = img.size
    if H <= seg_h:
        return [img]
    segs = []
    y = 0
    while y < H:
        segs.append(img.crop((0, y, W, min(y + seg_h, H))))
        if y + seg_h >= H:
            break
        y += seg_h - overlap
    return segs


def build_prompt(num_segs: int, hint: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    seg_note = (f"\n\n输入说明：下面 {num_segs} 张图是同一段连续滚动聊天的纵向切片"
                f"（按时间从旧到新，第 1 段最旧，第 {num_segs} 段最新；段间约 200 px 重叠）。"
                f"请把它们当作一张完整长图来理解，**不要重复计数重叠区域里的消息**。"
                if num_segs > 1 else "")
    hint_note = f"\n\n额外提示：{hint}" if hint else ""

    return f"""这是一张微信/飞书/类似 IM 的群聊或私聊滚动长截图。当前时间：{now}{hint_note}

任务：完整提取并总结所有可见消息。

# 时间识别规则
- "今天 14:30" / "14:30" → 今天
- "昨天 18:00" → 昨天
- "周一 23:02" / "星期二 09:30" → 推算实际日期
- "5月3日 14:00" / "12月20日 18:00" → 当年该日
- "MM/DD" 简写 → 当年
- "2025年12月20日 18:00" → 跨年带年份

# 提取要求
1. 每条消息：发送人、时间、内容
2. 群聊把所有人发言都纳入（不只关注某一个人）
3. summary 要全面：聊了哪些话题、谁主导发言、出现了什么决议/争论/重要信息
4. key_points 列出**所有**值得关注的信息点（包括别人之间的讨论结论、行业动态、商务信息等）
5. things_for_you = 跟用户**间接或直接相关**的事（被@、问你、跟你业务相关、值得关注的趋势）

严格输出 JSON（不要 markdown 代码块）：
{{
  "date_observed": "实际看到的最早 - 最新时间",
  "total_messages": 数字,
  "main_participants": ["主要发言人 1", "主要发言人 2"],
  "topics": ["讨论话题 1", "话题 2"],
  "summary": "6-10 句完整总结",
  "key_points": ["要点 1", "要点 2", "..."],
  "things_for_you": ["跟用户相关或值得关注的事，无则空数组"],
  "raw_excerpts": [
    {{"time": "X月X日 HH:MM", "from": "发送人名", "content": "原文摘录"}}
  ],
  "tone": "氛围（友好/讨论激烈/技术分享/吐槽/商务对接 等）"
}}{seg_note}"""


def summarize_long_image(image_path: str, hint: str = "") -> dict:
    if not DOUBAO_API_KEY:
        raise RuntimeError("缺 DOUBAO_API_KEY，请配置 .env")

    img = Image.open(image_path)
    print(f"[1/3] 读取长图: {img.size[0]}x{img.size[1]}  {os.path.getsize(image_path)/1024:.0f} KB")

    segs = split_long_image(img, seg_h=3500, overlap=200)
    print(f"[2/3] 切成 {len(segs)} 段")

    contents = [{"type": "text", "text": build_prompt(len(segs), hint)}]
    total_kb = 0
    for i, seg in enumerate(segs):
        buf = io.BytesIO()
        seg.save(buf, format="JPEG", quality=75, optimize=True)
        kb = len(buf.getvalue()) / 1024
        total_kb += kb
        b64 = base64.b64encode(buf.getvalue()).decode()
        contents.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    print(f"      总 JPEG 大小: {total_kb:.0f} KB")

    print(f"[3/3] 调 DOUBAO ({DOUBAO_MODEL})...")
    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    resp = client.chat.completions.create(
        model=DOUBAO_MODEL,
        messages=[{"role": "user", "content": contents}],
        temperature=0.2,
        max_tokens=4000,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def post_lark_card(result: dict, source_label: str = "长图摘要"):
    if not BOSS_CHAT:
        print("⚠ LARK_FASHION_COCKPIT_BOSS_CHAT 未配，跳过飞书")
        return False

    things = result.get("things_for_you", [])
    msgs_n = result.get("total_messages", 0)
    color = "red" if things else ("orange" if msgs_n >= 10 else "blue")

    elements = [
        {"tag": "div", "text": {"tag": "lark_md",
            "content": f"**📨 {source_label}**\n\n📊 **{msgs_n}** 条 · ⏱ {result.get('date_observed','?')} · 🎭 {result.get('tone','?')}"}},
    ]
    if result.get("main_participants"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"👥 主要发言：{', '.join(result['main_participants'])}"}})
    if result.get("topics"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"🏷 话题：{', '.join(result['topics'])}"}})
    elements.append({"tag": "hr"})
    elements.append({"tag": "div", "text": {"tag": "lark_md",
        "content": f"**摘要**\n{result.get('summary','(无)')}"}})
    if result.get("key_points"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**关键信息**\n" + "\n".join(f"• {p}" for p in result["key_points"])}})
    if things:
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**值得你关注**\n" + "\n".join(f"⚡ {a}" for a in things)}})
    if result.get("raw_excerpts"):
        excerpts = "\n".join(f"• `{e.get('time','?')}` **{e.get('from','?')}**: {e.get('content','')[:80]}"
                              for e in result["raw_excerpts"][:10])
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**原文摘录**\n{excerpts}"}})

    card = {"config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": f"📨 {source_label}"}, "template": color},
            "elements": elements}

    r = subprocess.run(
        [LARK_CLI, "im", "+messages-send",
         "--as", "user", "--chat-id", BOSS_CHAT,
         "--msg-type", "interactive",
         "--content", json.dumps(card, ensure_ascii=False)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if r.returncode != 0:
        print(f"  lark-cli stderr: {(r.stderr or r.stdout or '')[:300]}")
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="长图路径")
    ap.add_argument("--hint", default="", help="额外提示（如来源、时间范围、背景）")
    ap.add_argument("--label", default="长图摘要", help="飞书卡片头部标签")
    ap.add_argument("--no-send", action="store_true", help="不发飞书，只终端打印")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        print(f"❌ 文件不存在: {args.image}")
        sys.exit(1)

    print(f"=== 长截图总结 ===\n来源: {args.image}\n")
    try:
        result = summarize_long_image(args.image, hint=args.hint)
    except Exception as e:
        print(f"❌ 总结失败: {e}")
        sys.exit(2)

    print(f"\n=== 结果 ===")
    print(f"日期范围: {result.get('date_observed','?')}")
    print(f"消息数: {result.get('total_messages',0)}")
    print(f"主要发言: {', '.join(result.get('main_participants',[]))}")
    print(f"话题: {', '.join(result.get('topics',[]))}")
    print(f"语气: {result.get('tone','?')}")
    print(f"\n{result.get('summary','(无)')}")
    if result.get("key_points"):
        print(f"\n关键点:")
        for p in result["key_points"]:
            print(f"  • {p}")
    if result.get("things_for_you"):
        print(f"\n值得关注:")
        for a in result["things_for_you"]:
            print(f"  ⚡ {a}")
    if result.get("raw_excerpts"):
        print(f"\n原文摘录（前 10 条）:")
        for e in result["raw_excerpts"][:10]:
            print(f"  [{e.get('time','?')}] {e.get('from','?')}: {e.get('content','')[:80]}")

    if not args.no_send:
        ok = post_lark_card(result, source_label=args.label)
        print(f"\n飞书卡片: {'✓ 已发' if ok else '⚠ 失败/跳过'}")


if __name__ == "__main__":
    main()
