"""扫描某个微信联系人 / 群的历史消息 → AI 总结过去 N 小时

视觉 RPA 路线（微信 4.x mmui 框架不支持 UIA，所以全靠 DOUBAO 视觉 + bbox 定位）：
  1. 截图 → DOUBAO 返回搜索框 bbox → 点击中心
  2. 粘贴目标名
  3. 截图 → DOUBAO 找搜索结果里目标项的 bbox → 点击
  4. 截图 → DOUBAO 验证当前聊天对象名
  5. 滚屏读消息 → DOUBAO 内容总结
  6. ESC 退出

用法：
  python scan-person.py --name "MM"
  python scan-person.py --name "MM" --hours 24 --scrolls 6
"""

import os, sys, json, base64, argparse, subprocess, time, io, re, hashlib
from datetime import datetime, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pygetwindow as gw
import pyautogui
import pyperclip
import numpy as np
import cv2
import win32gui
import win32con
import win32process
import win32ui
import ctypes
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

DEBUG_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\out\wechat-snapshots"


def capture_hwnd_via_printwindow(hwnd) -> Image.Image:
    """用 Win32 PrintWindow API 直接抓窗口内容 — 即使被其他窗口遮挡也能拿到完整像素"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    if w <= 0 or h <= 0:
        return None
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(bitmap)
    # PW_RENDERFULLCONTENT = 2 (Win 8.1+，捕获 Chromium/Qt/UWP 等需要的全内容渲染)
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                            bmpstr, "raw", "BGRX", 0, 1)
    win32gui.DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return img if result else None


def shot_window(win) -> tuple:
    """截窗口区域（Qt 微信 PrintWindow 无效，只能屏幕截图，要求微信前台无遮挡）"""
    img = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), img


def shot_to_b64_jpeg(img, quality=85, max_side=None) -> str:
    """转 JPEG base64，可选缩小到长边 max_side"""
    if max_side:
        w, h = img.size
        m = max(w, h)
        if m > max_side:
            ratio = max_side / m
            from PIL import Image as _PIL
            img = img.resize((int(w * ratio), int(h * ratio)), _PIL.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def doubao_call(prompt: str, img, max_tokens=400, temperature=0.0) -> dict:
    """调 DOUBAO 视觉，返回 JSON 解析后的 dict"""
    if not DOUBAO_API_KEY:
        raise RuntimeError("缺 DOUBAO_API_KEY")
    b64 = shot_to_b64_jpeg(img)
    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    resp = client.chat.completions.create(
        model=DOUBAO_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def bbox_to_screen_center(bbox_pct: dict, win) -> tuple:
    """bbox 百分比 → 屏幕绝对像素中心"""
    x1 = bbox_pct["x1"] * win.width
    y1 = bbox_pct["y1"] * win.height
    x2 = bbox_pct["x2"] * win.width
    y2 = bbox_pct["y2"] * win.height
    cx = win.left + int((x1 + x2) / 2)
    cy = win.top + int((y1 + y2) / 2)
    return cx, cy


WECHAT_TITLES = ("微信", "Weixin", "WeChat")


def find_wechat_hwnd_all():
    """找所有微信窗口（含隐藏/托盘），返回 [{hwnd, title, class, visible, iconic, rect}]"""
    found = []
    def cb(hwnd, _):
        try:
            t = win32gui.GetWindowText(hwnd) or ""
            cls = win32gui.GetClassName(hwnd) or ""
        except Exception:
            return True
        if t in WECHAT_TITLES or "mmui::MainWindow" in cls or "WeChatMainWndForPC" in cls:
            try:
                rect = win32gui.GetWindowRect(hwnd)
            except Exception:
                rect = None
            found.append({
                "hwnd": hwnd, "title": t, "class": cls,
                "visible": bool(win32gui.IsWindowVisible(hwnd)),
                "iconic": bool(win32gui.IsIconic(hwnd)),
                "rect": rect,
            })
        return True
    win32gui.EnumWindows(cb, None)
    return found


SWP_FLAGS = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW


def force_foreground(hwnd):
    """AttachThreadInput trick: 把脚本线程和当前前台窗口线程焊接在一起，绕过 Win11 抢焦点限制"""
    try:
        fore_hwnd = win32gui.GetForegroundWindow()
        if fore_hwnd == hwnd:
            return
        fore_tid, _ = win32process.GetWindowThreadProcessId(fore_hwnd) if fore_hwnd else (0, 0)
        cur_tid = ctypes.windll.kernel32.GetCurrentThreadId()

        attached = False
        if fore_tid and fore_tid != cur_tid:
            attached = ctypes.windll.user32.AttachThreadInput(cur_tid, fore_tid, True)

        # Alt key trick
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x12, 0, 0x0002, 0)

        # 取消最小化
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception:
            pass
        # SwitchToThisWindow（最强 API）
        try:
            ctypes.windll.user32.SwitchToThisWindow(hwnd, True)
        except Exception:
            pass
        # 顶置
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, SWP_FLAGS)
        except Exception:
            pass
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass

        if attached:
            ctypes.windll.user32.AttachThreadInput(cur_tid, fore_tid, False)
    except Exception as e:
        print(f"  force_foreground 异常: {e}")


def is_window_foreground(hwnd) -> bool:
    """检测 hwnd 当前是否在最前台"""
    try:
        return win32gui.GetForegroundWindow() == hwnd
    except Exception:
        return False


def unpin_topmost(hwnd):
    """操作完取消 TOPMOST，恢复正常 z-order"""
    try:
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass


def wake_wechat_from_tray():
    """从托盘/隐藏/最小化呼出微信主窗口，强制置顶；返回 (success, hwnd)"""
    wins = find_wechat_hwnd_all()
    if not wins:
        return False, None
    target = next((w for w in wins if w["visible"] and not w["iconic"]), None) or wins[0]
    hwnd = target["hwnd"]

    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.2)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    time.sleep(0.2)
    force_foreground(hwnd)
    time.sleep(0.4)
    force_foreground(hwnd)
    time.sleep(0.4)
    return is_window_foreground(hwnd), hwnd


def ensure_wechat_foreground(timeout_sec: int = 12):
    """微信必须连续 2 秒在最前台才认为真前台（避免 wake API 瞬时假阳性）"""
    wins = find_wechat_hwnd_all()
    if not wins:
        raise RuntimeError("找不到微信主窗口")
    hwnd = next((w["hwnd"] for w in wins if w["visible"] and not w["iconic"]), wins[0]["hwnd"])

    print(f"\n  ⚡ 请按 Alt+Tab 切到微信，让它**保持在最前台、不被遮挡**")
    print(f"     倒计时 {timeout_sec}s（检测到微信稳定前台 2 秒立即开始）")

    REQUIRED_STREAK = 4   # 0.5s × 4 = 连续 2 秒
    streak = 0
    for tick in range(timeout_sec * 2):
        if is_window_foreground(hwnd):
            streak += 1
            if streak >= REQUIRED_STREAK:
                print(f"\n  ✓ 微信稳定前台，开始操作")
                return True
        else:
            streak = 0
        sec_left = timeout_sec - tick // 2
        print(f"     剩 {sec_left}s  连续前台 {streak * 0.5:.1f}s   ", end="\r", flush=True)
        time.sleep(0.5)
    print()
    raise RuntimeError("微信始终未保持前台 → 取消操作。请手动 Alt+Tab 切到微信再重跑。")


def find_wechat_window():
    """先用 pygetwindow 找可见微信；找不到就用 win32 唤起再找"""
    for w in gw.getAllWindows():
        if (w.title or "") in WECHAT_TITLES:
            return w
    print("  (微信不在前台，尝试从托盘唤起...)")
    ok, _ = wake_wechat_from_tray()
    if ok or not ok:  # 不管成不成功都再 list 一次（窗口可能变可见了）
        time.sleep(0.5)
        for w in gw.getAllWindows():
            if (w.title or "") in WECHAT_TITLES:
                return w
    return None


def activate_wechat(win):
    """确保微信置顶到最前台。失败则提示用户手动 Alt+Tab"""
    ensure_wechat_foreground(timeout_sec=8)
    time.sleep(0.3)


def step_locate_search_box(win, save_debug=False):
    """步骤 1：找搜索框 bbox 并点击"""
    print("  [1] 截图找搜索框...")
    _, img = shot_window(win)
    if save_debug:
        img.save(os.path.join(DEBUG_DIR, f"step1-find-search-{int(time.time())}.png"))

    prompt = """这是 PC 微信主窗口截图。请找到**搜索框**：
