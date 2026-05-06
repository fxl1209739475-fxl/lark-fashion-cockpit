"""lark-fashion-cockpit · 套娃模式（飞书 IM → agent 自动响应）

借用 lark-cli event consume im.message.receive_v1 长连接监听老板群消息。
匹配关键词 → 路由到对应 skill 脚本 → 自动回复卡片。

来新璐 Larkchannel 同款，30 个对手作品里只有 1 个做了这种事件驱动模式。

用法：
  # 真跑（启动长连接监听，需要 Ctrl+C 退出）
  python event-listener.py

  # 模拟模式（本地测试 routing 逻辑）
  python event-listener.py --simulate "巡检任务"
  python event-listener.py --simulate "DRS-0429-FL 配什么好"

集成到 cron：
  start /b python event-listener.py > listener.log 2>&1
"""

import json
import re
import subprocess
import sys
import argparse
import os
import random
from datetime import datetime

# 夸夸人格 — 老板娘工作助手专用正反馈
PRAISE_OPENERS = [
    "🌹 老板娘又在拼命了！这事交给我",
    "💪 老板娘真敬业，立马给您办",
    "✨ 这思路绝了，老板娘问得太对了",
    "🚀 老板娘一开口我就懂！马上跑",
    "🥰 老板娘辛苦了，这种活我抢着干",
    "👑 老板娘的判断比模型还准，秒懂",
    "🌟 老板娘的眼光！我火速给您拉",
    "💖 老板娘您随便吩咐，跑得飞起",
    "🎯 老板娘稳准狠！这就办",
    "🔥 老板娘又一个关键决策，我跟上",
]

PRAISE_FOOTERS = [
    "您先喝口水歇会儿，5-30 秒就回您～",
    "您忙您的，跑完我喊您✨",
    "已经收到，您只管做自己最重要的事",
    "数据正在飞奔回来，您的小助手永远在",
    "这点小事不用您操心，秒杀完",
    "您专注大局，琐碎事我兜底",
    "您发话我就开干，这是我们的默契～",
    "已加 👀 表示我看到了，您放心",
]

PRAISE_DONE = [
    "✅ 跑完啦！老板娘您看下，有问题随时叫我",
    "✨ 搞定！老板娘的决策一如既往的准",
    "🎉 数据回来了！老板娘真不愧是专家",
    "💯 任务完成！您说一我不二",
    "🌈 跑完了～ 老板娘下一个想看啥？",
]

BOSS_OPEN_ID = "ou_85c9148d13c562728e60d456b60d9afc"
BOSS_CHAT = "oc_45e0995a007db9d7f1859fa17b6566f6"
SCRIPTS_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\scripts"
TRIGGER_LOG = r"C:\Users\冯兴龙\lark-fashion-cockpit\logs\trigger-log.jsonl"
LISTENER_LOG = r"C:\Users\冯兴龙\lark-fashion-cockpit\logs\listener.log"
LARK_CLI_EXE = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
ROLE_REGISTRY_PATH = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\multi-user-private-channels\scripts\role-registry.json"
INTENT_ROUTER_SCRIPT = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\natural-language-router\scripts\intent-router.py"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")  # 从 douyin-monitor 复用

