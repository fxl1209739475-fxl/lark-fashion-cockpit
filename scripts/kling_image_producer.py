"""可灵 AI 文生图（淘宝主图风格模特图）

复用 douyin-monitor/config.py 的 KLING_ACCESS_KEY / KLING_SECRET_KEY
端点：POST /v1/images/generations
"""

import os
import sys
import time
import argparse
import httpx

sys.path.insert(0, r"C:\Users\冯兴龙\douyin-monitor")
from config import KLING_ACCESS_KEY, KLING_SECRET_KEY  # type: ignore

KLING_API_BASE = "https://api-beijing.klingai.com"
OUT_DIR = r"C:\Users\冯兴龙\lark-fashion-cockpit\assets\products"


def _make_jwt(access_key: str, secret_key: str) -> str:
    import jwt as pyjwt
    return pyjwt.encode(
        {"iss": access_key, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5},
        secret_key,
        headers={"alg": "HS256", "typ": "JWT"},
    )


def _headers():
    return {
        "Authorization": f"Bearer {_make_jwt(KLING_ACCESS_KEY, KLING_SECRET_KEY)}",
        "Content-Type": "application/json",
    }


def submit(prompt: str, aspect_ratio="3:4", n=1, model="kling-v1"):
    payload = {
        "model_name": model,
        "prompt": prompt,
        "negative_prompt": "low quality, blurry, distorted, deformed hands, watermark, text, logo, cartoon, painting",
        "n": n,
        "aspect_ratio": aspect_ratio,
    }
    r = httpx.post(f"{KLING_API_BASE}/v1/images/generations", headers=_headers(), json=payload, timeout=30)
    if r.status_code != 200:
        print(f"  HTTP {r.status_code}: {r.text}")
        r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"submit failed: {data}")
    return data["data"]["task_id"]


def poll(task_id: str, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = httpx.get(f"{KLING_API_BASE}/v1/images/generations/{task_id}", headers=_headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 0:
            raise RuntimeError(f"poll failed: {data}")
        status = data["data"]["task_status"]
        if status == "succeed":
            imgs = data["data"]["task_result"]["images"]
            return [img["url"] for img in imgs]
        if status == "failed":
            raise RuntimeError(f"task failed: {data['data'].get('task_status_msg')}")
        print(f"  ... status={status}, waiting 8s")
        time.sleep(8)
    raise TimeoutError(f"task {task_id} timeout")


def download(url: str, out_path: str):
    r = httpx.get(url, timeout=60, follow_redirects=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return os.path.getsize(out_path)


# 元素 → prompt 模板
PROMPTS = {
    "DRS-0429-FL": {
        "prompt": "Fashion editorial photo, full body shot of an Asian female model in her late 20s wearing a French-style cream beige floral midi dress with V-neck and waist tie, light chiffon fabric flowing naturally, standing pose facing the camera, plain pure white studio background, even soft studio lighting from front, taobao e-commerce main image style, lookbook fashion photography, high resolution 4K, professional product photography, no shadows on background",
        "name": "法式碎花连衣裙",
    },
    "KNT-0402-CD": {
        "prompt": "Fashion editorial photo, full body shot of an Asian female model in her late 20s wearing a short caramel brown knit cardigan over a white tank top with denim jeans, soft chunky knit texture clearly visible, standing pose facing camera, plain pure white studio background, even soft studio lighting from front, taobao e-commerce main image style, lookbook fashion photography, high resolution 4K, professional product photography, no shadows on background",
        "name": "焦糖针织开衫",
    },
    "PNT-0418-SU": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing high-waist black tailored office trousers with a fitted ivory blouse, professional commute style, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, lookbook photography, 4K, no shadows",
        "name": "通勤西装裤",
    },
    "SHT-0420-SP": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing light sea-salt blue lightweight UV protection blouse with white pleated skirt, summer Korean style, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, 4K, no shadows",
        "name": "海盐蓝防晒衬衫",
    },
    "SKT-0328-A": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing high-waist gray A-line midi skirt with tucked-in white knit top, professional and feminine, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, 4K, no shadows",
        "name": "灰色A字半身裙",
    },
    "KNT-2024-WL": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing oversized cream beige knit sweater with light wash jeans, Korean cozy style, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, 4K, no shadows",
        "name": "韩系奶油针织毛衣",
    },
    "DRS-2024-LC": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing French-style berry red lace slip dress with delicate lace trim, satin texture, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, lookbook photography, 4K, no shadows",
        "name": "法式蕾丝吊带连衣裙",
    },
    "OUT-2024-OL": {
        "prompt": "Fashion editorial photo, full body shot of Asian female model in late 20s wearing a sharp tailored black minimalist OL blazer over white blouse with matching trousers, professional power suit style, standing pose facing camera, pure white studio background, soft even lighting, taobao e-commerce main image style, 4K, no shadows",
        "name": "OL极简西服",
    },
}


def gen_one(sku: str):
    if sku not in PROMPTS:
        print(f"  ❌ no prompt for {sku}")
        return None
    p = PROMPTS[sku]
    print(f"\n=== {sku} · {p['name']} ===")
    print(f"  Prompt: {p['prompt'][:120]}...")
    print("  Submitting to Kling...")
    task_id = submit(p["prompt"])
    print(f"  task_id = {task_id}")
    print("  Polling...")
    urls = poll(task_id)
    print(f"  Got {len(urls)} image(s)")

    out_path = os.path.join(OUT_DIR, f"{sku}.kling.jpg")
    backup_path = os.path.join(OUT_DIR, f"{sku}.placeholder.jpg")
    orig_path = os.path.join(OUT_DIR, f"{sku}.jpg")

    # backup placeholder
    if os.path.exists(orig_path) and not os.path.exists(backup_path):
        import shutil
        shutil.copy(orig_path, backup_path)
        print(f"  Backed up placeholder -> {backup_path}")

    size = download(urls[0], out_path)
    print(f"  Downloaded -> {out_path}  ({size} bytes)")

    # also overwrite the .jpg so gen-outfit-image.py uses it
    import shutil
    shutil.copy(out_path, orig_path)
    print(f"  Activated as -> {orig_path}")

    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("skus", nargs="+", help="SKUs to generate (e.g. DRS-0429-FL KNT-0402-CD)")
    args = ap.parse_args()

    for sku in args.skus:
        try:
            gen_one(sku)
        except Exception as e:
            print(f"  [FAIL] {sku}: {e}")

    print("\nDone.")