- 位置：窗口左上角，群列表上方
- 特征：灰色长条 + 放大镜图标 + "搜索"灰色占位文字
- 它跟左侧群列表同宽

返回搜索框的 bounding box（百分比，0-1 之间小数）：
{"x1": 左边x/图片宽, "y1": 顶边y/图片高, "x2": 右边x/图片宽, "y2": 底边y/图片高, "found": true}

如果没找到：{"found": false}

只返回 JSON，不要 markdown 代码块。"""

    res = doubao_call(prompt, img, max_tokens=200)
    if not res.get("found"):
        raise RuntimeError("DOUBAO 没找到搜索框")
    cx, cy = bbox_to_screen_center(res, win)
    print(f"      搜索框 bbox: ({res['x1']:.3f}, {res['y1']:.3f}, {res['x2']:.3f}, {res['y2']:.3f}) → 屏幕中心 ({cx}, {cy})")
    pyautogui.click(cx, cy)
    time.sleep(0.5)


def step_input_name(name: str):
    """步骤 2：清空 + 粘贴目标名"""
    print(f"  [2] 输入 {name!r}...")
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    time.sleep(0.1)
    pyperclip.copy(name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)  # 等搜索结果展开


def step_select_via_enter():
    """步骤 3 主：搜索框输入完按 Enter 进入第一个匹配 — 微信默认会高亮第一项"""
    print("  [3] 按 Enter 进入第一个搜索结果...")
    pyautogui.press("enter")
    time.sleep(1.2)


def step_click_search_result_fallback(win, name: str, save_debug=False):
    """步骤 3 备：Enter 没进对，视觉定位 dropdown 里的目标"""
    print(f"  [3-fallback] 视觉找 dropdown 里的 {name!r}...")
    _, img = shot_window(win)
    if save_debug:
        img.save(os.path.join(DEBUG_DIR, f"step3fb-{int(time.time())}.png"))

    prompt = f"""这是 PC 微信主窗口截图。用户刚在搜索框输入了 "{name}"，搜索框下方会展开一个**搜索结果 dropdown**（独立的悬浮列表，覆盖在群列表上方）。

