"""企业微信 → 给客户（个人微信好友）发消息

走两条路径：
  1. 应用消息（发给企微员工自己）—— /cgi-bin/message/send
  2. 客户联系消息（发给客户的微信）—— /cgi-bin/externalcontact/add_msg_template
     注意：这是群发模板，每客户每月 ≤ 4 条。如果想超过这个限制，
     必须客户先主动给你发消息触发"48h 服务窗口"，期间用 message/send 无限。

用法：
  python send-msg.py --to wYourSelfWecomId --text "测试消息"     # 发给员工自己
  python send-msg.py --to-customer ext_xxx --text "..."          # 发给单客户（需 48h 窗口）
  python send-msg.py --customer-broadcast ext1,ext2 --text "..." # 群发（每月 ≤ 4 条）
"""

import os, sys, argparse, json, importlib.util

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location("wecom_client", os.path.join(os.path.dirname(__file__), "wecom-client.py"))
wc_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc_mod)
WecomClient = wc_mod.WecomClient


def send_to_employee(c: WecomClient, agent_id: int, touser: str, text: str):
    """应用消息（给企微员工自己 / 团队同事发）"""
    r = c.post("message/send", {
        "touser": touser,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {"content": text},
    })
    return r


def send_to_customer_in_window(c: WecomClient, agent_id: int, external_userid: str, text: str):
    """客户主动咨询触发的 48h 窗口内发消息（无限制）

    需要先有客户主动消息记录。如果 48h 窗口已过期，调用会失败。
    """
    # 实际上发给客户走的也是 message/send 但 touser 是 external_userid
    r = c.post("message/send", {
        "touser": external_userid,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {"content": text},
    })
    return r


def broadcast_to_customers(c: WecomClient, sender: str, external_userids: list, text: str):
    """群发模板（每客户每月 ≤ 4 条）"""
    r = c.post("externalcontact/add_msg_template", {
        "sender": sender,
        "external_userid": external_userids,
        "text": {"content": text},
    })
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", help="企微员工 ID")
    ap.add_argument("--to-customer", help="单个客户 external_userid（48h 窗口内）")
    ap.add_argument("--customer-broadcast", help="多个客户 external_userid 逗号分隔（群发模板，每月 ≤ 4）")
    ap.add_argument("--sender", help="群发的发起员工 ID（仅 --customer-broadcast 时需要）")
    ap.add_argument("--text", required=True)
    ap.add_argument("--agent-id", type=int, default=int(os.environ.get("WECOM_AGENT_ID", "1000002")))
    args = ap.parse_args()

    c = WecomClient(secret_kind="agent")

    if args.to:
        print(f"=== 发给员工 {args.to} ===")
        r = send_to_employee(c, args.agent_id, args.to, args.text)
    elif args.to_customer:
        print(f"=== 发给客户 {args.to_customer}（48h 窗口）===")
        r = send_to_customer_in_window(c, args.agent_id, args.to_customer, args.text)
    elif args.customer_broadcast:
        if not args.sender:
            print("❌ --customer-broadcast 必须配 --sender")
            sys.exit(1)
        ext_list = [x.strip() for x in args.customer_broadcast.split(",") if x.strip()]
        print(f"=== 群发 {len(ext_list)} 客户（模板） ===")
        # 客户群发要切到 contact secret
        c_contact = WecomClient(secret_kind="contact")
        r = broadcast_to_customers(c_contact, args.sender, ext_list, args.text)
    else:
        print("❌ 必须指定 --to / --to-customer / --customer-broadcast 之一")
        sys.exit(1)

    if r.get("errcode") == 0:
        print(f"✓ 发送成功: {json.dumps(r, ensure_ascii=False)}")
    else:
        print(f"✗ 发送失败: {json.dumps(r, ensure_ascii=False)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
