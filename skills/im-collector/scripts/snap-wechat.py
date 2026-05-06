"""微信主窗口截图测试 —— 第一步：能不能定位到微信窗口并截图

用法：
  python snap-wechat.py
  python snap-wechat.py --keep   # 保留截图文件（默认会提示路径但不写盘逻辑）

说明：
  1. 这个脚本只截图，不调 AI、不发飞书 —— 用于验证窗口定位和截图本身
  2. 微信主窗口必须可见（不能最小化到托盘）
"""

import os, sys, argparse, time
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pygetwindow as gw
import pyautogui
from PIL import Image


OUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\out\wechat-snapshots"


def find_wechat_window():
    """找到微信主窗口（4.0+ 版本叫"微信"或"Weixin"）"""
    candidates = []
    for w in gw.getAllWindows():
        title = w.title or ""
        if title in ("微信", "Weixin", "WeChat"):
            candidates.append(w)
    return candidates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="保留截图（默认也会保留以便看效果）")
    args = ap.parse_args()

    print("=== 微信窗口截图测试 ===\n")

    print("[1/3] 查找微信主窗口...")
    wins = find_wechat_window()
    if not wins:
        print("❌ 没找到微信主窗口")
        print("   请确认：")
        print("   1. PC 微信桌面版正在运行")
        print("   2. 主窗口可见（不能最小化到系统托盘）")
        print("\n   当前所有窗口标题:")
        for w in gw.getAllWindows()[:20]:
            if w.title:
                print(f"     - {w.title!r}")
        sys.exit(1)

    if len(wins) > 1:
        print(f"⚠ 找到 {len(wins)} 个微信窗口，用第一个")
    win = wins[0]
    print(f"✓ 找到: {win.title!r}  位置=({win.left},{win.top}) 大小=({win.width}x{win.height})")

    if win.width < 400 or win.height < 300:
        print(f"⚠ 窗口太小（{win.width}x{win.height}），AI 识别效果会差，建议放大")

    print("\n[2/3] 把窗口前置（避免被遮挡）...")
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.6)
    except Exception as e:
        print(f"⚠ 前置失败（可能不影响截图）: {e}")

    print("\n[3/3] 截图...")
    region = (win.left, win.top, win.width, win.height)
    shot = pyautogui.screenshot(region=region)

    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(OUT_DIR, f"wechat-{ts}.png")
    shot.save(path, optimize=True)

    size_kb = os.path.getsize(path) / 1024
    print(f"✓ 截图已存: {path}")
    print(f"  大小: {size_kb:.1f} KB  尺寸: {shot.size[0]}x{shot.size[1]}")

    print(f"\n🎉 截图测试通过。下一步：")
    print(f"   1. 打开截图看下质量：{path}")
    print(f"   2. 配置 DOUBAO_API_KEY 后跑 scan-wechat.py 让 AI 识别")


if __name__ == "__main__":
    main()