请只在**搜索框正下方的 dropdown 列表**里找名字含 "{name}" 的第一项（不要看左侧默认群列表里的高亮项）。

返回 bbox（百分比 0-1）+ 你看到的项名 + 是否在 dropdown 里：
{{"x1":..., "y1":..., "x2":..., "y2":..., "matched_text": "你看到的字面文字", "in_dropdown": true/false, "found": true}}

如果完全没有匹配：{{"found": false}}

不要 markdown 代码块。"""

    res = doubao_call(prompt, img, max_tokens=300)
    if not res.get("found"):
        raise RuntimeError(f"搜索 dropdown 里没找到 {name!r}")
    print(f"      匹配项 {res.get('matched_text','?')!r}  in_dropdown={res.get('in_dropdown')}")
    cx, cy = bbox_to_screen_center(res, win)
    pyautogui.click(cx, cy)
    time.sleep(0.9)


def step_verify_chat(win, expected_name: str, save_debug=False):
    """步骤 4：截顶部 bar，验证当前聊天对象"""
    print("  [4] 验证已切到目标聊天...")
    _, img = shot_window(win)
    if save_debug:
        img.save(os.path.join(DEBUG_DIR, f"step4-verify-{int(time.time())}.png"))

    prompt = f"""这是 PC 微信窗口截图。请看**聊天主区顶部**显示的当前聊天对象名（顶部 bar 中央或左上的标题）。

返回 JSON：
{{"current_chat_name": "你看到的当前聊天对象名（如果完全没看到名字写 unknown）"}}

