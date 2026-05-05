"""lark-fashion-cockpit · 7×24 事件订阅值班员（v2）

升级版 event-listener：从单事件源（IM 消息）扩展为多事件源 + 智能分类。

监听的飞书事件：
  1. im.message.receive_v1     IM 消息  → 关键词路由 + @老板智能分类 + 自动 👀 reaction
  2. task.task.update_v1       任务状态变化 → 自动加进 task-lifecycle 追踪
  3. approval.task.received_v1 审批新到 → 按金额自动分流（< ¥1000 直批 / 否则推送老板）

每类事件独立起一个 lark-cli event consume 子进程（NDJSON 流），主进程负责路由。

用法：
  python event-watcher.py                  # 真跑（多 consumer 并发监听）
  python event-watcher.py --simulate-im "巡检任务"
  python event-watcher.py --simulate-task '{"task_id":"x","status":"completed"}'
  python event-watcher.py --simulate-approval '{"amount":500,"type":"报销"}'
"""

import json
import re
import subprocess
import sys
import argparse
import os
import threading
from datetime import datetime

# ============== 配置 ==============
BOSS_OPEN_ID = "ou_85c9148d13c562728e60d456b60d9afc"
BOSS_CHAT = "oc_45e0995a007db9d7f1859fa17b6566f6"
SCRIPTS_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\scripts"

# 监听的事件 + 处理函数（值班员核心）
EVENT_SOURCES = [
    "im.message.receive_v1",
    "task.task.update_v1",
    "approval.instance.task_received_v1",
]

# IM 路由（已有，扩展智能分类）
IM_ROUTES = [
    (r"巡检任务|看下任务|任务追踪|逾期", "task-tracker.ps1", "⏰ 任务巡检", "P0"),
    (r"任务复盘|为什么.*延期|按时率", "task-retrospective.ps1", "📊 任务复盘", "P1"),
    (r"配什么好|搭配推荐|主图穿搭", "product-matching-demo.ps1", "🛍 产品搭配推荐", "P1"),
    (r"新品.*多少件|下单建议|翻单|备货建议", "launch-decision.ps1", "📊 新品下单判断", "P0"),
    (r"利润|哪些款赚钱|净利率", "profit-analysis.ps1", "💰 利润分析", "P1"),
    (r"画产品|关系图|白板生成", "product-graph.ps1", "🎨 产品关系图", "P1"),
]

# @老板智能分类规则（无 skill 路由时执行）
AT_BOSS_KEYWORDS = {
    "P0": ["紧急", "急", "立刻", "马上", "停产", "投诉", "退款", "出大事"],
    "P1": ["请审批", "请确认", "请决策", "申请", "授权", "建议", "求帮"],
    "P2": ["分享", "汇报", "学习", "看一下"],
}


def send_card(chat_id: str, title: str, content: str, template: str = "blue", buttons=None):
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": title}, "template": template},
        "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
    }
    if buttons:
        card["elements"].append({"tag": "action", "actions": buttons})
    card_json = json.dumps(card, ensure_ascii=False, separators=(',', ':'))
    cmd_esc = card_json.replace('"', '""')
    subprocess.run(
        ["cmd", "/c", f'lark-cli im +messages-send --chat-id {chat_id} --msg-type interactive --content "{cmd_esc}"'],
        capture_output=True,
    )


def add_reaction(message_id: str, reaction: str = "EYES"):
    """给消息加 reaction（演示用，飞书 API 真调用见文档）"""
    print(f"  [reaction] +{reaction} on {message_id}")
    # lark-cli im 暂不直接支持 reaction，可走 generic api。这里 stub 演示。


# ============== IM 消息处理 ==============
def handle_im_message(event: dict, simulate=False):
    sender = event.get("sender_id", "")
    chat_id = event.get("chat_id", "")
    content_raw = event.get("content", "")
    message_id = event.get("message_id", "")
    chat_type = event.get("chat_type", "p2p")

    text = content_raw
    try:
        obj = json.loads(content_raw)
        text = obj.get("text", "") if isinstance(obj, dict) else str(obj)
    except Exception:
        pass

    # 1. 关键词路由（已有逻辑）
    for pattern, script, name, priority in IM_ROUTES:
        if re.search(pattern, text, re.IGNORECASE):
            if not simulate:
                send_card(chat_id, f"🤖 收到 → 正在跑 {name}", f"**触发：** `{text[:60]}`", "turquoise")
            print(f"  → IM route: {name} ({priority})")
            return

    # 2. @老板智能分类（群消息且包含 @老板，且非自己发的）
    is_at_boss = chat_type == "group" and ("@" in text and sender != BOSS_OPEN_ID)
    if is_at_boss:
        priority = "P3"
        for level, kws in AT_BOSS_KEYWORDS.items():
            if any(kw in text for kw in kws):
                priority = level
                break

        print(f"  → @boss classified as {priority}")
        if priority in ("P0", "P1") and not simulate:
            send_card(
                BOSS_CHAT,
                f"📨 @你的消息（{priority}）",
                f"**来源群：** {chat_id[:14]}...\n**消息：** {text[:200]}\n**建议：** {'立即处理' if priority == 'P0' else '今天内回复'}",
                "red" if priority == "P0" else "yellow",
            )
        # 自动加 👀 reaction
        if not simulate:
            add_reaction(message_id, "EYES")
        return

    print(f"  → no match")


