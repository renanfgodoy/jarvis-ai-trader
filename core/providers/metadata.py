from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def normalize_provider_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    json.dumps(metadata, ensure_ascii=False, sort_keys=True, default=str)
    return dict(metadata)


def build_provider_fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
