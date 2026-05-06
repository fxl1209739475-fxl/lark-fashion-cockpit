"""微信聊天记录导出文件 → AI 总结

适用场景：
  用户用第三方导出工具（淘宝/eBay/亚马逊上的"微信聊天记录导出"软件）
  把某个群/联系人的历史聊天记录导出成 .txt / .json / .html 文件
  → cockpit 解析 → 时间过滤 → DEEPSEEK 总结 → 飞书卡片

为什么不像 summarize-image 用 DOUBAO 视觉：
  - 文本远比图便宜（DEEPSEEK 输入 token 单价 ~0.5 元/百万 vs DOUBAO 视觉 ~10 元/百万）
  - 文本结构化，能精确按时间窗过滤
  - 数千条消息一次塞进 DEEPSEEK 32K 上下文（图片视觉装不下这么多）

支持的导出格式（按市场常见度）：
  1. WXBackup / WeChatExporter / "留痕" 等的 txt 格式：
     2026-05-04 14:30:00 张三:
       消息内容
  2. 简单 txt（每行一条）：[时间] 发送人: 内容
  3. JSON 数组：[{"time": "2026-05-04T14:30:00", "from": "张三", "content": "..."}]

用法：
  python summarize-export.py --file C:\\path\\to\\export.txt --hours 72
  python summarize-export.py --file ... --label "ZC 工厂群"
"""

import os, sys, re, json, argparse, subprocess
from datetime import datetime, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from openai import OpenAI

try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BOSS_CHAT = os.environ.get("LARK_FASHION_COCKPIT_BOSS_CHAT", "")


def parse_messages(content: str) -> list:
    """解析多种常见导出格式 → 统一 [(datetime, from, text), ...]"""
    msgs = []

    # 尝试 1: JSON
    s = content.strip()
    if s.startswith("[") or s.startswith("{"):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                for it in data:
                    t = it.get("time") or it.get("timestamp") or it.get("date") or ""
                    f = it.get("from") or it.get("sender") or it.get("name") or ""
                    c = it.get("content") or it.get("text") or it.get("msg") or ""
                    dt = parse_time_string(t)
                    if dt and (f or c):
                        msgs.append((dt, str(f), str(c)))
                if msgs:
                    return msgs
        except Exception:
            pass

    # 尝试 2: WeChatExporter / 留痕 等 txt 格式
    # 匹配多行：第一行是 时间 + 发送人，后续行是消息内容（直到下一个时间行）
    # 时间格式：2026-05-04 14:30:00 / 2026/05/04 14:30 / 等
    time_pattern = re.compile(
        r"^(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?)\s+(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+?):?\s*$"
    )

    lines = content.split("\n")
    cur_time, cur_from, cur_text = None, None, []

    for line in lines:
        m = time_pattern.match(line.strip())
        if m:
            # 保存上一条
            if cur_time:
                msgs.append((cur_time, cur_from or "", "\n".join(cur_text).strip()))
            date_str = m.group(1).replace("年", "-").replace("月", "-").replace("日", "").replace("号", "").replace("/", "-")
            time_str = m.group(2)
            try:
                cur_time = datetime.strptime(f"{date_str} {time_str}",
                                              "%Y-%m-%d %H:%M:%S" if time_str.count(":") == 2 else "%Y-%m-%d %H:%M")
            except ValueError:
                cur_time = None
            cur_from = m.group(3).strip()
            cur_text = []
        else:
            if cur_time is not None and line.strip():
                cur_text.append(line)
    if cur_time:
        msgs.append((cur_time, cur_from or "", "\n".join(cur_text).strip()))

    if msgs:
        return msgs

    # 尝试 3: 简单格式 [time] from: content（单行）
    simple_pat = re.compile(r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\]\s+(.+?):\s*(.+)$")
    for line in lines:
        m = simple_pat.match(line.strip())
        if m:
            dt = parse_time_string(m.group(1))
            if dt:
                msgs.append((dt, m.group(2).strip(), m.group(3).strip()))

    return msgs