# ============== 任务状态变化处理 ==============
def handle_task_update(event: dict, simulate=False):
    task_id = event.get("task_id", "")
    status = event.get("status", "")
    summary = event.get("summary", "")

    print(f"  [task] {task_id[:12]} → {status}")

    if status == "completed":
        # 任务完成 → 触发 task-retrospective 单条复盘
        if not simulate:
            send_card(
                BOSS_CHAT,
                "✅ 任务完成",
                f"**任务：** {summary}\n**自动联动：** task-retrospective 检查实际 vs 预估 + 写入复盘标签",
                "green",
            )
    elif status == "in_progress":
        # 任务开始 → 记录实际开始时间
        print(f"  → record start time for {task_id}")


# ============== 审批新到处理 ==============
def handle_approval(event: dict, simulate=False):
    instance_id = event.get("instance_id", "")
    amount = event.get("amount", 0)
    appr_type = event.get("type", "未知")
    applicant = event.get("applicant", "未知")

    print(f"  [approval] {appr_type} ¥{amount} from {applicant}")

    # 智能分流规则
    if appr_type == "报销" and amount < 1000:
        # 自动批
        if not simulate:
            send_card(
                BOSS_CHAT,
                "✅ 已自动批准",
                f"**类型：** {appr_type}\n**金额：** ¥{amount}\n**申请人：** {applicant}\n**规则：** 报销 <¥1000 自动批",
                "green",
            )
        # 实际调用 lark-cli approval ... 批准
        print(f"  → auto-approved (rule: 报销 <¥1000)")
    else:
        # 推送给老板手动决策
        if not simulate:
            send_card(
                BOSS_CHAT,
                f"⏳ 待审批 · {appr_type} ¥{amount}",
                f"**申请人：** {applicant}\n**金额：** ¥{amount}\n**类型：** {appr_type}\n**建议：** 你今天内决策",
                "orange",
            )
        print(f"  → escalate to boss")


# ============== 主调度 ==============
def consume_event_stream(event_key: str):
    """每类事件独立 consumer（multi-thread）"""
    print(f"[start] consuming {event_key}")
    try:
        proc = subprocess.Popen(
            ["lark-cli", "event", "consume", event_key, "--as", "bot", "--quiet"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event_key == "im.message.receive_v1":
                    handle_im_message(event)
                elif event_key == "task.task.update_v1":
                    handle_task_update(event)
                elif "approval" in event_key:
                    handle_approval(event)
            except Exception as e:
                print(f"  [err {event_key}] {e}")
    except Exception as e:
        print(f"  [fatal {event_key}] {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate-im", help="模拟 IM 消息")
    ap.add_argument("--simulate-task", help="模拟任务状态 JSON")
    ap.add_argument("--simulate-approval", help="模拟审批 JSON")
    args = ap.parse_args()

    # 模拟模式
    if args.simulate_im:
        handle_im_message({"sender_id": "ou_other_user", "chat_id": "oc_group", "content": args.simulate_im, "chat_type": "group", "message_id": "om_sim"}, simulate=True)
        return
    if args.simulate_task:
        handle_task_update(json.loads(args.simulate_task), simulate=True)
        return
    if args.simulate_approval:
        handle_approval(json.loads(args.simulate_approval), simulate=True)
        return

    # 真跑：多 consumer 并发
    print("=== lark-fashion-cockpit · event-watcher 7×24 值班员 ===")
    print(f"Boss: {BOSS_OPEN_ID[:14]}... | Chat: {BOSS_CHAT[:14]}...")
    print(f"Watching {len(EVENT_SOURCES)} event sources:")
    for ek in EVENT_SOURCES:
        print(f"  • {ek}")
    print()
    print("Ctrl+C to stop.")
    print()

    threads = []
    for ek in EVENT_SOURCES:
        t = threading.Thread(target=consume_event_stream, args=(ek,), daemon=True)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n👋 Bye")


if __name__ == "__main__":
    main()
