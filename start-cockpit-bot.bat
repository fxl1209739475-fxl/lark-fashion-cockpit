@echo off
REM lark-fashion-cockpit 后台静默启动（无窗口版）
REM 双击运行 → listener + scheduler 都启动 → 不开黑窗口
REM 看日志：notepad logs\listener.log

cd /d "%~dp0"

REM 用 pythonw（无 console 版）启动 listener — 不开黑窗口
start "" /b pythonw scripts\event-listener.py

REM 启动 scheduler（自动调度 12 个 cron 任务）
start "" /b pythonw skills\auto-scheduler\scripts\cockpit-scheduler.py

REM 立刻退出，不留窗口
exit
