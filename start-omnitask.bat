@echo off
REM omnitask-bridge 一键启动
REM   - 启动 FastAPI server（端口 8080）
REM   - 可选：同时启动 douyin-monitor（端口 8000）

setlocal
cd /d "%~dp0"

echo ============================================================
echo   lark-fashion-cockpit · omnitask-bridge
echo ============================================================
echo.

REM 确认依赖
python -c "import fastapi, uvicorn, openai, dotenv" 2>nul
if errorlevel 1 (
  echo [安装依赖]
  pip install fastapi uvicorn openai python-dotenv
)

REM 可选：后台启动创作系统
if exist "C:\Users\冯兴龙\douyin-monitor\server.py" (
  echo [后台启动 douyin-monitor 创作系统 ^(端口 8000^)...]
  start "" /b pythonw "C:\Users\冯兴龙\douyin-monitor\server.py"
  timeout /t 2 >nul
)

echo.
echo [启动 omnitask-bridge ^(端口 8080^)...]
echo 浏览器访问: http://localhost:8080
echo 按 Ctrl+C 停止
echo.

python skills\omnitask-bridge\scripts\server.py
