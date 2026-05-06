"""拉客户历史会话 → 喂 DEEPSEEK 总结 → 飞书卡片

⚠ 这条路径需要企业微信"会话存档"（msgaudit）功能：
  - 仅认证企业可开通（不需付费但需要营业执照认证）
  - 客户需要授权（在客户的微信对话顶部会显示"会话存档已开启"）
  - 数据通过会话存档 SDK（C++/Python 包）拉取，不是普通 HTTP API

未实测，**仅 spec**。当用户认证企业并开通会话存档后，按下面流程实现：

1. 注册企业 → 认证 → 开通"会话存档"功能
2. 在企业微信后台下载会话存档 SDK（finance.dll / libWeWorkFinanceSdk.so）
3. 拿存档 secret + 公钥
4. 调 SDK 拉取加密的聊天记录 → 解密 → 结构化
5. 按 hours 过滤 → DEEPSEEK 总结 → 飞书卡片

API 路径：
  - msgaudit/check_single_agree    检查客户是否同意存档
  - msgaudit/get_permit_user_list  拿允许存档的员工列表
  - GetChatData (SDK 调用)         拉加密消息流

替代路径（未认证企业）：
  - 不能拉历史（API 限制）
  - 但可以**实时监听**自己发的消息 + 客户回的消息（在 48h 窗口内）
  - 用 wecom-client 监听消息回调 webhook

用法（spec）：
  python sync-history.py --customer wm_xxx --hours 72 --no-send
"""

import os, sys, argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer", help="客户 external_userid")
    ap.add_argument("--hours", type=int, default=72)
    ap.add_argument("--no-send", action="store_true")
    args = ap.parse_args()

    print("⚠ 本脚本是 spec / placeholder 实现")
    print("   原因：企业微信会话存档功能需要：")
    print("   1. 企业认证（需营业执照）")
    print("   2. 客户授权同意会话存档")
    print("   3. 下载会话存档 SDK（C++/Python 包）")
    print()
    print("   当前 cockpit 不强制实现此能力，仅作为 wecom-bridge skill 的扩展点保留。")
    print()
    print("   如果你已有会话存档环境，本脚本应实现：")
    print("   - 调 GetChatData (SDK) 拉加密消息流")
    print("   - 用企业 私钥 解密 random_key + AES 解密 message")
    print("   - 按 hours 过滤")
    print("   - 调 DEEPSEEK 总结")
    print("   - 发飞书卡片")
    print()
    print("   想用替代方案：")
    print("   - 个人微信好友 → 用 ../../wechat-monitor/scripts/summarize-image.py（飞书滚动截屏 + AI）")
    print("   - 客户企微会话 → 让客户主动发一条消息触发 48h 窗口，期间用 send-msg.py 双向沟通")


if __name__ == "__main__":
    main()
