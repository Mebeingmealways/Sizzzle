import json
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app


def _redis_rest_url():
    url = (current_app.config.get('UPSTASH_REDIS_REST_URL') or '').strip()
    return url.rstrip('/')


def _redis_rest_token():
    # Support both names so existing deployments can provide either one.
    token = (current_app.config.get('UPSTASH_REDIS_REST_TOKEN') or '').strip()
    if token:
        return token
    return (current_app.config.get('UPSTASH_REDIS_API_KEY') or '').strip()


def redis_is_configured():
    return bool(_redis_rest_url() and _redis_rest_token())


def _request(path):
    url = f"{_redis_rest_url()}/{path}"
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f"Bearer {_redis_rest_token()}",
            'Accept': 'application/json',
            'User-Agent': 'Sizzzle-Backend/1.0',
        },
        method='GET',
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        raw = resp.read().decode('utf-8')
    return json.loads(raw) if raw else {}


def set_otp(key, code, ttl_seconds):
    if not redis_is_configured():
        return False
    try:
        key_q = urllib.parse.quote(str(key), safe='')
        code_q = urllib.parse.quote(str(code), safe='')
        ttl_q = urllib.parse.quote(str(int(ttl_seconds)), safe='')
        _request(f"set/{key_q}/{code_q}?EX={ttl_q}")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError, json.JSONDecodeError):
        return False


def get_otp(key):
    if not redis_is_configured():
        return None
    try:
        key_q = urllib.parse.quote(str(key), safe='')
        payload = _request(f"get/{key_q}")
        return payload.get('result')
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None


def delete_otp(key):
    if not redis_is_configured():
        return False
    try:
        key_q = urllib.parse.quote(str(key), safe='')
        payload = _request(f"del/{key_q}")
        return bool((payload or {}).get('result', 0))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return False
