"""企业微信 API 客户端 — access_token 获取 + 缓存 + 通用 API 调用

被其他脚本 import：
  from wecom_client import WecomClient
  c = WecomClient()
  data = c.get('externalcontact/list', {'userid': 'xxx'})
"""

import os, sys, json, time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass


WECOM_BASE = "https://qyapi.weixin.qq.com/cgi-bin"
TOKEN_CACHE = Path(os.path.expanduser("~")) / ".cache" / "lark-cockpit" / "wecom-tokens.json"


class WecomClient:
    def __init__(self, corp_id: str = None, secret: str = None, secret_kind: str = "agent"):
        self.corp_id = corp_id or os.environ.get("WECOM_CORP_ID", "")
        if secret_kind == "contact":
            self.secret = secret or os.environ.get("WECOM_CONTACT_SECRET", "")
        else:
            self.secret = secret or os.environ.get("WECOM_AGENT_SECRET", "")
        self.secret_kind = secret_kind
        if not self.corp_id or not self.secret:
            raise RuntimeError(f"缺 WECOM_CORP_ID 或 WECOM_{secret_kind.upper()}_SECRET")

    def _cache_key(self) -> str:
        return f"{self.corp_id}:{self.secret_kind}"

    def _load_cache(self) -> dict:
        if not TOKEN_CACHE.exists():
            return {}
        try:
            return json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_cache(self, cache: dict):
        TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

    def get_access_token(self) -> str:
        """拿 access_token，带本地缓存（有效期 7200s，提前 5 分钟刷新）"""
        cache = self._load_cache()
        key = self._cache_key()
        entry = cache.get(key)
        if entry and entry.get("expires_at", 0) > time.time() + 300:
            return entry["token"]

        r = requests.get(f"{WECOM_BASE}/gettoken",
                          params={"corpid": self.corp_id, "corpsecret": self.secret},
                          timeout=10)
        d = r.json()
        if d.get("errcode") != 0:
            raise RuntimeError(f"gettoken 失败: {d}")
        token = d["access_token"]
        cache[key] = {"token": token, "expires_at": time.time() + d.get("expires_in", 7200)}
        self._save_cache(cache)
        return token

    def get(self, path: str, params: dict = None) -> dict:
        params = dict(params or {})
        params["access_token"] = self.get_access_token()
        r = requests.get(f"{WECOM_BASE}/{path}", params=params, timeout=15)
        return r.json()

    def post(self, path: str, json_body: dict, params: dict = None) -> dict:
        params = dict(params or {})
        params["access_token"] = self.get_access_token()
        r = requests.post(f"{WECOM_BASE}/{path}", params=params, json=json_body, timeout=15)
        return r.json()


def main():
    print("=== WecomClient 自检 ===\n")
    try:
        c = WecomClient(secret_kind="agent")
    except RuntimeError as e:
        print(f"❌ {e}")
        print("配置 .env：WECOM_CORP_ID / WECOM_AGENT_SECRET")
        sys.exit(1)
    try:
        token = c.get_access_token()
        print(f"✓ Agent access_token: {token[:30]}... (cached at {TOKEN_CACHE})")
    except Exception as e:
        print(f"❌ 拿 token 失败: {e}")
        sys.exit(2)

    try:
        c2 = WecomClient(secret_kind="contact")
        token2 = c2.get_access_token()
        print(f"✓ Contact access_token: {token2[:30]}...")
    except RuntimeError as e:
        print(f"⚠ Contact secret 未配（如不需要客户联系功能可忽略）: {e}")


if __name__ == "__main__":
    main()
