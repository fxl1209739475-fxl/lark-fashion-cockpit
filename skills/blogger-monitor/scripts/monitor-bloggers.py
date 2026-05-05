"""对标博主视频监控 — 拉表 + 4 路筛选 + 飞书工作汇报卡片

复刻 douyin-monitor AI 博主监控的算法（4 路筛选 + 爆款指数排序），
聚焦女装赛道，把 TOP 视频 + 完整口播文案 + 数据指标汇报到飞书群。

用法：
  python scripts/monitor-bloggers.py
  python scripts/monitor-bloggers.py --reply-chat-id oc_xxx
  python scripts/monitor-bloggers.py --top 5  # TOP N 数量
"""

import subprocess, json, os, argparse
from datetime import datetime, timedelta

BASE = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
TABLE = "tblPDTGpUiJxZwHA"  # 27_对标博主视频监控
LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
DEFAULT_CHAT = "oc_45e0995a007db9d7f1859fa17b6566f6"  # 老板独人通知群
TABLE_URL = f"https://my.feishu.cn/base/{BASE}?table={TABLE}"


def fetch():
    r = subprocess.run(
        [LARK_CLI, "base", "+record-list", "--base-token", BASE, "--table-id", TABLE,
         "--limit", "200", "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    if r.returncode != 0:
        raise RuntimeError(f"record-list failed: {r.stderr[:400]}")
    d = json.loads(r.stdout)
    fields = d["data"]["fields"]
    rows = d["data"]["data"]
    out = []
    for row in rows:
        rec = dict(zip(fields, row))
        def unwrap(v):
            if isinstance(v, list) and v: return v[0]
            return v
        out.append({k: unwrap(v) for k, v in rec.items()})
    return out


def fmt_num(n):
    n = int(n or 0)
    if n >= 10000: return f"{n/10000:.1f}w"
    if n >= 1000: return f"{n/1000:.1f}k"
    return str(n)


def build_card(videos, top_n=3):
    selected = [v for v in videos if v.get("状态") == "已选中"]
    pending = [v for v in videos if v.get("状态") == "待评估"]
    selected.sort(key=lambda v: v.get("爆款指数", 0) or 0, reverse=True)

    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Header 总览
    overview = (f"**📊 监控博主：** {len(set(v.get('博主名称','') for v in videos))} 位  "
                f"｜ **今日抓取视频：** {len(videos)} 条\n"
                f"**🎯 已选中（值得二创）：** {len(selected)} 条  "
                f"｜ **待评估：** {len(pending)} 条\n")

    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": overview}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md",
            "content": f"**🔥 爆款指数 TOP {top_n}（按算法排序）**"}},
    ]

    for i, v in enumerate(selected[:top_n], 1):
        博主 = v.get("博主名称", "")
        粉丝 = fmt_num(v.get("粉丝数", 0))
        标题 = v.get("视频标题", "")
        url = v.get("视频链接", "")
        if isinstance(url, dict): url = url.get("link", "") or url.get("text", "")
        点赞 = fmt_num(v.get("点赞数", 0))
        评论 = fmt_num(v.get("评论数", 0))
        收藏 = fmt_num(v.get("收藏数", 0))
        分享 = fmt_num(v.get("分享数", 0))
        zan_fen = v.get("赞粉比", 0) or 0
        collect_rate = v.get("收藏率", 0) or 0
        bao = v.get("爆款指数", 0) or 0
        ai_s = v.get("AI 评分", 0) or 0
        角度 = v.get("推荐角度", "")
        文案 = v.get("口播文案", "") or ""

        # 数据指标
        metrics = (f"👍 {点赞}  💬 {评论}  ⭐ {收藏}  🔄 {分享}\n"
                   f"赞粉比 **{zan_fen:.2%}**  收藏率 **{collect_rate:.2%}**  "
                   f"爆款指数 **{bao}/10**  AI 评分 **{ai_s}/10**")

        # 文案摘要
        if 文案 and 文案.strip():
            type_label = "🎤 有口播"
            doc_short = 文案[:120] + ("..." if len(文案) > 120 else "")
            doc_block = f"**口播文案（前 120 字）：** {doc_short}"
        else:
            type_label = "🧥 纯穿搭（无口播）"
            doc_block = "**视频类型：** 纯穿搭走秀，无口播文案"

        elements.append({"tag": "hr"})
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"**[{i}] {博主}** · 粉丝 {粉丝} · {type_label}\n"
                       f"📝 **{标题}**\n"
                       f"{metrics}\n"
                       f"💡 推荐角度：{角度}\n"
                       f"{doc_block}"}})
        if url:
            elements.append({"tag": "action", "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "▶ 看视频"},
                 "type": "default", "url": url},
            ]})

    elements.append({"tag": "hr"})
    elements.append({"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "📋 查看完整 27 表"},
         "type": "primary", "url": TABLE_URL},
    ]})
    elements.append({"tag": "note", "elements": [{"tag": "plain_text",
        "content": f"扫描时间 {today} ｜ 4 路筛选：AI≥7 / 收藏率≥10% / 评赞比≥8% / 赞粉比≥40%"}]})

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "👀 对标博主每日监控"},
            "template": "blue",
        },
        "elements": elements,
    }


def send_card(chat_id, card):
    card_json = json.dumps(card, ensure_ascii=False, separators=(',', ':'))
    r = subprocess.run(
        [LARK_CLI, "im", "+messages-send",
         "--chat-id", chat_id, "--msg-type", "interactive",
         "--content", card_json],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if r.returncode != 0:
        print(f"✗ send_card rc={r.returncode}: {r.stderr[:300]}")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reply-chat-id", default=DEFAULT_CHAT)
    ap.add_argument("--top", type=int, default=3)
    args = ap.parse_args()

    print(f"[1/3] 拉 27_对标博主视频监控 ...")
    videos = fetch()
    print(f"  共 {len(videos)} 条视频")

    print(f"[2/3] 构建汇报卡片 ...")
    card = build_card(videos, top_n=args.top)

    print(f"[3/3] 发到飞书群 {args.reply_chat_id[:14]}...")
    ok = send_card(args.reply_chat_id, card)
    print("✓ 完成" if ok else "✗ 失败")


if __name__ == "__main__":
    main()
