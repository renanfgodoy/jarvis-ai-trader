from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any


class VisionDiagnostics:
    path_json = Path(".jarvis_cache/diagnostics/friday_vision_v1_analysis.json")
    path_txt = Path(".jarvis_cache/diagnostics/friday_vision_v1_analysis.txt")

    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[dict[str, Any]] = []

    def record(self, event: dict[str, Any]) -> None:
        sanitized = {key: value for key, value in event.items() if key not in {"image", "base64", "api_key", "prompt", "raw_response"}}
        with self._lock:
            self._events.append(sanitized)
            self._events = self._events[-100:]
            self._write()

    def _write(self) -> None:
        self.path_json.parent.mkdir(parents=True, exist_ok=True)
        payload = {"events": self._events}
        self.path_json.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        lines = ["Friday Vision V1 Analysis Diagnostics", ""]
        for event in self._events[-20:]:
            fields = ", ".join(f"{key}={value}" for key, value in event.items())
            lines.append(fields)
        self.path_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")


vision_diagnostics = VisionDiagnostics()