只返回 JSON，不要 markdown 代码块。"""

    res = doubao_call(prompt, img, max_tokens=100)
    actual = res.get("current_chat_name", "unknown")
    matched = expected_name.lower() in actual.lower() or actual.lower() in expected_name.lower()
    return matched, actual


def doubao_top_time(img) -> str:
    """让 DOUBAO 看一张聊天截图，返回顶部最早一条消息的时间标记字符串"""
    prompt = """这是 PC 微信聊天界面截图。

任务：找出截图里**位置最靠上**的那个**时间分隔条**（注意特征）：
- 是聊天主区**水平居中**的一行**灰色小字**
- 独占一行，**不在任何消息气泡里**，**不是消息时间戳**
- 通常的格式：
  - "今天 14:30" / "14:30"（同一天分组）
  - "昨天 18:00"
  - "周一 23:02" / "星期二 09:30"
  - "5月3日 14:00" / "12月20日 18:00"
  - "MM/DD" 或 "M/D" 简写形式（如 "04/13"）
  - "2025年12月20日 18:00"

**严格规则**：
- 只看真实存在的"水平居中、独占一行、灰色"的时间分隔条
- 如果整张图最上面是消息气泡里的时间戳（不是分隔条），不算 → 返回 unknown
- 如果你不能确定看到的是不是分隔条 → 宁可返回 unknown，不要瞎猜

只返回 JSON：{"earliest_time_label": "原文 或 unknown"}

