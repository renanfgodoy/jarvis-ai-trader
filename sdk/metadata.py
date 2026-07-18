from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def build_module_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ModuleMetadata:
    module: str
    author: str = "Friday AI Platform"
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fingerprint: str = ""
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        created_at = self.created_at
        updated_at = self.updated_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            object.__setattr__(self, "created_at", created_at)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
            object.__setattr__(self, "updated_at", updated_at)
        if not self.fingerprint:
            object.__setattr__(
                self,
                "fingerprint",
                build_module_fingerprint(
                    {
                        "module": self.module,
                        "author": self.author,
                        "version": self.version,
                        "tags": self.tags,
                    }
                ),
            )
