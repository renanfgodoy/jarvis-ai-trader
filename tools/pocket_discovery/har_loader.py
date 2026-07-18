from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.pocket_discovery.models import HarLoadResult


def load_har(path: str | Path) -> HarLoadResult:
    har_path = Path(path)
    if not har_path.exists():
        return HarLoadResult(path=str(har_path), exists=False, size_bytes=0, valid_json=False, entry_count=0, error="HAR_NOT_FOUND")
    size_bytes = har_path.stat().st_size
    try:
        payload = json.loads(har_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        try:
            payload = json.loads(har_path.read_text(encoding="utf-8-sig"))
        except Exception as error:  # noqa: BLE001 - report sanitized load failure only.
            return HarLoadResult(path=str(har_path), exists=True, size_bytes=size_bytes, valid_json=False, entry_count=0, error=type(error).__name__)
    except json.JSONDecodeError as error:
        return HarLoadResult(path=str(har_path), exists=True, size_bytes=size_bytes, valid_json=False, entry_count=0, error=f"JSON_DECODE_ERROR:{error.msg}")

    entries = _entries(payload)
    return HarLoadResult(path=str(har_path), exists=True, size_bytes=size_bytes, valid_json=True, entry_count=len(entries), har=payload)


def har_entries(har: dict[str, Any]) -> list[dict[str, Any]]:
    return _entries(har)


def _entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries = payload.get("log", {}).get("entries", [])
    return entries if isinstance(entries, list) else []
