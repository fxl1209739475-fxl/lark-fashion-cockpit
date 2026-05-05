"""视频脚本拆解 skill — 不看视频也能拿到完整脚本

输入：抖音/快手/TikTok/B 站/小红书 视频 URL
处理：
  1. yt-dlp 下载视频
  2. ffmpeg 抽关键帧（每秒 1 张）
  3. 豆包多模态视觉理解（按 6 维结构拆解：基础要求/场景/分镜/声音/文字/可调参数）
  4. 写飞书 wiki 文档

用法：
  $env:DOUBAO_API_KEY="..."; $env:DOUBAO_MODEL="ep-xxx"
  python scripts/parse-video-script.py --url "https://www.douyin.com/video/xxx"
  python scripts/parse-video-script.py --url "..." --no-wiki   # 只本地存 .md
"""

import subprocess, json, os, argparse, base64, sys, re
from pathlib import Path
from openai import OpenAI

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_MODEL = os.environ.get("DOUBAO_MODEL", "")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

OUTPUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\out\video-analysis"
LARK_CLI = r"C:\Users\冯兴龙\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE = os.environ.get("LARK_FASHION_COCKPIT_BASE_TOKEN", "")
TABLE_BLOGGERS = "tblPDTGpUiJxZwHA"  # 27_对标博主视频监控
TMP_DIR = r"C:\Users\冯兴龙\AppData\Local\Temp"

PROMPT = """你是专业的短视频脚本拆解专家。我给你这条视频的关键帧截图（每秒 1 张，按时间顺序排列），请按以下结构详细拆解视频脚本：

## 一、基础要求
- **平台**（推断：抖音/快手/TikTok/小红书/B 站）
- **比例**（9:16 竖屏 / 16:9 横屏 / 1:1 方屏）
- **风格**（真实手持拍摄/三脚架固定/Vlog 风/广告片风/产品摆拍 等）

## 二、场景设定
- **场景类型**（仓库/居家/户外/门店/咖啡馆/机场/路边 等）
- **地面**（具体材质和颜色）
- **天花/光源**（自然光/灯光/混合，光照方向）
- **背景**(完整描述背景元素)
- **核心展示区**（主产品的位置）
- **辅助陈列**（旁边其他物品，如果有）

## 三、分镜结构（按秒拆解）
按 markdown 表格输出，每秒一行：
| 时间区间 | 镜头动作 | 画面内容 |
| --- | --- | --- |
| 0-1s | ... | ... |
| 1-2s | ... | ... |
（一直到视频结尾）

## 四、声音设计
- **BGM 风格**
- **旁白语言/语气**
- **旁白台词**（如果画面里能推断出口型/字幕，尽量转写）
- **环境音**

## 五、文字设计
- **位置**（画面上半/中央/下方）
- **字体/样式**
- **文字内容**（完整转写画面上的所有文字，含标签 #）
- **特殊要求**（动效/位移/颜色变化）

## 六、可调参数
- **镜头类型**（第一人称/第三人称）
- **手持抖动**（无/轻微/明显）
- **情绪标签**（搞怪/温柔/专业/种草/治愈/紧张 等）

要求：
- 用 markdown 格式输出
- 分镜表格每一秒都要有，不要跳秒
- 每个字段都要填，没看出来就写"未明显呈现"
- 直接输出 markdown，不要前后加任何解释"""


def _resolve_douyin_aweme_id(url: str):
    """从抖音长链/短链提取 aweme_id（数字串）"""
    m = re.search(r'/video/(\d+)', url)
    if m:
        return m.group(1)
    if 'v.douyin.com' in url:
        try:
            import requests
            r = requests.head(url, allow_redirects=True, timeout=10,
                              headers={"User-Agent": "Mozilla/5.0"})
            m = re.search(r'/video/(\d+)', r.url)
            if m:
                return m.group(1)
        except Exception as e:
            print(f"  [warn] 短链解析失败: {e}")
    return None


