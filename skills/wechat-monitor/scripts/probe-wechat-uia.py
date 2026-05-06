"""探测 PC 微信 4.1.9 的 UIA 控件树 — 找搜索框、群列表、消息区的真实控件路径

只读，不点不输入。dump 关键控件的 AutomationId / Name / ClassName / ControlType。
"""

import sys, os, json
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError


def find_wechat_app():
    """连接到微信主窗口"""
    desk = Desktop(backend="uia")
    candidates = []
    for w in desk.windows():
        try:
            t = w.window_text()
            cls = w.class_name()
            if t in ("微信", "Weixin", "WeChat") or cls in ("WeChatMainWndForPC", "Qt51514QWindowIcon", "MainWindow"):
                candidates.append((t, cls, w))
        except Exception:
            continue
    return candidates


def walk_controls(elem, depth=0, max_depth=6, results=None):
    """递归遍历控件树，收集有意义的节点"""
    if results is None:
        results = []
    if depth > max_depth:
        return results
    try:
        info = elem.element_info
        ctype = info.control_type or ""
        name = (info.name or "")[:60]
        auto_id = info.automation_id or ""
        cls = info.class_name or ""
        rect = info.rectangle

        # 收集"有信息量"的控件：有 name 或 auto_id 或属于关键类型
        keep_types = {"Edit", "List", "ListItem", "Button", "Document", "Text", "Pane", "Group"}
        if name or auto_id or ctype in keep_types:
            results.append({
                "depth": depth,
                "type": ctype,
                "name": name,
                "auto_id": auto_id,
                "class": cls,
                "rect": [rect.left, rect.top, rect.right, rect.bottom] if rect else None,
            })
    except Exception:
        return results

    try:
        for child in elem.children():
            walk_controls(child, depth + 1, max_depth, results)
    except Exception:
        pass
    return results


def main():
    print("=== 探测 PC 微信 UIA 控件树 ===\n")

    print("[1/3] 找微信主窗口...")
    cands = find_wechat_app()
    if not cands:
        print("❌ 没找到微信主窗口（标题=微信/Weixin）")
        sys.exit(1)
    for i, (t, cls, w) in enumerate(cands):
        print(f"  [{i}] title={t!r}  class={cls!r}")
    win = cands[0][2]
    print(f"\n用 [{0}]")

    print("\n[2/3] 遍历控件树（max_depth=8）...")
    results = walk_controls(win, max_depth=8)
    print(f"找到 {len(results)} 个有意义的控件")

    out_dir = Path(__file__).parent.parent / "out"
    out_dir.mkdir(exist_ok=True)
    full_path = out_dir / "uia-tree-full.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"完整树已存: {full_path}")

    print("\n[3/3] 找关键控件 ===")

    print("\n--- Edit (输入框/搜索框) ---")
    edits = [r for r in results if r["type"] == "Edit"]
    for r in edits[:10]:
        print(f"  depth={r['depth']}  name={r['name']!r}  auto_id={r['auto_id']!r}  rect={r['rect']}")

    print("\n--- List (列表容器) ---")
    lists = [r for r in results if r["type"] == "List"]
    for r in lists[:10]:
        print(f"  depth={r['depth']}  name={r['name']!r}  auto_id={r['auto_id']!r}  rect={r['rect']}")

    print("\n--- 顶部 0-15% 区域控件（搜索框/标题应在这）---")
    try:
        win_rect = win.element_info.rectangle
        win_h = win_rect.bottom - win_rect.top
        top_thresh = win_rect.top + win_h * 0.15
    except Exception:
        top_thresh = 1000
    top_ctrls = [r for r in results if r["rect"] and r["rect"][1] < top_thresh and r["type"] in ("Edit", "Button", "Text", "Pane")]
    for r in top_ctrls[:15]:
        print(f"  type={r['type']:8} name={r['name']!r:30}  auto_id={r['auto_id']!r:20} rect={r['rect']}")

    print("\n--- ListItem 前 15 个（猜：左侧群/联系人列表）---")
    items = [r for r in results if r["type"] == "ListItem"]
    for r in items[:15]:
        print(f"  depth={r['depth']}  name={r['name']!r}  rect={r['rect']}")

    print(f"\n=== 完成 ===")
    print(f"完整 dump: {full_path}")


if __name__ == "__main__":
    main()