不要 markdown 代码块。"""
    res = doubao_call(prompt, img, max_tokens=80)
    return res.get("earliest_time_label", "unknown")


def parse_wechat_time(s: str) -> datetime:
    """微信时间字符串 → datetime（最近一次匹配该标签的时刻）"""
    if not s or s == "unknown":
        return None
    now = datetime.now()
    s = s.strip()

    m_hm = re.search(r"(\d{1,2}):(\d{2})", s)

    # 今天
    if s.startswith("今天") and m_hm:
        return now.replace(hour=int(m_hm.group(1)), minute=int(m_hm.group(2)), second=0, microsecond=0)
    # 昨天
    if s.startswith("昨天") and m_hm:
        d = now - timedelta(days=1)
        return d.replace(hour=int(m_hm.group(1)), minute=int(m_hm.group(2)), second=0, microsecond=0)
    # 周X / 星期X
    wd_map = {"周一":0,"周二":1,"周三":2,"周四":3,"周五":4,"周六":5,"周日":6,
              "星期一":0,"星期二":1,"星期三":2,"星期四":3,"星期五":4,"星期六":5,"星期日":6,"星期天":6}
    for k, v in wd_map.items():
        if s.startswith(k) and m_hm:
            today_wd = now.weekday()
            days_back = (today_wd - v) % 7
            if days_back == 0:
                days_back = 7
            d = now - timedelta(days=days_back)
            return d.replace(hour=int(m_hm.group(1)), minute=int(m_hm.group(2)), second=0, microsecond=0)
    # X月X日 HH:MM 或 X月X日（无小时分钟）
    m = re.search(r"(\d{1,2})月(\d{1,2})日(?:.*?(\d{1,2}):(\d{2}))?", s)
    if m:
        h = int(m.group(3)) if m.group(3) else 0
        mn = int(m.group(4)) if m.group(4) else 0
        return datetime(now.year, int(m.group(1)), int(m.group(2)), h, mn)
    # YYYY年X月X日 HH:MM
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?(\d{1,2}):(\d{2})", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
    # MM/DD 或 M/D 或 MM-DD（带可选 HH:MM）
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?$", s)
    if m:
        h = int(m.group(3)) if m.group(3) else 0
        mn = int(m.group(4)) if m.group(4) else 0
        return datetime(now.year, int(m.group(1)), int(m.group(2)), h, mn)
    # 单纯 HH:MM
    if m_hm and not s.startswith(("今天","昨天","周","星期")):
        return now.replace(hour=int(m_hm.group(1)), minute=int(m_hm.group(2)), second=0, microsecond=0)
    return None


def img_pixel_hash(img) -> str:
    """缩小图片到 64x64 灰度后取 md5，用于判断'两张截图像素是否完全相同'"""
    small = img.convert("L").resize((64, 64))
    return hashlib.md5(small.tobytes()).hexdigest()


def stitch_vertical_scrolling(images: list, search_band=300) -> Image.Image:
    """把垂直滚动捕获的多张截图拼接成一张连续长图（去重叠区）

    输入 images 顺序：从最旧（顶部）到最新（底部）
    算法：对每对相邻 (上, 下)，在"上"底部 search_band 像素里找"下"上半部分的最佳模板匹配
         匹配点之上的像素属于"上"，之下的属于"下"，拼起来
    """
    if len(images) <= 1:
        return images[0] if images else None

    # 转 numpy 灰度（匹配快+稳）
    grays = [cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY) for img in images]
    arrays = [np.array(img.convert("RGB")) for img in images]

    result = arrays[0]
    for i in range(1, len(images)):
        prev_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
        next_gray = grays[i]
        next_arr = arrays[i]

        h_prev = prev_gray.shape[0]
        h_next = next_gray.shape[0]

        # 拿 next 顶部 search_band 像素作模板，在 prev 底部 search_band*2 像素里找
        band = min(search_band, h_next // 2)
        template = next_gray[:band]
        # 在 prev 底部 search_band*2 区域找模板
        search_top = max(0, h_prev - band * 3)
        search_region = prev_gray[search_top:]

        # cv2.matchTemplate
        if search_region.shape[0] < template.shape[0] or search_region.shape[1] != template.shape[1]:
            # 兜底：直接拼（信任滚屏步长精确）
            result = np.concatenate([result, next_arr], axis=0)
            continue

        res = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        # max_loc[1] = 模板在 search_region 中的最佳 y 偏移
        if max_val < 0.4:
            # 匹配置信太低，可能是已到顶或场景突变，直接追加（容忍冗余）
            result = np.concatenate([result, next_arr], axis=0)
            continue

        match_y_in_prev = search_top + max_loc[1]
        # prev 中 match_y_in_prev 处对应 next 的 y=0
        # 拼接：result[:match_y_in_prev] + next_arr
        result = np.concatenate([result[:match_y_in_prev], next_arr], axis=0)

    return Image.fromarray(result)


def step_scroll_until_time(win, hours: int, max_scrolls: int = 40, check_interval: int = 2, save_debug=False) -> list:
    """步骤 5：先滚到底 → 持续往上滚，**直到顶部时间 ≤ cutoff 或像素不再变化（真到顶）**才停"""
    target_cutoff = datetime.now() - timedelta(hours=hours)
    print(f"  [5] 滚屏到 {target_cutoff.strftime('%m-%d %H:%M')} 之前（cutoff = -{hours}h）")
    print(f"      最多滚 {max_scrolls} 次，每 {check_interval} 次问 DOUBAO 看顶部时间")

    list_ratio = 0.27
    top_ratio = 0.08
    bottom_ratio = 0.18
    chat_x = win.left + int(win.width * list_ratio)
    chat_y = win.top + int(win.height * top_ratio)
    chat_w = int(win.width * (1 - list_ratio))
    chat_h = int(win.height * (1 - top_ratio - bottom_ratio))
    cx = chat_x + chat_w // 2
    cy = chat_y + chat_h // 2

    pyautogui.moveTo(cx, cy)
    time.sleep(0.2)

    # 先到底（确保从最新开始）
    for _ in range(3):
        pyautogui.scroll(-3000, x=cx, y=cy)
        time.sleep(0.3)

    shots = [pyautogui.screenshot(region=(chat_x, chat_y, chat_w, chat_h))]

    last_pixel_hash = img_pixel_hash(shots[0])
    no_change_count = 0

    SCROLL_STEP = 1200
    for i in range(max_scrolls):
        pyautogui.scroll(SCROLL_STEP, x=cx, y=cy)
        time.sleep(0.8)  # 等历史消息加载（聊天区滚到顶后微信会异步加载更老的）
        new_shot = pyautogui.screenshot(region=(chat_x, chat_y, chat_w, chat_h))
        shots.append(new_shot)

        # 像素级"到顶"判定（比 DOUBAO 标签稳）
        cur_hash = img_pixel_hash(new_shot)
        if cur_hash == last_pixel_hash:
            no_change_count += 1
            if no_change_count >= 3:
                print(f"      ⚠ 连续 3 张截图像素完全相同 → 真的到顶了，停止 (滚了 {i+1} 次)")
                break
        else:
            no_change_count = 0
        last_pixel_hash = cur_hash

        # 时间检测：满足 cutoff 也停
        if (i + 1) % check_interval == 0:
            try:
                label = doubao_top_time(new_shot)
            except Exception as e:
                label = f"err:{e}"
            dt = parse_wechat_time(label)
            print(f"      滚 {i+1}/{max_scrolls}  顶部时间={label!r}  解析={dt}  像素无变化={no_change_count}")

            if dt and dt <= target_cutoff:
                print(f"      ✓ 已滚到 cutoff 之前 ({dt.strftime('%m-%d %H:%M')} ≤ {target_cutoff.strftime('%m-%d %H:%M')})，停止")
                break

    if save_debug:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        for i, img in enumerate(shots):
            img.save(os.path.join(DEBUG_DIR, f"scroll-{ts}-{i:02d}.png"))

    print(f"      共 {len(shots)} 张截图")
    shots.reverse()
    return shots


def step_summarize(name: str, hours: int, shots: list) -> dict:
    """步骤 6：DOUBAO 内容总结（严格按时间过滤）"""
    print(f"  [6] DOUBAO 总结 {len(shots)} 张图（严格过滤 {hours}h）...")
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d %H:%M")
    cutoff_str = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]

    prompt = f"""这是用户的微信「{name}」聊天的连续 {len(shots)} 张截图（**按时间从旧到新**，第 1 张最旧，第 {len(shots)} 张最新）。

