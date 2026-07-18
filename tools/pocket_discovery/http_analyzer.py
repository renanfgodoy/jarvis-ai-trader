from __future__ import annotations

import json
from urllib.parse import urlsplit

from tools.pocket_discovery.har_loader import har_entries
from tools.pocket_discovery.models import HttpEndpointSummary
from tools.pocket_discovery.sanitizer import payload_shape, sanitize

HTTP_MARKERS = {
    "assets": "assets",
    "candles": "candles",
    "chart": "chart",
    "history": "history",
    "quotes": "quotes",
    "payout": "payout",
    "profit": "payout",
    "auth": "auth",
    "session": "session",
    "profile": "profile",
    "account": "account",
}


def analyze_http_endpoints(har_path: str, har: dict) -> tuple[HttpEndpointSummary, ...]:
    endpoints: list[HttpEndpointSummary] = []
    for entry in har_entries(har):
        request = entry.get("request", {})
        url = str(request.get("url", ""))
        if url.startswith(("ws://", "wss://")) or entry.get("_webSocketMessages"):
            continue
        if _is_static_asset(url, entry.get("response", {})):
            continue
        responsibility = _probable_responsibility(url)
        if responsibility == "other":
            continue
        parsed_url = urlsplit(url)
        response = entry.get("response", {})
        endpoints.append(
            HttpEndpointSummary(
                har_path=har_path,
                host=parsed_url.netloc,
                path=parsed_url.path,
                method=str(request.get("method", "GET")),
                status=response.get("status") if isinstance(response.get("status"), int) else None,
                content_type=_content_type(response),
                response_shape=_response_shape(response),
                probable_responsibility=responsibility,
            )
        )
    return tuple(endpoints)


def _probable_responsibility(url: str) -> str:
    lower = url.lower()
    for marker, responsibility in HTTP_MARKERS.items():
        if marker in lower:
            return responsibility
    return "other"


def _is_static_asset(url: str, response: dict) -> bool:
    path = urlsplit(url).path.lower()
    if path.endswith((".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".css", ".js", ".woff", ".woff2", ".ttf")):
        return True
    content_type = (_content_type(response) or "").lower()
    return content_type.startswith(("image/", "font/", "text/css", "application/javascript", "text/javascript"))


def _content_type(response: dict) -> str | None:
    for header in response.get("headers", []) or []:
        if str(header.get("name", "")).lower() == "content-type":
            return sanitize(str(header.get("value", "")), max_string=120)
    return None


def _response_shape(response: dict) -> object:
    text = response.get("content", {}).get("text")
    if not isinstance(text, str) or not text:
        return None
    try:
        return payload_shape(json.loads(text))
    except json.JSONDecodeError:
        return "text"
