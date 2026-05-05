"""微信群速览 — 截图主窗口 → DOUBAO 视觉识别 → 飞书卡片

风险：0（OS 级截图，不动微信进程）
兼容：所有微信版本（4.0/4.1/5.0），不依赖 wxauto

用法：
  python scan-wechat.py
  python scan-wechat.py --keywords "DRS-0429,出货,质量"   # 关键词命中即报警
  python scan-wechat.py --no-cleanup                       # 保留截图（默认用完即删）
"""

import os, sys, json, base64, argparse, subprocess, tempfile, time
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pygetwindow as gw
import pyautogui
from openai import OpenAI


DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "doubao-1-5-vision-pro-32k-250115")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BOSS_CHAT = os.environ.get("LARK_FASHION_COCKPIT_BOSS_CHAT", "")

PROMPT = """你正在看一张 PC 微信主窗口截图。请系统提取信息并返回 JSON：

{
  "groups_with_unread": [
    {"name": "群名", "unread_count": 数字 或 null, "last_msg_preview": "最后一条预览文字", "is_at_me": true/false}
  ],
  "summary": "用 1-2 句话概括「过去这段时间微信里发生了什么值得老板知道的」",
  "important_alerts": ["命中关键词或 @我 的紧急消息列表，每条一句话"],
  "noise_groups": ["营销号/广告/家庭群等不重要的群名"]
}

规则：
1. 只识别左侧群列表里**有未读红点**或**预览文字带价值信号**的群
2. 群名后的数字标签（如 [3]、[12]）就是 unread_count
3. 如果预览前有"[有人@你]"或类似标记，is_at_me=true
4. summary 要面向老板视角，过滤掉营销号/家庭闲聊
5. 严格输出 JSON，不要 markdown 代码块包裹"""


def find_wechat_window():
    for w in gw.getAllWindows():
        if (w.title or "") in ("微信", "Weixin", "WeChat"):
            return w
    return None


def capture_wechat() -> bytes:
    win = find_wechat_window()
    if not win:
        raise RuntimeError("没找到微信主窗口（请确认 PC 微信开着且不在托盘里）")
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.6)
    except Exception:
        pass
    region = (win.left, win.top, win.width, win.height)
    shot = pyautogui.screenshot(region=region)
    import io
    buf = io.BytesIO()
    shot.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def call_doubao(img_bytes: bytes, keywords: list) -> dict:
    if not DOUBAO_API_KEY:
        raise RuntimeError("缺 DOUBAO_API_KEY，请先在 .env 配置")

    b64 = base64.b64encode(img_bytes).decode()
    prompt = PROMPT
    if keywords:
        prompt += f"\n\n额外关注的关键词列表（命中放进 important_alerts）：{', '.join(keywords)}"

    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    resp = client.chat.completions.create(
        model=DOUBAO_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]}],
        temperature=0.2,
        max_tokens=2000,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def post_lark_card(result: dict):
    if not BOSS_CHAT:
        print("⚠ LARK_FASHION_COCKPIT_BOSS_CHAT 未配，跳过飞书发送")
        return False

    unread = result.get("groups_with_unread", [])
    alerts = result.get("important_alerts", [])
    summary = result.get("summary", "")

    color = "red" if alerts else ("orange" if unread else "blue")
    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**📱 微信群速览**  ·  {datetime.now().strftime('%H:%M')}"}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**摘要**\n{summary}"}},
    ]
    if alerts:
        a_text = "\n".join(f"🚨 {a}" for a in alerts[:5])
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**紧急消息**\n{a_text}"}})
    if unread:
        u_lines = []
        for g in unread[:8]:
            cnt = f"[{g['unread_count']}]" if g.get("unread_count") else ""
            at = " 🔔@你" if g.get("is_at_me") else ""
            u_lines.append(f"• **{g.get('name','?')}** {cnt}{at}\n  {g.get('last_msg_preview','')}")
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": "**未读群**\n" + "\n".join(u_lines)}})

    card = {"config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "📱 微信群速览"},
                       "template": color},
            "elements": elements}

    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False)

    r = subprocess.run(
        [LARK_CLI, "im", "+message-send",
         "--receive-id-type", "chat_id",
         "--receive-id", BOSS_CHAT,
         "--msg-type", "interactive",
         "--content", "@" + path],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    os.remove(path)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", default="", help="逗号分隔的关键词，命中即报警")
    ap.add_argument("--no-cleanup", action="store_true", help="不删除截图（默认用完即删）")
    args = ap.parse_args()
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    print("=== 微信群速览 ===\n")

    print("[1/3] 截图微信主窗口...")
    img = capture_wechat()
    print(f"      截图 {len(img)/1024:.1f} KB")

    print("\n[2/3] DOUBAO 视觉分析...")
    try:
        result = call_doubao(img, keywords)
    except Exception as e:
        print(f"❌ DOUBAO 调用失败: {e}")
        sys.exit(1)

    print(f"      识别到 {len(result.get('groups_with_unread',[]))} 个未读群")
    if result.get("important_alerts"):
        print(f"      🚨 {len(result['important_alerts'])} 条紧急消息")

    print("\n[3/3] 发飞书卡片...")
    ok = post_lark_card(result)
    print(f"      {'✓ 已发' if ok else '⚠ 跳过/失败'}")

    print(f"\n=== 摘要 ===\n{result.get('summary','(无)')}")
    if result.get("important_alerts"):
        print("\n=== 紧急 ===")
        for a in result["important_alerts"]:
            print(f"  🚨 {a}")


if __name__ == "__main__":
    main()
