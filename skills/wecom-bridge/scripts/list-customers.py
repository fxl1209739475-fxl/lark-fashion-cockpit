"""列出当前账号的所有"客户"（外部联系人）→ 输出名单

用法：
  python list-customers.py
  python list-customers.py --userid wYourSelfWecomId
"""

import os, sys, argparse, json
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 同目录 import
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("wecom_client", os.path.join(os.path.dirname(__file__), "wecom-client.py"))
wc_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc_mod)
WecomClient = wc_mod.WecomClient


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--userid", help="指定企微员工 ID（不填则列出所有员工的客户聚合）")
    args = ap.parse_args()

    c = WecomClient(secret_kind="contact")

    # 1. 拿到能用客户联系的成员列表
    print("[1/3] 拿可用客户联系功能的员工列表...")
    res = c.get("externalcontact/get_follow_user_list")
    if res.get("errcode") != 0:
        print(f"❌ {res}")
        sys.exit(1)
    follow_users = res.get("follow_user", [])
    print(f"  可用员工 {len(follow_users)} 人: {follow_users}")

    targets = [args.userid] if args.userid else follow_users

    # 2. 遍历每个员工拿其客户列表
    print(f"\n[2/3] 遍历 {len(targets)} 个员工，拿客户列表...")
    all_externals = {}  # userid -> [external_userid]
    for uid in targets:
        r = c.get("externalcontact/list", {"userid": uid})
        if r.get("errcode") != 0:
            print(f"  ⚠ 员工 {uid}: {r}")
            continue
        ext_list = r.get("external_userid", [])
        all_externals[uid] = ext_list
        print(f"  员工 {uid}: {len(ext_list)} 个客户")

    # 3. 拿每个客户的详情
    print(f"\n[3/3] 拉客户详情...")
    print(f"\n{'员工':16} {'客户external_userid':40} {'昵称':20} {'类型'}")
    print("-" * 100)
    for uid, exts in all_externals.items():
        for ext_id in exts[:30]:  # 每个员工最多取 30 个详情，防 API 配额
            d = c.get("externalcontact/get", {"external_userid": ext_id})
            if d.get("errcode") != 0:
                print(f"{uid:16} {ext_id:40} ⚠ 拉详情失败: {d.get('errmsg','')}")
                continue
            ec = d.get("external_contact", {})
            nick = ec.get("name", "?")
            tp = "微信用户" if ec.get("type") == 1 else "企微账号"
            print(f"{uid:16} {ext_id:40} {nick:20} {tp}")


if __name__ == "__main__":
    main()