def _fetch_douyin_via_f2(aweme_id: str):
    """用 douyin-monitor 的 f2 + cookie 拿 CDN 直链 + 元数据"""
    import asyncio
    sys.path.insert(0, r'C:\Users\冯兴龙\douyin-monitor')
    from config import DOUYIN_COOKIE
    from f2.apps.douyin.crawler import DouyinCrawler
    from f2.apps.douyin.model import PostDetail

    async def _fetch():
        crawler = DouyinCrawler({"cookie": DOUYIN_COOKIE})
        params = PostDetail(aweme_id=aweme_id)
        result = await crawler.fetch_post_detail(params)
        if result.get("status_code") != 0:
            return None
        item = result.get("aweme_detail", {})
        urls = item.get("video", {}).get("play_addr", {}).get("url_list", [])
        return {
            "aweme_id": aweme_id,
            "desc": item.get("desc", ""),
            "play_url": urls[0] if urls else None,
            "duration_ms": item.get("duration", 0),
        }
    return asyncio.run(_fetch())


def download_video(url, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # 抖音走 f2（cookie + CDN 直链 不依赖 yt-dlp 的 douyin extractor）
    if "douyin.com" in url:
        print(f"[1/4] 抖音 走 f2 拿 CDN 直链: {url[:60]}")
        aweme_id = _resolve_douyin_aweme_id(url)
        if not aweme_id:
            raise RuntimeError(f"无法解析抖音 aweme_id: {url}")
        info = _fetch_douyin_via_f2(aweme_id)
        if not info or not info["play_url"]:
            raise RuntimeError(f"f2 没拿到视频直链（aweme_id={aweme_id}），可能需要更新 cookie")
        print(f"  → aweme_id={aweme_id}, desc={info['desc'][:50]}")
        out_path = os.path.join(out_dir, f"{aweme_id}.mp4")
        import requests
        # 抖音 CDN 防盗链：要带 Referer + 完整 UA + cookie
        sys.path.insert(0, r'C:\Users\冯兴龙\douyin-monitor')
        from config import DOUYIN_COOKIE
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Cookie": DOUYIN_COOKIE,
            "Range": "bytes=0-",
        }
        with requests.get(info["play_url"], stream=True, timeout=120, headers=headers) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(64 * 1024):
                    f.write(chunk)
        size_mb = os.path.getsize(out_path) / 1024 / 1024
        print(f"  → 已下载 {os.path.basename(out_path)} ({size_mb:.1f} MB)")
        return out_path
    # 非抖音（TikTok / B 站 / 快手等）走 yt-dlp
    out_template = os.path.join(out_dir, "%(id)s.%(ext)s")
    print(f"[1/4] yt-dlp 下载: {url[:60]}")
    r = subprocess.run(
        ["yt-dlp", "--no-warnings", "--no-playlist",
         "-f", "best[height<=1080]/best",
         "-o", out_template, url],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {(r.stderr or r.stdout)[:500]}")
    for ext in [".mp4", ".webm", ".mkv", ".mov"]:
        files = list(Path(out_dir).glob(f"*{ext}"))
        if files:
            print(f"  → {files[0].name}")
            return str(files[0])
    raise FileNotFoundError(f"video not downloaded in {out_dir}")


def extract_audio(video_path, out_dir):
    """ffmpeg 抽音频（mp3，单声道，16kHz Whisper 友好）"""
    audio_path = os.path.join(out_dir, "audio.mp3")
    print(f"[2a/5] ffmpeg 抽音频 ...")
    r = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000",
         "-q:a", "2", "-y", audio_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    if r.returncode != 0:
        print(f"  [warn] ffmpeg audio failed: {(r.stderr or '')[:200]}")
        return None
    return audio_path


def transcribe_audio(audio_path):
    """faster-whisper 转文字（中英文自动识别）"""
    if not audio_path or not os.path.exists(audio_path):
        return None
    print(f"[2b/5] Whisper 语音识别（首次会下载 base 模型 ~150MB）...")
    try:
        from faster_whisper import WhisperModel
        # base 模型够用 + 快；CPU int8 量化省内存
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
        # 拼成时间戳 + 台词
        lines = []
        full_text = []
        for seg in segments:
            lines.append(f"[{seg.start:.1f}-{seg.end:.1f}s] {seg.text.strip()}")
            full_text.append(seg.text.strip())
        if not lines:
            print(f"  → 未识别到语音（可能是纯穿搭/无口播视频）")
            return None
        result = "\n".join(lines)
        print(f"  → 识别到 {len(lines)} 段语音 / 语种: {info.language}")
        return {"timeline": result, "full_text": " ".join(full_text), "language": info.language}
    except Exception as e:
        print(f"  [warn] whisper failed: {e}")
        return None


def extract_frames(video_path, out_dir, fps=1):
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    # 清空旧帧
    for f in Path(frames_dir).glob("*.jpg"):
        f.unlink()
    print(f"[2/4] ffmpeg 抽帧（每秒 {fps} 张）...")
    r = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vf", f"fps={fps}",
         "-q:v", "2", "-y", os.path.join(frames_dir, "frame_%03d.jpg")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {(r.stderr or '')[:500]}")
    frames = sorted(Path(frames_dir).glob("*.jpg"))
    print(f"  → {len(frames)} 帧")
    return [str(f) for f in frames]


def analyze(frames, asr_result=None, max_frames=30):
    use = frames[:max_frames]
    print(f"[3/5] 豆包多模态分析 {len(use)} 帧 ...")
    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)

    # 把 ASR 结果注入到 prompt 里，让豆包整合"四、声音设计"那块
    asr_block = ""
    if asr_result:
        asr_block = (f"\n\n【附加信息：视频音频已通过 Whisper 识别，请整合到「四、声音设计」中】\n"
                     f"识别语种: {asr_result['language']}\n"
                     f"按时间戳的台词:\n{asr_result['timeline']}\n")

    full_prompt = PROMPT + asr_block

    content = [{"type": "text", "text": full_prompt}]
    for fp in use:
        with open(fp, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })
    resp = client.chat.completions.create(
        model=DOUBAO_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.3,
        max_tokens=4000,
    )
    return resp.choices[0].message.content