# 时间锚定
- 现在时刻：{today_str}（{weekday_cn}）
- 时间窗口：**只保留过去 {hours} 小时内**，即 {cutoff_str} 到 {today_str} 之间
- 微信时间戳显示规则：
  - "今天 14:30" / "14:30" → 今天
  - "昨天 18:00" → 昨天
  - "周一 23:02" / "星期二 09:30" → 按当前 {weekday_cn} 推算最近的过去那天
  - "5月3日 14:00" → 当年该日
  - "2025年12月20日 18:00" → 跨年带年份

# 任务（重点：完整总结所有人所有消息）
1. 提取每条消息：发送人 + 时间（推算成实际日期+时间）+ 内容
2. 严格按时间过滤：丢弃 {cutoff_str} 之前的消息
3. 多张截图重叠去重（同一条消息只算一次）
4. **群聊/私聊都把所有人的所有消息纳入总结**——不只关注 {name}，不只关注"@你"
5. summary 要全面：群里聊了哪些话题、谁是主要发言者、出现了什么决议/争论/重要信息
6. key_points 列出**所有重要信息点**（包括别人之间的讨论结论、技术细节、商务信息、行业动态等）
7. things_for_you = 跟用户**间接或直接相关**的事（@你、问你、跟你业务相关、值得你关注的趋势）

严格输出 JSON（不要 markdown 代码块）：
{{
  "person_or_group": "{name}",
  "time_range_observed": "实际看到的最早 - 最新时间",
  "messages_in_window": 时间窗内消息总条数,
  "main_participants": ["主要发言人 1", "主要发言人 2"],
  "topics": ["讨论话题 1", "话题 2"],
  "summary": "5-10 句话完整总结：群里聊了什么、谁说了什么、达成了什么、出现了什么有价值信息",
  "key_points": ["重要信息点 1", "信息点 2", "..."],
  "things_for_you": ["跟用户相关或值得用户关注的事，无则空数组"],
  "raw_excerpts": [
    {{"time": "5/5 19:23", "from": "发送人名", "content": "原文摘录"}}
  ],
  "tone": "氛围（友好/讨论激烈/技术分享/吐槽/闲聊/商务对接 等）"
}}

