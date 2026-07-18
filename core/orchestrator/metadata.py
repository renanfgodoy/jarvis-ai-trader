from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from core.orchestrator.models import ExecutionMetadata, ExecutionStatus


def build_execution_fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_execution_metadata(
    *,
    request_id: str,
    module: str,
    pipeline_version: str,
    status: ExecutionStatus,
    started_at: datetime,
    finished_at: datetime | None = None,
    provider: str | None = None,
    provider_version: str | None = None,
    identity: str | None = None,
) -> ExecutionMetadata:
    finished = finished_at or datetime.now(timezone.utc)
    duration = (finished - started_at).total_seconds() if finished and started_at else None
    fingerprint = build_execution_fingerprint(
        {
            "request_id": request_id,
            "module": module,
            "provider": provider,
            "provider_version": provider_version,
            "identity": identity,
            "pipeline_version": pipeline_version,
            "status": status,
        }
    )
    return ExecutionMetadata(
        execution_id=str(uuid4()),
        request_id=request_id,
        started_at=started_at,
        finished_at=finished,
        duration=duration,
        provider=provider,
        provider_version=provider_version,
        identity=identity,
        module=module,
        pipeline_version=pipeline_version,
        fingerprint=fingerprint,
        status=status,
    )
