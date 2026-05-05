"""livestream-scraper.py — 直播平台数据自动抓取

完整工作流：
  1. Playwright 启动浏览器（首次手动登录，cookie 持久化）
  2. 打开抖音/视频号/小红书 商家后台直播数据页
  3. DOM 抓取 / 截屏 OCR 提取销售明细
  4. 调 inventory-gmv-matcher.ps1 匹配库存 GMV
  5. 写飞书 base / 推卡片

3 个平台支持：
  --platform douyin    抖音电商后台
  --platform shipinhao 视频号小店
  --platform xhs       小红书电商

首次使用：
  python livestream-scraper.py --platform douyin --first-login
  → 浏览器打开，扫码登录，关闭浏览器，cookie 自动保存

后续使用：
  python livestream-scraper.py --platform douyin
  → 自动加载 cookie，无需登录

集成 douyin-monitor（推荐，复用现有能力）：
  抖音不用重写，直接调 ~/douyin-monitor/scripts/抓直播间数据
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PLATFORMS = {
    "douyin": {
        "name": "抖音电商",
        "url": "https://fxg.jinritemai.com/ffa/buyin/dashboard/live",
        "cookie": "cookies/douyin.json",
        "selectors": {
            "sales_table": "table.live-sales tbody tr",
            "sku": "td.sku-col",
            "name": "td.product-name",
            "amount": "td.gmv-col",
        },
    },
    "shipinhao": {
        "name": "视频号小店",
        "url": "https://channels.weixin.qq.com/livedata",
        "cookie": "cookies/shipinhao.json",
        "selectors": {
            "sales_table": ".live-product-list .item",
            "sku": ".product-id",
            "name": ".product-name",
            "amount": ".sales-amount",
        },
    },
    "xhs": {
        "name": "小红书电商",
        "url": "https://ark.xiaohongshu.com/livedata",
        "cookie": "cookies/xhs.json",
        "selectors": {
            "sales_table": ".live-sales-row",
            "sku": ".sku",
            "name": ".product-title",
            "amount": ".gmv",
        },
    },
}


def ensure_dirs():
    Path("cookies").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)


def scrape_browser(platform_key: str, first_login: bool = False, debug: bool = False):
    """真用 Playwright 抓数据"""
    config = PLATFORMS[platform_key]
    print(f"=== {config['name']} 数据抓取 ===")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠ playwright 未装：pip install playwright && playwright install chromium")
        return scrape_mock(platform_key)

    sales = []
    with sync_playwright() as p:
        # 首次登录走 headed 模式让用户扫码；后续走 headed + cookie
        browser = p.chromium.launch(headless=False, slow_mo=500)
        cookie_path = config["cookie"]

        if not first_login and Path(cookie_path).exists():
            with open(cookie_path) as f:
                ctx = browser.new_context(storage_state=json.load(f))
        else:
            ctx = browser.new_context()

        page = ctx.new_page()
        print(f"  打开: {config['url']}")
        page.goto(config["url"])

        if first_login:
            print()
            print("  ⚠ 首次登录步骤：")
            print("    1. 在浏览器里扫码登录（用手机飞书/微信扫码）")
            print("    2. 登录成功后，导航到「直播数据」页面（首页菜单可找到）")
            print("    3. 在 PowerShell 这里按【回车】保存 cookie")
            print()
            input("  → 登录 + 进入直播数据页后按【回车】... ")
            # 保存 cookie
            with open(cookie_path, "w") as f:
                json.dump(ctx.storage_state(), f)
            print(f"  ✓ cookie 已保存到 {cookie_path}")

            if debug:
                # 调试模式：保持浏览器开 + 让用户复制 HTML 给我
                print()
                print("  🔍 调试模式 - 帮我找 DOM selector：")
                print("    1. 在浏览器按 F12 打开开发者工具")
                print("    2. 切到 Elements 标签")
                print("    3. 用左上角箭头点击「直播销售数据表格」整体")
                print("    4. 选中的元素 → 右键 → Copy → Copy outerHTML")
                print(f"    5. HTML 太长？保存到 C:\\temp\\{platform_key}_html.txt")
                print()
                input("  → 完成后按【回车】关闭浏览器... ")

            browser.close()
            return []

        # 等表格加载
        try:
            page.wait_for_selector(config["selectors"]["sales_table"], timeout=15000)
        except Exception as e:
            print(f"  ⚠ 元素未找到 / selector 还没调好: {e}")
            if debug:
                print("  保持浏览器开供你 F12 调试 selector...")
                input("  完成后按【回车】关闭... ")
            browser.close()
            return []

        # 截屏（用作 OCR 备份）
        screenshot_path = f"screenshots/{platform_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  ✓ 截屏: {screenshot_path}")

        # DOM 抓数据
        rows = page.query_selector_all(config["selectors"]["sales_table"])
        for row in rows:
            try:
                sku = row.query_selector(config["selectors"]["sku"]).inner_text().strip()
                name = row.query_selector(config["selectors"]["name"]).inner_text().strip()
                amount_txt = row.query_selector(config["selectors"]["amount"]).inner_text().strip()
                amount = float(amount_txt.replace("¥", "").replace(",", "").replace("元", ""))
                sales.append({"sku": sku, "name": name, "amount": int(amount), "platform": config["name"]})
            except Exception as e:
                print(f"  [skip row] {e}")

        browser.close()

    print(f"  ✓ 抓到 {len(sales)} 条销售记录")
    return sales


def scrape_mock(platform_key: str):
    """无 Playwright 时使用 mock 数据演示完整链路"""
    print(f"  [mock] 使用 mock 销售数据演示算法")
    base = {
        "douyin": [
            {"sku": "DRS-0429-FL", "name": "法式碎花连衣裙", "amount": 29900, "platform": "抖音"},
            {"sku": "KNT-0402-CD", "name": "短款焦糖针织开衫", "amount": 18900, "platform": "抖音"},
            {"sku": "PNT-0418-SU", "name": "通勤西装裤", "amount": 21500, "platform": "抖音"},
        ],
        "shipinhao": [
            {"sku": "SHT-0420-SP", "name": "海盐蓝防晒衬衫", "amount": 33800, "platform": "视频号"},
            {"sku": "SKT-0328-A", "name": "高腰A字裙", "amount": 15900, "platform": "视频号"},
        ],
        "xhs": [
            {"sku": "OUT-2024-OL", "name": "OL极简西服", "amount": 27500, "platform": "小红书"},
        ],
    }
    return base.get(platform_key, [])


def call_inventory_matcher(sales):
    """把抓到的数据传给 inventory-gmv-matcher.ps1"""
    sales_json_path = r"C:\Users\冯兴龙\AppData\Local\Temp\livestream-sales.json"
    with open(sales_json_path, "w", encoding="utf-8") as f:
        json.dump(sales, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 销售数据写入: {sales_json_path}")

    print("\n=== 调用 inventory-gmv-matcher.ps1 ===")
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File",
         r"C:\Users\冯兴龙\lark-fashion-cockpit\scripts\inventory-gmv-matcher.ps1",
         "-InputJsonPath", sales_json_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=120,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  [stderr] {result.stderr[:300]}")


def main():
    ensure_dirs()
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], default="all")
    ap.add_argument("--first-login", action="store_true", help="首次登录（扫码后保存 cookie）")
    ap.add_argument("--debug", action="store_true", help="调试模式（保持浏览器开 + 提示 F12 找 selector）")
    ap.add_argument("--mock", action="store_true", help="跳过浏览器，用 mock 数据演示完整算法")
    args = ap.parse_args()

    targets = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]

    all_sales = []
    for plat in targets:
        if args.mock:
            sales = scrape_mock(plat)
        else:
            sales = scrape_browser(plat, args.first_login, args.debug)
        all_sales.extend(sales)
        print()

    if args.first_login:
        return

    print(f"=== 合计 {len(all_sales)} 条销售记录 ===")
    if all_sales:
        call_inventory_matcher(all_sales)


if __name__ == "__main__":
    main()