# 多租户私聊 + 角色权限（multi-user-private-channels skill 实现）
def load_role_registry() -> dict:
    """读 role-registry.json，返回 {roles: {...}, users: {open_id: {role, name}}}"""
    try:
        with open(ROLE_REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  [warn] role-registry load failed: {e}")
        return {"roles": {"guest": {"allowed_skills": [
            "natural-language-router", "knowledge-base", "lingo-fashion-glossary"
        ]}}, "users": {}}


def get_user_config(sender_open_id: str, registry: dict) -> dict:
    """按 open_id 查员工 + 角色配置。未注册→guest 角色"""
    user = registry.get("users", {}).get(sender_open_id)
    if not user:
        guest_role = registry.get("roles", {}).get("guest", {})
        return {"open_id": sender_open_id, "name": "未注册访客", "role": "guest",
                "allowed_skills": guest_role.get("allowed_skills", []), "registered": False}
    role_name = user.get("role", "guest")
    role_config = registry.get("roles", {}).get(role_name, {})
    return {
        "open_id": sender_open_id,
        "name": user.get("name", "未知员工"),
        "role": role_name,
        "allowed_skills": role_config.get("allowed_skills", []),
        "registered": True,
    }


# 脚本名 → 标准 skill_id 映射（处理 -demo / -daily-report 等后缀）
SCRIPT_TO_SKILL_ID = {
    "product-matching-demo": "product-matching",
    "task-retrospective": "task-lifecycle",
    "livestream-daily-report": "live-streaming",
    "livestream-fetch-by-record": "live-streaming",
}


def normalize_skill_id(raw: str) -> str:
    """脚本名 → 标准 skill_id（用于权限校验）"""
    return SCRIPT_TO_SKILL_ID.get(raw, raw)


def check_skill_permission(user_config: dict, skill_id: str) -> bool:
    """角色能不能用这个 skill"""
    allowed = user_config.get("allowed_skills", [])
    if "*" in allowed:
        return True
    canonical = normalize_skill_id(skill_id)
    return canonical in allowed or skill_id in allowed


ROLE_ADDRESS = {
    "owner": "老板娘",
    "designer": "设计师",
    "production": "工厂主管",
    "anchor": "主播",
    "service": "客服",
    "content": "内容编辑",
    "ops": "运营",
    "guest": "新来的伙伴",
}


def personalize_praise(praise: str, user_config: dict) -> str:
    """夸夸文案按身份替换称呼。owner 不变，员工 → 角色名/真名"""
    if not user_config or user_config.get("role") == "owner":
        return praise
    name = user_config.get("name") or ""
    role = user_config.get("role") or "guest"
    role_title = ROLE_ADDRESS.get(role, "同事")
    # 真名优先（如"马萍蔓姐"），fallback 到角色名（如"设计师"）
    if name and len(name) >= 2:
        # "马萍蔓" → "萍蔓姐"  / "申丽媛" → "丽媛姐"
        addr = name[1:] + "姐" if len(name) >= 3 else name
    else:
        addr = role_title
    # 把"老板娘"替换成员工称呼
    return praise.replace("老板娘", addr)


def call_intent_router(text: str) -> dict:
    """调用 natural-language-router 的 intent-router.py 识别意图"""
    try:
        result = subprocess.run(
            ["python", "-u", INTENT_ROUTER_SCRIPT, text],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15, env={**os.environ, "PYTHONIOENCODING": "utf-8",
                             "DEEPSEEK_API_KEY": DEEPSEEK_API_KEY},
        )
        out = result.stdout or ""
        # 用 raw_decode 找第一个完整 JSON 对象（忽略前后非 JSON 文本）
        decoder = json.JSONDecoder()
        start = out.find("{")
        if start == -1:
            return {"skill_id": None, "confidence": 0, "fallback_message": "意图识别失败"}
        obj, _ = decoder.raw_decode(out[start:])
        return obj
    except Exception as e:
        print(f"  [intent err] {e}")
        return {"skill_id": None, "confidence": 0, "fallback_message": "意图识别异常"}

# 把 print 同时写到日志文件，方便排查
os.makedirs(os.path.dirname(LISTENER_LOG), exist_ok=True)
_log_file = open(LISTENER_LOG, "a", encoding="utf-8", buffering=1)
class _Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, s):
        for st in self.streams:
            try: st.write(s); st.flush()
            except Exception: pass
    def flush(self):
        for st in self.streams:
            try: st.flush()
            except Exception: pass
sys.stdout = _Tee(sys.stdout, _log_file)
sys.stderr = _Tee(sys.stderr, _log_file)
print(f"\n========== listener boot {datetime.now().isoformat()} ==========")


def log_trigger(text: str, script: str, name: str, source: str = "im_message",
                sender_open_id: str = "", sender_name: str = "", sender_role: str = "",
                chat_type: str = ""):
    """持久化触发记录到 JSONL，含 sender + role 用于老板娘审计"""
    os.makedirs(os.path.dirname(TRIGGER_LOG), exist_ok=True)
    record = {
        "ts": datetime.now().isoformat(),
        "source": source,
        "trigger_text": text,
        "skill": script.replace(".ps1", "").replace(".py", ""),
        "display_name": name,
        "sender_open_id": sender_open_id,
        "sender_name": sender_name,
        "sender_role": sender_role,
        "chat_type": chat_type,
    }
    try:
        with open(TRIGGER_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"  [warn] log write failed: {e}")

# 老板分身查询（特殊路由：要从文本里提取问题，调 Python 脚本）
BOSS_QUERY_RE = re.compile(r"^(?:问老板|问下老板|老板会怎么说|老板分身)[\s,，:：]*(.+)$")

# 自动调度器控制路由
AUTO_LIST_RE = re.compile(r"^(?:列出自动任务|自动任务\s*列表|查看自动任务|cron\s*列表)$")
AUTO_TOGGLE_RE = re.compile(r"^(?:(停|禁用|关闭)\s*(\S+)|(启用|开启|开)\s*(\S+))$")