def save_local(title, body, video_url, out_dir):
    out_md = os.path.join(out_dir, "script.md")
    header = (f"# 视频脚本拆解 - {title}\n\n"
              f"**视频来源:** {video_url}\n"
              f"**分析工具:** 豆包多模态 + yt-dlp + ffmpeg\n\n---\n\n")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(header + body)
    return out_md


def write_to_table(record_id, body):
    """把拆解结果写回 27 表对应记录的「视频拆解」字段"""
    if not record_id:
        return False
    print(f"[4/5] 写回 27 表 record_id={record_id} 「视频拆解」字段 ...")
    # lark-cli base +record-upsert 要求直接 {field_name: value}，不要 fields wrapper
    payload = {"视频拆解": body}
    payload_path = os.path.join(TMP_DIR, "video-script-update.json")
    with open(payload_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    r = subprocess.run(
        [LARK_CLI, "base", "+record-upsert",
         "--base-token", BASE, "--table-id", TABLE_BLOGGERS,
         "--record-id", record_id,
         "--json", "@./video-script-update.json"],
        cwd=TMP_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
    )
    if r.returncode == 0:
        print(f"  ✓ 已写回单元格")
        return True
    print(f"  ✗ 写回失败: {(r.stderr or '')[:200]}")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--max-frames", type=int, default=30)
    ap.add_argument("--record-id", default=None,
                    help="27_对标博主视频监控 表的 record_id；给了就把拆解结果写回该单元格")
    ap.add_argument("--skip-asr", action="store_true", help="跳过 Whisper 语音识别（仅画面分析）")
    args = ap.parse_args()

    if not DOUBAO_API_KEY or not DOUBAO_MODEL:
        print("⚠ 未设置环境变量。先跑：")
        print('  $env:DOUBAO_API_KEY="..."; $env:DOUBAO_MODEL="..."')
        sys.exit(1)

    workdir = os.path.join(OUTPUT_DIR, str(abs(hash(args.url)) % 10**8))
    video = download_video(args.url, workdir)

    # ASR：抽音频 + Whisper 识别
    asr_result = None
    if not args.skip_asr:
        audio = extract_audio(video, workdir)
        asr_result = transcribe_audio(audio)

    # 抽帧 + 豆包分析
    frames = extract_frames(video, workdir, fps=1)
    body = analyze(frames, asr_result, args.max_frames)

    title = Path(video).stem
    md_path = save_local(title, body, args.url, workdir)
    print(f"[5/5] 本地保存: {md_path}")

    if args.record_id:
        write_to_table(args.record_id, body)

    print("\n" + "=" * 50)
    print(body[:800])
    print(("..." if len(body) > 800 else "") + f"\n\n完整 md: {md_path}")


if __name__ == "__main__":
    main()
