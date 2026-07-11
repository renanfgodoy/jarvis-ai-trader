from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.market.pipeline import MarketPipeline
from app.market.pipeline.models import PipelineResult

FORBIDDEN_MARKERS = (
    "authorization",
    "bearer",
    "cookie",
    "credentials",
    "credential",
    "headers",
    "password",
    "refresh_token",
    "access_token",
    "ssid",
    "token",
)


@dataclass(frozen=True)
class RuntimeFeedResult:
    success: bool
    development_only: bool
    processed: int
    stored: int
    ignored: int
    updated: int
    unsupported: int
    rejected: int
    errors: tuple[str, ...]
    event_name: str | None


class ControlledMarketRuntimeFeed:
    """Development-only entrypoint for sanitized market messages."""

    def __init__(self, pipeline: MarketPipeline) -> None:
        self._pipeline = pipeline

    def feed(self, message: dict[str, Any]) -> RuntimeFeedResult:
        validation_errors = _validate_sanitized_message(message)
        if validation_errors:
            return RuntimeFeedResult(
                success=False,
                development_only=True,
                processed=0,
                stored=0,
                ignored=0,
                updated=0,
                unsupported=0,
                rejected=0,
                errors=validation_errors,
                event_name=None,
            )

        result = self._pipeline.process(message)
        return _from_pipeline_result(result)


def _from_pipeline_result(result: PipelineResult) -> RuntimeFeedResult:
    return RuntimeFeedResult(
        success=result.success,
        development_only=True,
        processed=result.processed,
        stored=result.stored,
        ignored=result.ignored,
        updated=result.updated,
        unsupported=result.unsupported,
        rejected=result.rejected,
        errors=tuple(error.message for error in result.errors),
        event_name=result.route_result.metadata.event_name,
    )


def _validate_sanitized_message(message: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(message, dict) or not message:
        return ("Runtime feed expects a non-empty sanitized JSON object.",)
    if _looks_like_har(message):
        errors.append("Raw HAR payloads are not accepted by the controlled runtime feed.")
    forbidden_path = _find_forbidden_marker(message)
    if forbidden_path:
        errors.append(f"Sensitive or private field is not accepted: {forbidden_path}.")
    return tuple(errors)


def _looks_like_har(message: dict[str, Any]) -> bool:
    log = message.get("log")
    return isinstance(log, dict) and isinstance(log.get("entries"), list)


def _find_forbidden_marker(value: Any, path: str = "$") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if any(marker in key_text for marker in FORBIDDEN_MARKERS):
                return child_path
            found = _find_forbidden_marker(child, child_path)
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _find_forbidden_marker(child, f"{path}[{index}]")
            if found:
                return found
    elif isinstance(value, str):
        text = value.lower()
        if any(marker in text for marker in FORBIDDEN_MARKERS):
            return path
    return None
