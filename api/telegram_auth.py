"""Telegram Mini App initData verification (HMAC-SHA256, freshness, strict parsing)."""
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

def verify_init_data(raw: str, bot_token: str, max_age_seconds: int = 3600):
    if not raw or not bot_token or len(raw) > 8192:
        return None
    try:
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
        data = dict(pairs)
        if len(pairs) != len(data):
            return None
        received_hash = data.pop("hash", "")
        if len(received_hash) != 64:
            return None
        timestamp = int(data["auth_date"])
        now = int(time.time())
        if timestamp > now + 60 or now - timestamp > max_age_seconds:
            return None
        check = "\n".join(f"{k}={v}" for k,v in sorted(data.items()))
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, received_hash):
            return None
        user = json.loads(data["user"])
        if not isinstance(user, dict) or not isinstance(user.get("id"), int):
            return None
        return user
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None
