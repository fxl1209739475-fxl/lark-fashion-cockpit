"""cockpit 主调度器 — 接管所有 cron 自动任务

启动后常驻运行，按 config/auto-triggers.json 调度 12+ 个自动任务。
飞书发"列出自动任务"/"停 X"/"启用 X"实时控制（接 event-listener 路由）。

用法：
  python skills/auto-scheduler/scripts/cockpit-scheduler.py

  # 后台运行（Windows）：
  Start-Process python -ArgumentList "skills/auto-scheduler/scripts/cockpit-scheduler.py" -WindowStyle Hidden

  # 开机自启：
  Windows Task Scheduler → 触发器选 "At log on" → 程序: pythonw.exe → 参数: 上面的脚本路径
"""

import json
import os
import sys
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = r"C:\Users\冯兴龙\lark-fashion-cockpit"
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "auto-triggers.json")
LOG_PATH = os.path.join(PROJECT_ROOT, "logs", "scheduler.log")
STATUS_PATH = os.path.join(PROJECT_ROOT, "logs", "scheduler-status.json")

# 命令目标 → chat_id 解析
TARGET_RESOLVE = {
    "boss_chat": os.environ.get("LARK_FASHION_COCKPIT_BOSS_CHAT", "oc_45e0995a007db9d7f1859fa17b6566f6"),
    "anchor_chat": os.environ.get("LARK_ANCHOR_CHAT", ""),
    "internal": "",
    "each_employee_p2p": "",
}


def log(msg: str, level: str = "INFO"):
    line = f"[{datetime.now().isoformat()}] [{level}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def write_status(scheduler):
    """把当前调度状态写到 logs/scheduler-status.json，event-listener 可读"""
    jobs = []
    for j in scheduler.get_jobs():
        jobs.append({
            "id": j.id,
            "name": j.name,
            "next_run": j.next_run_time.isoformat() if j.next_run_time else None,
        })
    try:
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump({"updated_at": datetime.now().isoformat(),
                       "jobs": jobs}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def run_command(trigger: dict):
    """执行单个触发器（subprocess 隔离失败不影响其他任务）"""
    cmd = trigger["command"]
    log(f"⚡ 触发 {trigger['id']} ({trigger['name']}): {cmd[:80]}")
    try:
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(
            cmd, shell=True, cwd=PROJECT_ROOT, env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=trigger.get("timeout_seconds", 600),
        )
        if result.returncode == 0:
            log(f"  ✓ {trigger['id']} 完成")
        else:
            log(f"  ✗ {trigger['id']} 失败 rc={result.returncode}: {(result.stderr or '')[:200]}", "ERROR")
    except subprocess.TimeoutExpired:
        log(f"  ⏱ {trigger['id']} 超时", "ERROR")
    except Exception as e:
        log(f"  ✗ {trigger['id']} 异常: {e}", "ERROR")


def setup_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        log("✗ 缺 apscheduler。运行: pip install apscheduler", "ERROR")
        sys.exit(1)

    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    cfg = load_config()
    enabled_count = 0

    for t in cfg["triggers"]:
        if not t.get("enabled", False):
            log(f"⏸ 跳过禁用任务: {t['id']}")
            continue
        try:
            trigger = CronTrigger.from_crontab(t["cron"], timezone="Asia/Shanghai")
            scheduler.add_job(
                func=run_command,
                trigger=trigger,
                args=[t],
                id=t["id"],
                name=t["name"],
                replace_existing=True,
            )
            enabled_count += 1
            log(f"✓ 注册 {t['id']} ({t['name']}) cron={t['cron']}")
        except Exception as e:
            log(f"✗ 注册 {t['id']} 失败: {e}", "ERROR")

    scheduler.start()
    log(f"\n[scheduler] 已注册 {enabled_count} 个自动任务")
    write_status(scheduler)
    return scheduler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reload", action="store_true", help="重新加载配置（实际跑要重启进程）")
    ap.add_argument("--list", action="store_true", help="列出所有任务（不启动调度器）")
    args = ap.parse_args()

    if args.list:
        cfg = load_config()
        print(f"\n{'ID':<32} {'状态':<6} {'cron':<16} 名称")
        print("─" * 90)
        for t in cfg["triggers"]:
            status = "✅ on" if t.get("enabled") else "⏸ off"
            print(f"{t['id']:<32} {status:<6} {t['cron']:<16} {t['name']}")
        return

    log("=" * 60)
    log(f"🚀 cockpit-scheduler 启动 @ {datetime.now()}")
    log("=" * 60)
    scheduler = setup_scheduler()

    log("\n[scheduler] 主循环开始（Ctrl+C 退出）")
    try:
        while True:
            time.sleep(60)
            write_status(scheduler)
    except (KeyboardInterrupt, SystemExit):
        log("👋 关闭调度器 ...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
