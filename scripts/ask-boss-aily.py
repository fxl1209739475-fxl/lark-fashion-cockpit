"""老板分身 · 飞书 Aily 版

把 ask-boss.py 升级到飞书 Aily 平台。员工搜「老板娘 AI」就能在飞书里直接对话。
SKILL.md 详见 skills/boss-clone-aily/SKILL.md。
搭建手册详见 docs/AILY-SETUP.md。

用法：
  $env:AILY_APP_ID="spring_xxxxx"   # 老板娘在 https://aily.feishu.cn 创建应用后拿到
  python scripts/ask-boss-aily.py -q "DRS-0429 备多少件？"
  python scripts/ask-boss-aily.py -q "..." --reply-chat-id oc_xxx  # 把答案发飞书卡片
"""

import subprocess, json, os, sys, argparse, time

LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
AILY_APP_ID = os.environ.get("AILY_APP_ID", "")
DEFAULT_CHAT = "oc_45e0995a007db9d7f1859fa17b6566f6"


def lark_api(method, path, data=None, params=None, jq=None):
    """通过 lark-cli api 裸调飞书 OpenAPI"""
    cmd = [LARK_CLI, "api", method, path, "--as", "bot"]
    if data:
        cmd += ["--data", json.dumps(data, ensure_ascii=False)]
    if params:
        cmd += ["--params", json.dumps(params, ensure_ascii=False)]
    if jq:
        cmd += ["--jq", jq]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"lark-cli api failed: {(r.stderr or r.stdout)[:300]}")
    out = (r.stdout or "").strip()
    return json.loads(out) if out and out.startswith("{") else out


def create_session(channel_context: dict = None):
    payload = {}
    if channel_context:
        payload["channel_context"] = json.dumps(channel_context, ensure_ascii=False)
    res = lark_api("POST", "/open-apis/aily/v1/sessions", data=payload)
    return res["data"]["session"]["id"]


def send_message(session_id: str, content: str):
    return lark_api(
        "POST", f"/open-apis/aily/v1/sessions/{session_id}/messages",
        data={"content": content, "content_type": "MDX"},
    )


def trigger_run(session_id: str, app_id: str):
    res = lark_api(
        "POST", f"/open-apis/aily/v1/sessions/{session_id}/runs",
        data={"app_id": app_id},
    )
    return res["data"]["run"]["id"]


def get_run(session_id: str, run_id: str):
    return lark_api("GET", f"/open-apis/aily/v1/sessions/{session_id}/runs/{run_id}")


def list_messages(session_id: str):
    res = lark_api("GET", f"/open-apis/aily/v1/sessions/{session_id}/messages")
    return res["data"].get("messages", [])


def wait_for_answer(session_id: str, run_id: str, timeout: int = 60):
    """轮询直到 run.status='completed' 或超时"""
    started = time.time()
    while time.time() - started < timeout:
        res = get_run(session_id, run_id)
        status = res["data"]["run"]["status"]
        if status == "completed":
            return True
        if status in ("failed", "cancelled"):
            return False
        time.sleep(2)
    return False


def send_card(chat_id: str, question: str, answer: str):
    """把 Aily 回答发到飞书群"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "👑 老板娘 AI · 飞书 Aily 版"},
            "template": "purple",
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**问：** {question}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": answer}},
            {"tag": "note", "elements": [{"tag": "plain_text",
                "content": "由飞书 Aily 智能伙伴驱动 · 数据源 26_老板语料库 + 08_教训库"}]},
        ],
    }
    cmd = [LARK_CLI, "im", "+messages-send",
           "--chat-id", chat_id, "--msg-type", "interactive",
           "--content", json.dumps(card, ensure_ascii=False, separators=(',', ':'))]
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--question", required=True)
    ap.add_argument("--app-id", default=AILY_APP_ID, help="Aily app_id（spring_xxxxx）")
    ap.add_argument("--reply-chat-id", default=None)
    args = ap.parse_args()

    if not args.app_id:
        print("⚠ 未设置 AILY_APP_ID 环境变量。先按 docs/AILY-SETUP.md 在 Aily 平台搭好应用，拿到 app_id 后：")
        print('  $env:AILY_APP_ID="spring_xxxxx"')
        sys.exit(1)

    print(f"[1/4] 创建 Aily 会话 ...")
    sid = create_session()
    print(f"  → session_id={sid}")

    print(f"[2/4] 发送问题: {args.question}")
    send_message(sid, args.question)

    print(f"[3/4] 触发 Aily 运行 ...")
    run_id = trigger_run(sid, args.app_id)
    print(f"  → run_id={run_id}")

    print(f"[4/4] 等待 Aily 回复（最长 60s）...")
    if not wait_for_answer(sid, run_id):
        print("⚠ Aily 运行超时或失败")
        sys.exit(1)

    msgs = list_messages(sid)
    # 找最后一条 assistant 角色的消息
    answer = ""
    for m in reversed(msgs):
        if m.get("role") == "ASSISTANT" or m.get("sender", {}).get("identity") == "ASSISTANT":
            answer = m.get("content", "")
            break

    print("\n" + "=" * 50)
    print("【老板娘 AI · Aily】")
    print(answer)

    if args.reply_chat_id:
        send_card(args.reply_chat_id, args.question, answer)


if __name__ == "__main__":
    main()
