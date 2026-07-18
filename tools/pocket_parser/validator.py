from __future__ import annotations

import json
from pathlib import Path

SENSITIVE_TERMS = ("token", "cookie", "authorization", "bearer", "ssid", "password", "user_id", "account_id")


def assert_report_is_sanitized(paths: tuple[Path, ...]) -> None:
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for term in SENSITIVE_TERMS:
            if term in text:
                raise ValueError(f"SENSITIVE_TERM_FOUND:{path}:{term}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

