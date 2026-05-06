"""把微信从系统托盘里呼出来 — 即使主窗口被关到托盘也能强制显示

原理：
  1. 用 win32gui.EnumWindows 遍历所有窗口（包括隐藏的）
  2. 按 class_name 'mmui::MainWindow' 找到微信主窗口 hwnd
  3. ShowWindow(SW_RESTORE) + SetForegroundWindow 让它显示并置顶
"""

import sys, time

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import win32gui
import win32con


WECHAT_TITLES = ("微信", "Weixin", "WeChat")
WECHAT_CLASSES = ("mmui::MainWindow", "WeChatMainWndForPC")


def find_wechat_windows():
    """遍历所有窗口（含隐藏），找微信主窗口"""
    found = []

    def callback(hwnd, _):
        try:
            title = win32gui.GetWindowText(hwnd) or ""
            cls = win32gui.GetClassName(hwnd) or ""
        except Exception:
            return True
        if title in WECHAT_TITLES or any(c in cls for c in WECHAT_CLASSES):
            visible = win32gui.IsWindowVisible(hwnd)
            iconic = win32gui.IsIconic(hwnd)  # 最小化
            try:
                rect = win32gui.GetWindowRect(hwnd)
            except Exception:
                rect = None
            found.append({
                "hwnd": hwnd, "title": title, "class": cls,
                "visible": bool(visible), "iconic": bool(iconic),
                "rect": rect,
            })
        return True

    win32gui.EnumWindows(callback, None)
    return found


def wake_wechat():
    """把微信从托盘/隐藏/最小化状态呼出来，置顶到前台"""
    wins = find_wechat_windows()
    if not wins:
        return False, "找不到任何微信主窗口（进程可能没运行）"

    # 优先选 class 是 mmui::MainWindow 的（4.x 主窗口）
    main = None
    for w in wins:
        if "mmui::MainWindow" in w["class"]:
            main = w
            break
    if not main:
        main = wins[0]

    hwnd = main["hwnd"]

    # SW_RESTORE = 9，会同时取消最小化 + 显示窗口
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.2)

    # 再次 SW_SHOW 确保 visible
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    time.sleep(0.2)

    # 置顶到前台
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        # 有时 Windows 拒绝抢焦点，试用 BringWindowToTop
        try:
            win32gui.BringWindowToTop(hwnd)
        except Exception:
            pass

    time.sleep(0.5)

    after = find_wechat_windows()
    main_after = next((w for w in after if w["hwnd"] == hwnd), None)
    if main_after and main_after["visible"] and not main_after["iconic"]:
        return True, f"已唤起 [{main_after['title']!r}]  rect={main_after['rect']}"
    return False, f"调用了 ShowWindow 但窗口仍未显示  state={main_after}"


def main():
    print("=== 唤起微信 ===\n")
    print("[1/2] 扫描所有微信窗口...")
    wins = find_wechat_windows()
    print(f"找到 {len(wins)} 个匹配窗口:")
    for w in wins:
        print(f"  hwnd={w['hwnd']}  title={w['title']!r}  class={w['class']!r}  visible={w['visible']}  iconic={w['iconic']}")

    if not wins:
        print("\n❌ 进程可能没运行，去开一下微信")
        sys.exit(1)

    print("\n[2/2] 唤起主窗口...")
    ok, msg = wake_wechat()
    print(f"  {'✓' if ok else '⚠'} {msg}")


if __name__ == "__main__":
    main()
