from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTED = "[REDACTED]"
REDACTED_KEY = "[REDACTED_KEY]"

SENSITIVE_KEYWORDS = (
    "authorization",
    "bearer",
    "cookie",
    "credential",
    "email",
    "jwt",
    "password",
    "refresh",
    "secret",
    "session",
    "ssid",
    "token",
    "user_id",
    "userid",
    "account_id",
    "accountid",
)

SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"bearer\s+[a-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"[a-z0-9_\-]{20,}\.[a-z0-9_\-]{20,}\.[a-z0-9_\-]{10,}", re.IGNORECASE),
    re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE),
)


def sanitize(value: Any, *, max_string: int = 240) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if is_sensitive_key(key_text):
                sanitized[REDACTED_KEY] = REDACTED
            else:
                sanitized[key_text] = sanitize(item, max_string=max_string)
        return sanitized
    if isinstance(value, tuple):
        return tuple(sanitize(item, max_string=max_string) for item in value)
    if isinstance(value, list):
        return [sanitize(item, max_string=max_string) for item in value[:20]]
    if isinstance(value, str):
        return sanitize_string(value, max_string=max_string)
    return value


def sanitize_string(value: str, *, max_string: int = 240) -> str:
    text = value.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    for pattern in SENSITIVE_VALUE_PATTERNS:
        text = pattern.sub(REDACTED, text)
    if len(text) > max_string:
        return f"{text[:max_string]}..."
    return text


def sanitize_url(url: str) -> str:
    parsed = urlsplit(url)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        query.append((REDACTED_KEY if is_sensitive_key(key) else key, REDACTED if is_sensitive_key(key) else sanitize_string(value, max_string=80)))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), ""))


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def payload_shape(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {_safe_key(str(key)): payload_shape(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not value:
            return []
        return [payload_shape(value[0])]
    if value is None:
        return "null"
    return type(value).__name__


def payload_keys(value: Any) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        return tuple(sorted(_safe_key(str(key)) for key in value.keys()))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        keys: set[str] = set()
        for item in value:
            if isinstance(item, Mapping):
                keys.update(str(key) for key in item.keys())
        return tuple(sorted(_safe_key(key) for key in keys))
    return ()


def _safe_key(key: str) -> str:
    return REDACTED_KEY if is_sensitive_key(key) else key
