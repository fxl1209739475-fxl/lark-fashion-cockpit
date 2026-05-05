@echo off
REM 停止 cockpit 机器人（杀所有 listener / scheduler / lark-cli 进程）

taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq event-listener*" 2>nul
wmic process where "name='pythonw.exe' and CommandLine like '%%event-listener%%'" delete 2>nul
wmic process where "name='pythonw.exe' and CommandLine like '%%cockpit-scheduler%%'" delete 2>nul
wmic process where "name='lark-cli.exe' and CommandLine like '%%event consume%%'" delete 2>nul

echo ✓ cockpit 机器人已停
timeout /t 2 >nul
exit