def parse_time_string(s: str):
    if not s:
        return None
    s = s.strip()
    fmts = [
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    # ISO 8601 带 Z 或时区
    if "T" in s:
        try:
            from datetime import datetime as _d
            return _d.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            pass
    return None


def filter_by_time(msgs: list, hours: int) -> list:
    if not hours:
        return msgs
    cutoff = datetime.now() - timedelta(hours=hours)
    return [m for m in msgs if m[0] >= cutoff]


def build_messages_text(msgs: list, max_chars: int = 25000) -> str:
    """把消息列表转成 LLM 友好的文本，限制字数防爆 token"""
    lines = []
    total = 0
    for dt, fr, txt in msgs:
        line = f"[{dt.strftime('%m-%d %H:%M')}] {fr}: {txt}"
        if total + len(line) > max_chars:
            lines.append(f"\n（已截断，仅展示前 {len(lines)} 条 / 共 {len(msgs)} 条）")
            break
        lines.append(line)
        total += len(line)
    return "\n".join(lines)


def summarize_messages_via_deepseek(msgs: list, hours: int, label: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("缺 DEEPSEEK_API_KEY")
    if not msgs:
        return {"total_messages": 0, "summary": f"过去 {hours} 小时无消息", "raw_excerpts": []}

    text = build_messages_text(msgs)
    earliest = msgs[0][0].strftime("%m-%d %H:%M")
    latest = msgs[-1][0].strftime("%m-%d %H:%M")
    participants = list({m[1] for m in msgs if m[1]})[:20]

    prompt = f"""下面是「{label}」过去 {hours} 小时的微信聊天记录（共 {len(msgs)} 条，时间范围 {earliest} → {latest}）。

请分析后输出 JSON：

{{
  "date_observed": "{earliest} → {latest}",
  "total_messages": {len(msgs)},
  "main_participants": ["主要发言人 1", "主要发言人 2"],
  "topics": ["话题 1", "话题 2"],
  "summary": "6-10 句完整总结：发生了哪些事、谁主导发言、有什么决议/争论",
  "key_points": ["关键信息 1", "关键信息 2"],
  "things_for_you": ["跟用户相关或值得关注的事，无则空数组"],
  "raw_excerpts": [
    {{"time": "MM-DD HH:MM", "from": "发送人", "content": "原文摘录"}}
  ],
  "tone": "氛围"
}}

# 聊天记录
{text}

只返回 JSON，不要 markdown 代码块。"""

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content.strip()
    return json.loads(raw)


def post_lark_card(result: dict, hours: int, label: str):
    if not BOSS_CHAT:
        return False
    things = result.get("things_for_you", [])
    msgs_n = result.get("total_messages", 0)
    color = "red" if things else ("orange" if msgs_n >= 10 else "blue")

    elements = [
        {"tag": "div", "text": {"tag": "lark_md",
            "content": f"**📨 {label} · 过去 {hours}h 摘要**\n\n📊 **{msgs_n}** 条 · ⏱ {result.get('date_observed','?')} · 🎭 {result.get('tone','?')}"}},
    ]
    if result.get("main_participants"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"👥 主要发言：{', '.join(result['main_participants'])}"}})
    elements.append({"tag": "hr"})
    elements.append({"tag": "div", "text": {"tag": "lark_md",
        "content": f"**摘要**\n{result.get('summary','')}"}})
    if result.get("key_points"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**关键信息**\n" + "\n".join(f"• {p}" for p in result["key_points"])}})
    if things:
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**值得你关注**\n" + "\n".join(f"⚡ {a}" for a in things)}})
    if result.get("raw_excerpts"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**原文摘录**\n" + "\n".join(f"• `{e.get('time','?')}` **{e.get('from','?')}**: {e.get('content','')[:80]}" for e in result["raw_excerpts"][:10])}})

    card = {"config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": f"📨 {label} 摘要"}, "template": color},
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
    ap.add_argument("--file", required=True, help="导出文件路径 (.txt/.json)")
    ap.add_argument("--hours", type=int, default=72, help="过滤过去 N 小时（0=全部）")
    ap.add_argument("--label", default="导出聊天记录", help="飞书卡片标题")
    ap.add_argument("--no-send", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    print(f"=== 解析导出文件 ===\n源: {args.file}  ({len(content)} 字符)")
    msgs = parse_messages(content)
    if not msgs:
        print("❌ 没解析到任何消息。请检查文件格式。")
        print("支持格式：")
        print("  1. WeChatExporter txt:    YYYY-MM-DD HH:MM:SS 发送人:\\n  内容")
        print("  2. 简单 txt:              [YYYY-MM-DD HH:MM] 发送人: 内容")
        print("  3. JSON:                  [{time, from, content}, ...]")
        sys.exit(2)
    print(f"解析到 {len(msgs)} 条消息（{msgs[0][0]} → {msgs[-1][0]}）")

    filtered = filter_by_time(msgs, args.hours)
    print(f"过去 {args.hours}h 内: {len(filtered)} 条")

    if not filtered:
        print("⚠ 时间窗内无消息")
        sys.exit(0)

    print(f"\n[调 DEEPSEEK 总结...]")
    try:
        result = summarize_messages_via_deepseek(filtered, args.hours, args.label)
    except Exception as e:
        print(f"❌ 总结失败: {e}")
        sys.exit(3)

    print(f"\n=== 摘要 ===")
    print(f"消息数: {result.get('total_messages', 0)}")
    print(f"主要发言: {', '.join(result.get('main_participants',[]))}")
    print(f"\n{result.get('summary','')}")
    if result.get("key_points"):
        print(f"\n关键点:")
        for p in result["key_points"]:
            print(f"  • {p}")

    if not args.no_send:
        ok = post_lark_card(result, args.hours, args.label)
        print(f"\n飞书卡片: {'✓ 已发' if ok else '⚠ 失败'}")


if __name__ == "__main__":
    main()