如果时间窗内消息 < 3，summary 写"过去 {hours} 小时该会话几乎无新消息"。"""

    # 步骤 1：拼接成一张长图
    print(f"  拼接 {len(shots)} 张滚动截图为一张长图...")
    long_img = stitch_vertical_scrolling(shots, search_band=300)
    print(f"  拼接完成：{long_img.size[0]}x{long_img.size[1]}")
    # 保存长图到 debug 目录（如果开启）
    try:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        long_path = os.path.join(DEBUG_DIR, f"stitched-{name}-{ts}.png")
        long_img.save(long_path, optimize=True)
        print(f"  长图已存: {long_path}")
    except Exception:
        pass

    # 步骤 2：把长图按高度切成 ≤ SEGMENT_H 像素一段，每段单独喂 DOUBAO
    SEGMENT_H = 4096    # 每段最高 4096 px
    OVERLAP = 200       # 段间重叠 200 px 防消息被切断
    w, h = long_img.size
    if h <= SEGMENT_H:
        segments = [long_img]
    else:
        segments = []
        y = 0
        while y < h:
            seg = long_img.crop((0, y, w, min(y + SEGMENT_H, h)))
            segments.append(seg)
            if y + SEGMENT_H >= h:
                break
            y += SEGMENT_H - OVERLAP
        print(f"  长图 {h}px > {SEGMENT_H}，切成 {len(segments)} 段")

    # 步骤 3：所有段一起送 DOUBAO（一次调用，prompt 里说明这是同一张连续长图的 N 段）
    seg_prefix = f"\n\n# 输入说明\n下面 {len(segments)} 张图是同一段连续滚动聊天的**纵向切片**（按时间从旧到新拼接，第 1 张最旧，第 {len(segments)} 张最新），每两张相邻切片有约 200 px 重叠。请把它们当作一张完整长图来理解，不要重复计数重叠区域里的消息。" if len(segments) > 1 else ""

    content = [{"type": "text", "text": prompt + seg_prefix}]
    for seg in segments:
        b64 = shot_to_b64_jpeg(seg, quality=75, max_side=2048)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })

    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    resp = client.chat.completions.create(
        model=DOUBAO_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=3000,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def step_exit(win):
    """步骤 7：ESC 关搜索 + 取消 TOPMOST 恢复正常窗口顺序"""
    pyautogui.press("escape")
    time.sleep(0.3)
    # 取消 TOPMOST，让微信恢复正常 z-order（不再永久顶置）
    wins = find_wechat_hwnd_all()
    if wins:
        unpin_topmost(wins[0]["hwnd"])


def post_lark_card(result: dict, hours: int):
    if not BOSS_CHAT:
        return False
    name = result.get("person_or_group", "?")
    summary = result.get("summary", "")
    msgs_n = result.get("messages_in_window", 0)
    things = result.get("things_for_you", [])
    color = "red" if things else ("orange" if msgs_n >= 10 else "blue")

    header_line = f"📊 **{msgs_n}** 条 · ⏱ {result.get('time_range_observed','?')} · 🎭 {result.get('tone','?')}"
    elements = [
        {"tag": "div", "text": {"tag": "lark_md",
            "content": f"**📨 {name} · 过去 {hours}h 摘要**\n\n{header_line}"}},
    ]
    if result.get("main_participants"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"👥 主要发言：{', '.join(result['main_participants'])}"}})
    if result.get("topics"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": f"🏷 话题：{', '.join(result['topics'])}"}})
    elements.append({"tag": "hr"})
    elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**摘要**\n{summary}"}})
    if result.get("key_points"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**关键信息**\n" + "\n".join(f"• {p}" for p in result["key_points"])}})
    if things:
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**值得你关注**\n" + "\n".join(f"⚡ {a}" for a in things)}})
    if result.get("raw_excerpts"):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
            "content": "**原文摘录**\n" + "\n".join(f"• `{e.get('time','')}` **{e.get('from','?')}**: {e.get('content','')}" for e in result["raw_excerpts"][:8])}})

    card = {"config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": f"📨 {name} 摘要"}, "template": color},
            "elements": elements}
    r = subprocess.run(
        [LARK_CLI, "im", "+messages-send",
         "--as", "user", "--chat-id", BOSS_CHAT,
         "--msg-type", "interactive",
         "--content", json.dumps(card, ensure_ascii=False)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--max-scrolls", type=int, default=40, help="向上滚屏最多次数（默认 40，到时间窗外提前停）")
    ap.add_argument("--check-interval", type=int, default=2, help="每滚 N 次让 DOUBAO 检查一次顶部时间（默认 2）")
    ap.add_argument("--no-send", action="store_true")
    ap.add_argument("--debug", action="store_true", help="保存中间步骤截图")
    args = ap.parse_args()

    print(f"=== 视觉 RPA 扫描 {args.name!r} · 过去 {args.hours}h ===\n")

    if args.debug:
        os.makedirs(DEBUG_DIR, exist_ok=True)

    win = find_wechat_window()
    if not win:
        print("❌ 没找到微信主窗口")
        sys.exit(1)
    print(f"找到微信 ({win.width}x{win.height}) at ({win.left}, {win.top})")

    print("\n=== 阶段 A：进入聊天 ===")
    print("⚠ 接下来 15-20 秒不要碰键鼠")
    activate_wechat(win)

    try:
        step_locate_search_box(win, save_debug=args.debug)
        step_input_name(args.name)
        # 主路径：Enter 进入第一个搜索结果
        step_select_via_enter()
    except Exception as e:
        print(f"\n❌ 进入聊天失败: {e}")
        sys.exit(2)

    matched, actual = step_verify_chat(win, args.name, save_debug=args.debug)
    if not matched:
        print(f"  ⚠ Enter 后当前聊天是 {actual!r}，回退到视觉点击 dropdown")
        # 重新点搜索框 + 输入 + 视觉定位（搜索框可能被 Enter 关掉了）
        try:
            step_locate_search_box(win, save_debug=args.debug)
            step_input_name(args.name)
            step_click_search_result_fallback(win, args.name, save_debug=args.debug)
            matched, actual = step_verify_chat(win, args.name, save_debug=args.debug)
        except Exception as e:
            print(f"\n❌ fallback 也失败: {e}")
            sys.exit(2)
        if not matched:
            print(f"\n❌ 验证失败：当前聊天是 {actual!r} 不是 {args.name!r}")
            sys.exit(3)
    print(f"  ✓ 已切到 {actual!r}")

    print("\n=== 阶段 B：滚到时间窗外 + 总结 ===")
    shots = step_scroll_until_time(win, args.hours, max_scrolls=args.max_scrolls,
                                    check_interval=args.check_interval, save_debug=args.debug)
    try:
        result = step_summarize(args.name, args.hours, shots)
    except Exception as e:
        print(f"❌ 总结失败: {e}")
        sys.exit(4)

    step_exit(win)

    print(f"\n=== 摘要 ===")
    print(f"时间范围: {result.get('time_range_observed','?')}")
    print(f"消息数: {result.get('messages_in_window',0)}")
    print(f"语气: {result.get('tone','?')}")
    if result.get("main_participants"):
        print(f"主要发言: {', '.join(result['main_participants'])}")
    if result.get("topics"):
        print(f"话题: {', '.join(result['topics'])}")
    print(f"\n{result.get('summary','(无)')}")
    if result.get("key_points"):
        print(f"\n关键信息点:")
        for p in result["key_points"]:
            print(f"  • {p}")
    if result.get("things_for_you"):
        print(f"\n值得你关注:")
        for a in result["things_for_you"]:
            print(f"  ⚡ {a}")
    if result.get("raw_excerpts"):
        print(f"\n原文摘录（前 8 条）:")
        for e in result["raw_excerpts"][:8]:
            print(f"  [{e.get('time','?')}] {e.get('from','?')}: {e.get('content','')}")
    if result.get("action_items"):
        print(f"\n🚨 TA 等你:")
        for a in result["action_items"]:
            print(f"  🚨 {a}")

    if not args.no_send:
        ok = post_lark_card(result, args.hours)
        print(f"\n飞书卡片: {'✓ 已发' if ok else '⚠ 失败'}")


if __name__ == "__main__":
    main()
