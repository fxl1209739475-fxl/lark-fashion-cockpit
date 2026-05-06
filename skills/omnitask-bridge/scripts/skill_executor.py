"""omnitask-bridge · skill 执行器

职责：
  - 加载 skills-registry.json
  - 提供 execute(skill_id, params, on_event) 异步执行接口
  - subprocess 调用 cockpit skill 脚本，流式回报执行进度

被 chat_router.py 用，server.py 通过 chat_router 间接使用。
"""

import os
import sys
import json
import asyncio
import shlex
from pathlib import Path
from typing import Callable, Optional


COCKPIT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = Path(__file__).parent.parent / "config" / "skills-registry.json"


_registry_cache: Optional[dict] = None


def load_registry() -> dict:
    global _registry_cache
    if _registry_cache is None:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            _registry_cache = json.load(f)
    return _registry_cache


def find_skill(skill_id: str) -> Optional[dict]:
    reg = load_registry()
    for s in reg.get("skills", []):
        if s["id"] == skill_id:
            return s
    return None


def keyword_match(text: str) -> Optional[dict]:
    """关键词快速匹配（绕过 AI 节省时间），返回 skill 或 None"""
    reg = load_registry()
    text_lower = text.lower()
    for s in reg.get("skills", []):
        for kw in s.get("trigger_keywords", []):
            if kw in text:
                return s
    return None


def _build_args(skill: dict, params: dict) -> list:
    """根据 skill executor 模板和 params 拼出最终命令行"""
    cmd = list(skill["executor"])
    # 把 params 翻译成 --key value 形式追加（按 params_schema 顺序）
    schema = skill.get("params_schema") or {}
    for k in schema.keys():
        v = params.get(k)
        if v is None or v == "":
            continue
        cmd.append(f"--{k.replace('_', '-')}")
        cmd.append(str(v))
    # 显式忽略 cockpit skills 的 --no-send 默认行为：让 chat_router 决定
    return cmd


async def execute(
    skill_id: str,
    params: dict,
    on_event: Callable[[dict], None],
    timeout_sec: int = 60,
) -> dict:
    """异步执行 skill。on_event 回调会被反复调用，事件 type 见下：
       skill_start / skill_log / skill_done

       返回最终 {"ok": bool, "exit_code": int, "summary": str, "stdout_tail": str}
    """
    skill = find_skill(skill_id)
    if not skill:
        on_event({"type": "skill_done", "skill": skill_id, "ok": False,
                  "summary": f"未注册的 skill: {skill_id}"})
        return {"ok": False, "exit_code": -1, "summary": f"unknown skill: {skill_id}"}

    if skill["executor"][0] == "__internal__":
        # 内部命令（如打开创作页），由前端处理，这里直接 ack
        on_event({"type": "skill_done", "skill": skill_id, "ok": True,
                  "summary": f"已请求 {skill['label']}（前端处理）"})
        return {"ok": True, "exit_code": 0, "summary": "internal handled"}

    cmd = _build_args(skill, params)
    on_event({"type": "skill_start", "skill": skill_id, "label": skill["label"],
              "cmd": " ".join(shlex.quote(c) for c in cmd)})

    # 工作目录用 cockpit 根，让相对路径 skill 路径生效
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(COCKPIT_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    tail_lines = []
    try:
        async def read_loop():
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                if not line:
                    continue
                tail_lines.append(line)
                if len(tail_lines) > 80:
                    tail_lines.pop(0)
                # 推送给前端（短的关键行）
                if len(line) < 200:
                    on_event({"type": "skill_log", "skill": skill_id, "text": line})
        await asyncio.wait_for(read_loop(), timeout=timeout_sec)
        await proc.wait()
    except asyncio.TimeoutError:
        proc.kill()
        on_event({"type": "skill_done", "skill": skill_id, "ok": False,
                  "summary": f"超时 ({timeout_sec}s)"})
        return {"ok": False, "exit_code": -1, "summary": "timeout"}

    ok = proc.returncode == 0
    summary = " · ".join(tail_lines[-3:]) if tail_lines else ("完成" if ok else "失败")
    summary = summary[:240]
    on_event({"type": "skill_done", "skill": skill_id, "ok": ok, "summary": summary})

    return {
        "ok": ok,
        "exit_code": proc.returncode or 0,
        "summary": summary,
        "stdout_tail": "\n".join(tail_lines[-10:]),
    }


# CLI 自检
if __name__ == "__main__":
    print("=== omnitask-bridge skill executor 自检 ===\n")
    reg = load_registry()
    print(f"已注册 {len(reg.get('skills', []))} 个 skill：")
    for s in reg.get("skills", []):
        print(f"  [{s['category']:8}] {s['id']:30} - {s['label']}  ({len(s.get('trigger_keywords', []))} 关键词)")
    print()

    # 测试关键词匹配
    test_cases = [
        "今天销售多少？",
        "通知 ZC 工厂下周交货",
        "今天什么会议",
        "随便聊聊吧",
    ]
    for t in test_cases:
        m = keyword_match(t)
        print(f"  「{t}」 → {m['id'] if m else '(无匹配)'}")
