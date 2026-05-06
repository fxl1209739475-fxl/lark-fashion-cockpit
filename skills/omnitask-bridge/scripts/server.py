"""omnitask-bridge · FastAPI 主服务（端口 8080）

启动：
  python skills/omnitask-bridge/scripts/server.py
  访问 http://localhost:8080

提供：
  - GET /              主驾驶舱页面（serve web/index.html）
  - GET /static/*      前端静态资源
  - GET /creator       创作系统子页（嵌入 douyin-monitor）
  - WS  /ws/chat       聊天窗口 WebSocket
  - GET /api/health    健康检查
  - GET /api/skills    列出可用 skill
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

import urllib.request
import urllib.error

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

# 同目录 import
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

chat_router = _load("chat_router", "chat_router.py")
skill_executor = _load("skill_executor", "skill_executor.py")


SKILL_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = SKILL_ROOT / "web"


# ============================================================
# 应用
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("  omnitask-bridge · 启动")
    print("=" * 60)
    skills = skill_executor.load_registry().get("skills", [])
    print(f"已注册 {len(skills)} 个 skill")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("⚠ 未配置 DEEPSEEK_API_KEY — chat_router AI 路由不可用（仅关键词匹配）")
    print(f"前端目录: {WEB_DIR}")
    print(f"访问: http://localhost:{os.environ.get('OMNITASK_PORT', '8080')}/")
    yield
    print("\nomnitask-bridge · 关闭")


app = FastAPI(title="omnitask-bridge", version="1.0.0", lifespan=lifespan)


# ============================================================
# 静态前端
# ============================================================

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
    creator_dir = WEB_DIR / "creator"
    if creator_dir.exists():
        app.mount("/creator-static", StaticFiles(directory=str(creator_dir)), name="creator")


@app.get("/")
async def root():
    """主驾驶舱页面"""
    index_html = WEB_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(status_code=500, detail="web/index.html 不存在")
    return FileResponse(str(index_html))


@app.get("/app.js")
async def app_js():
    return FileResponse(str(WEB_DIR / "app.js"), media_type="text/javascript")


@app.get("/styles.css")
async def styles_css():
    return FileResponse(str(WEB_DIR / "styles.css"), media_type="text/css")


@app.get("/chat.js")
async def chat_js():
    return FileResponse(str(WEB_DIR / "chat.js"), media_type="text/javascript")


@app.get("/creator")
async def creator_page():
    """创作系统子页 — 后续会嵌入 douyin-monitor 的 dashboard"""
    creator_html = WEB_DIR / "creator" / "index.html"
    if creator_html.exists():
        return FileResponse(str(creator_html))
    return JSONResponse({"todo": "creator 页面将嵌入 douyin-monitor/dashboard/index.html",
                         "_workaround": "暂时打开 http://localhost:8000 直接访问 douyin-monitor"},
                        status_code=200)


# ============================================================
# REST API
# ============================================================

@app.get("/api/health")
async def health():
    skills = skill_executor.load_registry().get("skills", [])
    return {
        "ok": True,
        "skills_count": len(skills),
        "deepseek_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "doubao_configured": bool(os.environ.get("DOUBAO_API_KEY")),
        "lark_base_token_configured": bool(os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN")),
    }


@app.get("/api/skills")
async def list_skills():
    return skill_executor.load_registry()


# ============================================================
# 创作系统反向代理（/creator-api/* → http://localhost:8000/api/*）
# ============================================================

CREATOR_BACKEND = os.environ.get("CREATOR_BACKEND_URL", "http://localhost:8000")


@app.api_route("/creator-api/{path:path}", methods=["GET", "POST", "PATCH", "DELETE", "PUT"])
async def creator_api_proxy(path: str, request: Request):
    """把 /creator-api/* 反代到 douyin-monitor server.py 的 /api/*"""
    target = f"{CREATOR_BACKEND}/api/{path}"
    if request.url.query:
        target += f"?{request.url.query}"

    body = await request.body()
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in {"host", "content-length"}}

    req = urllib.request.Request(target, data=body if body else None,
                                  method=request.method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            return Response(content=data, status_code=resp.status,
                            media_type=resp.headers.get("content-type", "application/json"))
    except urllib.error.URLError as e:
        return JSONResponse({"ok": False,
                             "error": f"创作系统未启动（{CREATOR_BACKEND}）。请另开窗口运行: cd C:\\Users\\冯兴龙\\douyin-monitor && python server.py",
                             "detail": str(e)}, status_code=503)


# ============================================================
# WebSocket：聊天
# ============================================================

@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    print(f"\n[WS] 新连接：{ws.client.host}:{ws.client.port}")
    history = []  # 简单内存历史（对话上下文）
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                await ws.send_text(json.dumps({"type": "error", "text": "消息不是合法 JSON"}))
                continue

            mtype = msg.get("type")
            if mtype != "user_message":
                await ws.send_text(json.dumps({"type": "error", "text": f"未知 type: {mtype}"}))
                continue

            text = (msg.get("text") or "").strip()
            if not text:
                continue

            print(f"[WS] user: {text[:80]}")
            await ws.send_text(json.dumps({"type": "ack"}))

            # on_event 回调：把 router/executor 的事件实时推给前端
            send_queue = asyncio.Queue()

            def push(event):
                # 同步回调 → 入队（在异步循环里发出去）
                send_queue.put_nowait(event)

            async def drain():
                while True:
                    ev = await send_queue.get()
                    if ev is None:
                        break
                    try:
                        await ws.send_text(json.dumps(ev, ensure_ascii=False))
                    except Exception:
                        return

            drain_task = asyncio.create_task(drain())

            try:
                result = await chat_router.route(text, user_role="owner", on_event=push)
                history.append({"role": "user", "content": text})
                if result.get("casual_reply"):
                    history.append({"role": "assistant", "content": result["casual_reply"]})
            except Exception as e:
                push({"type": "error", "text": f"处理异常: {e}"})

            push(None)  # 结束 drain
            try:
                await asyncio.wait_for(drain_task, timeout=2)
            except asyncio.TimeoutError:
                drain_task.cancel()

    except WebSocketDisconnect:
        print(f"[WS] 断开：{ws.client.host}:{ws.client.port}")


# ============================================================
# 启动
# ============================================================

def main():
    import uvicorn
    port = int(os.environ.get("OMNITASK_PORT", "8080"))
    host = os.environ.get("OMNITASK_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