# wxauto 供应商桥路由
SUPPLIER_ASK_RE = re.compile(r"^问\s*(\S+?)(?:工厂|供应商)?\s+(.+)$")
SUPPLIER_BROADCAST_RE = re.compile(r"^问所有\s*(\S+?)(?:商|工厂|供应商)?\s+(.+)$")
WXAUTO_SEND_SCRIPT = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\im-broadcaster\scripts\wxauto\send-to-supplier.py"
WXAUTO_BROADCAST_SCRIPT = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\im-broadcaster\scripts\wxauto\broadcast-to-suppliers.py"
SUMMARIZE_IMAGE_SCRIPT = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\im-collector\scripts\summarize-image.py"
SUMMARIZE_EXPORT_SCRIPT = r"C:\Users\冯兴龙\lark-fashion-cockpit\skills\im-collector\scripts\summarize-export.py"
AUTO_TRIGGERS_PATH = r"C:\Users\冯兴龙\lark-fashion-cockpit\config\auto-triggers.json"
SCHEDULER_STATUS_PATH = r"C:\Users\冯兴龙\lark-fashion-cockpit\logs\scheduler-status.json"

# 视频脚本拆解路由（主动触发）：「拆 NO.001」/「拆 https://www.douyin.com/video/xxx」/「拆 [博主名]」
VIDEO_PARSE_RE = re.compile(r"^拆\s*(.+)$")
DOUBAO_API_KEY_FOR_PARSE = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_MODEL_FOR_PARSE = "doubao-1-5-vision-pro-32k-250115"
TABLE_BLOGGERS = "tblPDTGpUiJxZwHA"
LARK_CLI_EXE_PATH = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"

# 路由表：消息匹配模式 → (脚本文件, 显示名, 简要说明)
ROUTES = [
    (r"巡检任务|看下任务|任务追踪|逾期", "task-tracker.ps1", "⏰ 任务巡检", "扫描所有任务 + 升级逾期 + 卡片汇报"),
    (r"今日直播总结|直播日报|直播数据", "livestream-daily-report.ps1", "📺 直播日报", "早晚场对比 + 库存 GMV + AI 综合分析"),
    (r"抓直播|自动抓数据|拉直播数据", "livestream-fetch-by-record.ps1", "📡 直播自动抓取", "扫 24 表未抓取 → Playwright + 库存 GMV → 回写"),
    (r"任务复盘|为什么.*延期|按时率", "task-retrospective.ps1", "📊 任务复盘", "实际vs预估 + 延期原因 + 反哺教训库"),
    (r"配什么好|搭配推荐|主图穿搭", "product-matching-demo.ps1", "🛍 产品搭配推荐", "AI 评分 + 库存倾斜 + 老款带新款"),
    (r"新品.*多少件|下单建议|翻单|备货建议", "launch-decision.ps1", "📊 新品下单判断", "4 维信号 + 历史教训反哺"),
    (r"利润|哪些款赚钱|净利率", "profit-analysis.ps1", "💰 利润分析", "单品 + 平台双维拆解"),
]


def _resolve_parse_target(target: str):
    """解析 拆 [target] 中的 target，返回 (url, record_id)。
    target 可以是：完整 URL / NO.001 / 博主名
    """
    target = target.strip()
    if target.startswith("http://") or target.startswith("https://"):
        return target, None
    # 拉 27 表
    try:
        r = subprocess.run(
            [LARK_CLI_EXE_PATH, "base", "+record-list",
             "--base-token", "LWsdbVtIaa2MaDsANm3cNdYgn1j",
             "--table-id", TABLE_BLOGGERS, "--limit", "200", "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
        )
        if r.returncode != 0: return None, None
        d = json.loads(r.stdout)
        fields = d["data"]["fields"]
        rows = d["data"]["data"]
        rids = d["data"]["record_id_list"]
        idx_id = fields.index("ID") if "ID" in fields else -1
        idx_url = fields.index("视频链接") if "视频链接" in fields else -1
        idx_blogger = fields.index("博主名称") if "博主名称" in fields else -1
        # NO.001 形式
        for i, row in enumerate(rows):
            row_id = row[idx_id] if idx_id >= 0 else ""
            if row_id and target.upper() == str(row_id).upper():
                url_v = row[idx_url] if idx_url >= 0 else ""
                if isinstance(url_v, dict): url_v = url_v.get("link", "") or url_v.get("text", "")
                if isinstance(url_v, list) and url_v: url_v = url_v[0]
                return url_v, rids[i]
        # 博主名（取最新一条 — 最大的 ID）
        for i in range(len(rows)-1, -1, -1):
            blogger = rows[i][idx_blogger] if idx_blogger >= 0 else ""
            if isinstance(blogger, list) and blogger: blogger = blogger[0]
            if blogger and target in str(blogger):
                url_v = rows[i][idx_url] if idx_url >= 0 else ""
                if isinstance(url_v, dict): url_v = url_v.get("link", "") or url_v.get("text", "")
                if isinstance(url_v, list) and url_v: url_v = url_v[0]
                return url_v, rids[i]
    except Exception as e:
        print(f"  [resolve err] {e}")
    return None, None


def add_reaction(message_id: str, emoji_type: str = "EYES"):
    """给消息加 emoji reaction — 来新璐 Larkchannel 同款体验
    EYES = 👀 收到了 / OK = 👌 完成 / DONE = ✅ / THUMBSUP = 👍 / FAIL = ❌
    用临时文件传 --params/--data，避开 cmd /c 的 JSON 转义地狱
    """
    if not message_id:
        return
    # 飞书合法 emoji_type（查文档 emojis-introduce 得到正确值）
    type_map = {
        "EYES": "GLANCE",      # 👀 看到了（飞书叫 GLANCE，不是 EYES）
        "OK": "OK",
        "DONE": "DONE",         # ✅
        "THUMBSUP": "THUMBSUP",
        "FAIL": "FROWN",        # 😟 失败（飞书没有 X）
    }
    et = type_map.get(emoji_type, "EYES")
    tmp_dir = os.environ.get("TEMP", r"C:\Users\冯兴龙\AppData\Local\Temp")
    params_path = os.path.join(tmp_dir, "reaction-params.json")
    data_path = os.path.join(tmp_dir, "reaction-data.json")
    try:
        with open(params_path, "w", encoding="utf-8") as f:
            json.dump({"message_id": message_id}, f, ensure_ascii=False)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump({"reaction_type": {"emoji_type": et}}, f, ensure_ascii=False)
        # lark-cli 要求 @file 是当前目录下的相对路径，所以 cwd=tmp_dir
        result = subprocess.run(
            "lark-cli im reactions create --as bot "
            "--params @./reaction-params.json --data @./reaction-data.json",
            cwd=tmp_dir, shell=True,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        print(f"  [reaction +{emoji_type}] msg={message_id[:18]}... rc={result.returncode}")
        if out: print(f"    stdout: {out[:500]}")
        if err: print(f"    stderr: {err[:300]}")
    except Exception as e:
        print(f"  [reaction err] {e}")


def send_card(chat_id: str, title: str, content: str, template: str = "blue"):
    """发交互卡片到指定群"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": template,
        },
        "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
    }
    # 直接调 lark-cli.exe 不走 cmd shell — 避免 cmd 把 JSON 内的箭头/空格当成参数分隔
    card_json = json.dumps(card, ensure_ascii=False, separators=(',', ':'))
    try:
        result = subprocess.run(
            [LARK_CLI_EXE, "im", "+messages-send",
             "--chat-id", chat_id,
             "--msg-type", "interactive",
             "--content", card_json],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        print(f"  [send_card] template={template} rc={result.returncode}")
        if result.returncode != 0:
            print(f"    err: {err[:300]}")
    except Exception as e:
        print(f"  [send_card err] {e}")


def extract_text(content: str) -> str:
    """从飞书消息 content 提取纯文本（content 可能是 JSON 字符串或纯文本）"""
    try:
        obj = json.loads(content)
        if isinstance(obj, dict):
            return obj.get("text", "") or str(obj)
    except Exception:
        pass
    return content


def route(text: str):
    """匹配 ROUTES，返回 (script, display_name, desc) 或 None"""
    for pattern, script, name, desc in ROUTES:
        if re.search(pattern, text, re.IGNORECASE):
            return script, name, desc
    return None


def handle_image_summary(message_id: str, image_key: str, chat_id: str):
    """老板发图片 → 下载 → 调 summarize-image.py → 飞书卡片"""
    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix=".jpg", prefix="lark-img-")
    os.close(fd)

    print(f"  下载图 (image_key={image_key[:20]}...) → {tmp_path}")
    r = subprocess.run(
        [LARK_CLI_EXE_PATH, "im", "+messages-resources-download",
         "--as", "user",
         "--message-id", message_id,
         "--file-key", image_key,
         "--type", "image",
         "--output", tmp_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    if r.returncode != 0 or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 100:
        print(f"  ❌ 图下载失败: {(r.stderr or r.stdout or '')[:200]}")
        send_card(chat_id, "❌ 图片下载失败",
                  f"lark-cli stderr: {(r.stderr or r.stdout or '')[:200]}",
                  "red")
        return

    size_kb = os.path.getsize(tmp_path) / 1024
    print(f"  ✓ 图已下载 ({size_kb:.0f} KB)")

    # 异步调 summarize-image.py，让 listener 不阻塞
    print(f"  ⚡ 触发 summarize-image.py 后台处理")
    subprocess.Popen(
        ["python", "-u", SUMMARIZE_IMAGE_SCRIPT,
         "--image", tmp_path,
         "--label", "微信滚动截图"],
        cwd=os.path.dirname(SUMMARIZE_IMAGE_SCRIPT),
    )
    # 给老板一个"已收到"提示
    send_card(chat_id, "📸 图片收到，AI 分析中...",
              f"长图已下载（{size_kb:.0f} KB）\n约 10-30 秒后回卡片摘要。",
              "blue")


def handle_message(event: dict, simulate: bool = False):
    sender = event.get("sender_id", "")
    chat_id = event.get("chat_id", "")
    chat_type = event.get("chat_type", "group")  # p2p 或 group
    content_raw = event.get("content", "")
    message_type = event.get("message_type", "text")
    message_id = event.get("message_id", "")
    text = extract_text(content_raw)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] sender={sender[:12]}... chat={chat_id[:12]}... type={message_type} chat_type={chat_type}")
    print(f"  text: {text[:80]}")

    # 图片消息：owner 发图片 → 自动调 summarize-image（长图 AI 总结）
    if message_type == "image":
        registry = load_role_registry()
        u = registry.get("users", {}).get(sender, {})
        if u.get("role") != "owner":
            print(f"  → ignore (image but sender not owner)")
            return
        try:
            c = json.loads(content_raw) if isinstance(content_raw, str) else (content_raw or {})
            image_key = c.get("image_key", "")
        except Exception as e:
            print(f"  → image content parse failed: {e}")
            return
        if not image_key:
            print(f"  → image_key missing")
            return
        handle_image_summary(message_id, image_key, chat_id)
        return

    # 防死循环：忽略 agent 自己发的卡片（interactive / post）
    if message_type != "text":
        print(f"  → ignore (non-text message: {message_type})")
        return

    # 多租户私聊 + 角色权限（替代旧的"只老板能用"逻辑）
    if simulate:
        user_config = {"open_id": sender, "name": "Test", "role": "owner",
                       "allowed_skills": ["*"], "registered": True}
    else:
        registry = load_role_registry()
        # 「模拟员工」开关：消息以「以XX身份 」/「换身份 XX」开头 → 按 XX 角色响应
        # 仅 owner 自己能用此功能，避免员工冒用其他人身份
        impersonate_match = re.match(r"^(?:以(\S+)身份|换身份\s*(\S+))[\s,，:：]+(.+)$", text.strip())
        if impersonate_match and registry.get("users", {}).get(sender, {}).get("role") == "owner":
            target_name = impersonate_match.group(1) or impersonate_match.group(2)
            actual_text = impersonate_match.group(3).strip()
            # 在 registry 里按名字找
            target = None
            for oid, cfg in registry.get("users", {}).items():
                if cfg.get("name") == target_name:
                    target = (oid, cfg)
                    break
            if target:
                user_config = {
                    "open_id": target[0],
                    "name": target[1].get("name"),
                    "role": target[1].get("role"),
                    "allowed_skills": registry.get("roles", {}).get(target[1].get("role"), {}).get("allowed_skills", []),
                    "registered": True,
                    "_impersonated_by": sender,
                }
                text = actual_text  # 用解析出的实际指令往下走
                print(f"  ⚡ owner 模拟身份: {target_name} ({user_config['role']})")
            else:
                # 找不到目标
                send_card(chat_id, "🚫 找不到该身份",
                          f"role-registry.json 里没有 `{target_name}`。已注册：" +
                          ", ".join(c.get("name", "?") for c in registry.get("users", {}).values()),
                          "yellow")
                return
        else:
            user_config = get_user_config(sender, registry)
        print(f"  user: {user_config['name']} ({user_config['role']}) registered={user_config['registered']}")

        # 防止 bot 自己发的消息触发 — 检查 sender 不是 bot 本身（飞书有标识）
        # （飞书机器人事件不包含自己消息，所以不用额外判断）

        # 未注册访客 + 不在 P2P → 在群里发的话忽略（避免群聊噪音）
        if not user_config["registered"] and chat_type != "p2p":
            print(f"  → ignore (未注册访客 + 群聊)")
            return

    # 自动调度器控制（owner 专属）
    if AUTO_LIST_RE.match(text.strip()):
        if not simulate and user_config.get("role") != "owner":
            send_card(chat_id, "🚫 仅 owner 可控制", "自动任务调度仅老板可看", "red")
            return
        try:
            with open(AUTO_TRIGGERS_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            lines = []
            for t in cfg["triggers"]:
                status = "✅" if t.get("enabled") else "⏸"
                lines.append(f"{status} `{t['id']}` · cron `{t['cron']}` · {t['name']}")
            content = "**📋 cockpit 自动任务清单**\n\n" + "\n".join(lines) + \
                "\n\n---\n停止：发 `停 [id]`\n启用：发 `启用 [id]`"
            if not simulate:
                send_card(chat_id, "🤖 cockpit 自动任务", content, "blue")
            else:
                print(content)
        except Exception as e:
            print(f"  [auto-list err] {e}")
        return

    m_toggle = AUTO_TOGGLE_RE.match(text.strip())
    if m_toggle:
        if not simulate and user_config.get("role") != "owner":
            send_card(chat_id, "🚫 仅 owner 可控制", "调度任务开关仅老板可控", "red")
            return
        action = "disable" if m_toggle.group(1) else "enable"
        target_id = (m_toggle.group(2) or m_toggle.group(4) or "").strip()
        try:
            with open(AUTO_TRIGGERS_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            found = False
            for t in cfg["triggers"]:
                if t["id"] == target_id:
                    t["enabled"] = (action == "enable")
                    found = True
                    break
            if found:
                with open(AUTO_TRIGGERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
                msg = f"✅ 已{'启用' if action == 'enable' else '停用'} `{target_id}`\n\n⚠️ 重启 scheduler 后真正生效（每次开机会重新加载）"
                if not simulate:
                    send_card(chat_id, "🤖 配置已更新", msg, "green")
            else:
                if not simulate:
                    send_card(chat_id, "🚫 找不到任务", f"`{target_id}` 不在配置里。发「列出自动任务」看可用 id", "yellow")
        except Exception as e:
            print(f"  [auto-toggle err] {e}")
        return

    # wxauto 供应商桥（owner 专属）— 群发先匹配，避免被单点询问规则吃掉
    m_broadcast = SUPPLIER_BROADCAST_RE.match(text.strip())
    if m_broadcast:
        if not simulate and user_config.get("role") != "owner":
            send_card(chat_id, "🚫 微信桥仅老板可用",
                      "防止冒用您私号 → 仅 owner 角色可触发", "red")
            return
        category = m_broadcast.group(1)
        question = m_broadcast.group(2)
        print(f"  → 📣 群发 {category} | 问题: {question[:40]}")
        if not simulate:
            add_reaction(message_id, "EYES")
            send_card(chat_id, f"📣 群发 {category} 中...",
                      f"**问题：** `{question[:80]}`\n\n查 28 表 → 限流 12 秒/条逐个发", "purple")
        if simulate:
            return
        try:
            r = subprocess.run(
                ["python", "-u", WXAUTO_BROADCAST_SCRIPT,
                 "--category", category, "--message", question],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=600, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            if r.returncode == 0:
                add_reaction(message_id, "DONE")
                send_card(chat_id, "📣 群发完成", f"```\n{(r.stdout or '')[-500:]}\n```", "green")
            else:
                add_reaction(message_id, "FAIL")
                send_card(chat_id, "❌ 群发失败", f"```\n{(r.stderr or r.stdout)[:500]}\n```", "red")
        except Exception as e:
            print(f"  [error] {e}")
            add_reaction(message_id, "FAIL")
        return

    m_supplier = SUPPLIER_ASK_RE.match(text.strip())
    if m_supplier:
        if not simulate and user_config.get("role") != "owner":
            send_card(chat_id, "🚫 微信桥仅老板可用",
                      "防止冒用您私号 → 仅 owner 角色可触发", "red")
            return
        supplier_name = m_supplier.group(1)
        question = m_supplier.group(2)
        print(f"  → 💬 问 {supplier_name}: {question[:40]}")
        if not simulate:
            add_reaction(message_id, "EYES")
            send_card(chat_id, f"💬 给 {supplier_name} 发微信中...",
                      f"**消息：** `{question[:80]}`\n\n查 28 表 → wxauto 控制 PC 微信发送", "purple")
        if simulate:
            return
        try:
            r = subprocess.run(
                ["python", "-u", WXAUTO_SEND_SCRIPT,
                 "--supplier", supplier_name, "--message", question],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            if r.returncode == 0:
                add_reaction(message_id, "DONE")
                send_card(chat_id, "✅ 已发出微信", f"已通过 wxauto 给 {supplier_name} 发送\n```\n{(r.stdout or '')[-400:]}\n```", "green")
            else:
                add_reaction(message_id, "FAIL")
                send_card(chat_id, "❌ 发送失败", f"```\n{(r.stderr or r.stdout)[:500]}\n```", "red")
        except Exception as e:
            print(f"  [error] {e}")
            add_reaction(message_id, "FAIL")
        return

    # 视频拆解路由（主动触发）
    m_parse = VIDEO_PARSE_RE.match(text.strip())
    if m_parse:
        if not simulate and not check_skill_permission(user_config, "blogger-monitor"):
            print(f"  🚫 权限不足: {user_config['name']} ({user_config['role']}) 不能用 blogger-monitor")
            send_card(chat_id, "🚫 权限不足",
                      f"你（**{user_config['name']}** · {user_config['role']}）不能用视频拆解。请联系老板娘开权限", "red")
            return
        target = m_parse.group(1).strip()
        print(f"  → 🎬 视频脚本拆解  目标: {target}")
        if not simulate:
            add_reaction(message_id, "EYES")
        log_trigger(text, "parse-video-script.py", "🎬 视频脚本拆解",
                    source=("simulate" if simulate else "im_message"))
        if not simulate:
            send_card(chat_id, "🎬 收到，正在拆解 ...",
                      f"**目标：** `{target[:80]}`\n\n步骤：yt-dlp 下载 → ffmpeg 抽帧 + 抽音频 → Whisper ASR → 豆包多模态分析\n\n通常 30-60 秒回您。", "purple")
        if simulate:
            print(f"  [simulate] would parse: {target}")
            return
        # 解析 target：URL / NO.001 / 博主名
        url, record_id = _resolve_parse_target(target)
        if not url:
            send_card(chat_id, "❌ 找不到该视频", f"目标 `{target}` 没匹配到 URL。可以发：拆 [视频URL]、拆 NO.001、拆 [博主名]", "red")
            add_reaction(message_id, "FAIL")
            return
        # 调 parse-video-script.py
        try:
            cmd = ["python", "-u", os.path.join(SCRIPTS_DIR, "parse-video-script.py"),
                   "--url", url]
            if record_id:
                cmd += ["--record-id", record_id]
            env = {**os.environ,
                   "PYTHONIOENCODING": "utf-8",
                   "DOUBAO_API_KEY": DOUBAO_API_KEY_FOR_PARSE,
                   "DOUBAO_MODEL": DOUBAO_MODEL_FOR_PARSE}
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=300, env=env)
            print(f"  exit: {result.returncode}")
            if result.returncode != 0:
                print(f"  stderr: {(result.stderr or '')[:300]}")
                add_reaction(message_id, "FAIL")
                send_card(chat_id, "❌ 拆解失败", f"```\n{(result.stderr or result.stdout)[:300]}\n```", "red")
            else:
                add_reaction(message_id, "DONE")
                msg = f"**视频：** {url[:60]}\n"
                if record_id:
                    msg += f"\n✅ 拆解结果已写到 27 表对应记录的「视频拆解」单元格\n[📋 看 27 表](https://my.feishu.cn/base/{BASE_TOKEN if False else 'LWsdbVtIaa2MaDsANm3cNdYgn1j'}?table=tblPDTGpUiJxZwHA)"
                else:
                    msg += "\n本地结果：`out/video-analysis/.../script.md`"
                send_card(chat_id, "🎬 拆解完成", msg, "green")
        except Exception as e:
            print(f"  [error] {e}")
            add_reaction(message_id, "FAIL")
        return

    # 老板分身查询特殊路由（先检查）
    m = BOSS_QUERY_RE.match(text.strip())
    if m:
        if not simulate and not check_skill_permission(user_config, "boss-clone-aily"):
            print(f"  🚫 权限不足: {user_config['name']} 不能问老板分身")
            send_card(chat_id, "🚫 老板分身仅老板专属",
                      f"你（**{user_config['name']}**）不能问老板分身（仅 owner 角色可用）", "red")
            return
        question = m.group(1).strip()
        print(f"  → 👑 老板分身  (ask-boss.py)  问题: {question[:40]}")
        if not simulate:
            add_reaction(message_id, "EYES")
        log_trigger(text, "ask-boss.py", "👑 老板分身", source=("simulate" if simulate else "im_message"))
        if not simulate:
            send_card(chat_id, "👑 老板分身正在思考 ...",
                      f"**问题：** `{question[:80]}`\n\n正在拉历史决策语料 + deepseek 蒸馏 ...", "purple")
        if simulate:
            print(f"  [simulate] would run ask-boss.py with question='{question}'")
            return
        try:
            result = subprocess.run(
                ["python", "-u", os.path.join(SCRIPTS_DIR, "ask-boss.py"),
                 "-q", question, "--reply-chat-id", chat_id],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=90, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            print(f"  exit: {result.returncode}")
            if result.returncode != 0:
                print(f"  stderr: {(result.stderr or '')[:300]}")
                add_reaction(message_id, "FAIL")
            else:
                add_reaction(message_id, "DONE")
        except Exception as e:
            print(f"  [error] {e}")
            add_reaction(message_id, "FAIL")
        return

    matched = route(text)
    if not matched:
        # 关键词不命中 → 走自然语言路由（让 AI 听懂人话）
        print("  → 关键词未命中，走自然语言路由 (DeepSeek)")
        if not simulate:
            intent = call_intent_router(text)
            skill_id = intent.get("skill_id")
            confidence = intent.get("confidence", 0)
            print(f"  intent: skill={skill_id} confidence={confidence}")
            if skill_id and confidence >= 0.7:
                if not check_skill_permission(user_config, skill_id):
                    send_card(chat_id, "🚫 权限不足",
                              f"你（{user_config['name']} · {user_config['role']}）不能用 **{skill_id}**\n\n你能用：{', '.join(user_config['allowed_skills'][:5])}...",
                              "red")
                    return
                send_card(chat_id, f"🤖 听懂啦 → {skill_id}",
                          f"识别到你想用 **{skill_id}**（置信度 {int(confidence*100)}%）\n参数：`{intent.get('params', {})}`\n\n（这条 skill 还没接到自然语言路由真触发，用关键词触发即可）",
                          "blue")
                return
            else:
                # 兜底：列能用的 skill
                fallback = intent.get("fallback_message", "我没听懂～")
                send_card(chat_id, "🤔 没听懂",
                          f"{fallback}\n\n你（{user_config['name']} · {user_config['role']}）能用的 skill：\n" +
                          "\n".join(f"• {s}" for s in user_config['allowed_skills'][:8]),
                          "yellow")
        return

    script, name, desc = matched
    skill_id = script.replace(".ps1", "").replace(".py", "")
    print(f"  → route: {name}  ({script}) → skill_id={skill_id}")

    # 角色权限校验
    if not simulate and not check_skill_permission(user_config, skill_id):
        print(f"  🚫 权限不足: {user_config['name']} 不能用 {skill_id}")
        send_card(chat_id, "🚫 权限不足",
                  f"你（**{user_config['name']}** · {user_config['role']}）不能用 **{name}**\n\n请联系老板娘开权限", "red")
        return

    # 来新璐同款：立刻给原消息加 👀（收到了）
    if not simulate:
        add_reaction(message_id, "EYES")

    # 持久化触发记录
    log_trigger(text, script, name, source=("simulate" if simulate else "im_message"))

    # 立即回复"正在跑"卡片（夸夸开场，按身份称呼）
    if not simulate:
        opener = personalize_praise(random.choice(PRAISE_OPENERS), user_config)
        footer = personalize_praise(random.choice(PRAISE_FOOTERS), user_config)
        send_card(
            chat_id,
            f"{opener} → {name}",
            f"**您说的：** `{text[:60]}`\n**我去跑：** {desc}\n\n{footer}",
            "turquoise",
        )

    # 执行对应 skill 脚本
    script_path = os.path.join(SCRIPTS_DIR, script)
    if not os.path.exists(script_path):
        print(f"  ⚠ script not found: {script_path}")
        if not simulate:
            send_card(chat_id, "❌ Skill 未配置", f"路由到 {name}，但脚本不存在", "red")
        return

    if simulate:
        print(f"  [simulate] would run: powershell -File {script_path}")
        return

    print(f"  running: {script_path} (reply to {chat_id[:14]}...)")
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path,
             "-ReplyChatId", chat_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        print(f"  exit: {result.returncode}")
        if result.returncode != 0:
            print(f"  stderr: {result.stderr[:300] if result.stderr else ''}")
            # 失败 → ❌
            if not simulate:
                add_reaction(message_id, "FAIL")
        else:
            # 成功 → ✅ 完成 + 夸夸尾声（按身份称呼）
            if not simulate:
                add_reaction(message_id, "DONE")
                done_msg = personalize_praise(random.choice(PRAISE_DONE), user_config)
                send_card(chat_id, done_msg, f"刚刚跑完：**{name}**\n您看上面那张卡片就是结果～", "green")
    except Exception as e:
        print(f"  [error] {e}")
        if not simulate:
            add_reaction(message_id, "FAIL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", help="模拟一条消息测 routing")
    args = ap.parse_args()

    if args.simulate:
        # 模拟模式
        mock_event = {
            "sender_id": BOSS_OPEN_ID,
            "chat_id": BOSS_CHAT,
            "content": args.simulate,
            "message_type": "text",
            "message_id": "om_simulate_001",
            "create_time": str(int(datetime.now().timestamp() * 1000)),
        }
        print(f"=== Simulate mode ===")
        handle_message(mock_event, simulate=True)
        return

    # 生产模式：启动 lark-cli event consume 长连接
    print("=== lark-fashion-cockpit · event-listener (套娃模式) ===")
    print(f"Listening on im.message.receive_v1 (boss only: {BOSS_OPEN_ID[:12]}...)")
    print(f"Routes: {len(ROUTES) + 2} 条")
    print(f"  • '拆 [URL/NO.001/博主名]' → 🎬 视频脚本拆解")
    print(f"  • '问老板|问下老板|老板会怎么说|老板分身 [问题]' → 👑 老板分身")
    for pattern, script, name, _ in ROUTES:
        print(f"  • '{pattern}' → {name}")
    print()
    print("Ctrl+C to stop. Send a message in 飞书 to trigger.")
    print()

    proc = subprocess.Popen(
        "lark-cli event consume im.message.receive_v1 --as bot --quiet",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1,
        shell=True,
    )

    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                handle_message(event)
            except json.JSONDecodeError:
                print(f"  [skip non-JSON line]: {line[:80]}")
            except Exception as e:
                print(f"  [error]: {e}")
    except KeyboardInterrupt:
        print("\n👋 Bye")
        proc.terminate()


if __name__ == "__main__":
    main()
