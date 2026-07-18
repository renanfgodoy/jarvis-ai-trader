from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.live_history_trace import socket_rows
from app.market.providers.pocket.multi_context_validation import build_bucket_isolation_report, validate_multi_context_source
from tools.pocket_parser.validator import assert_report_is_sanitized

REPORT_JSON = Path(".jarvis_cache/diagnostics/pocket_runtime_architecture_report.json")
REPORT_TXT = Path(".jarvis_cache/diagnostics/pocket_runtime_architecture_report.txt")
LIVE_OBSERVATION_JSON = Path(".jarvis_cache/diagnostics/pocket_live_observation_report.json")
LIVE_OBSERVATION_TXT = Path(".jarvis_cache/diagnostics/pocket_live_observation_report.txt")
SOCKET_OBSERVATION_JSON = Path(".jarvis_cache/diagnostics/pocket_socket_observation_report.json")
SOCKET_OBSERVATION_TXT = Path(".jarvis_cache/diagnostics/pocket_socket_observation_report.txt")
LIVE_CONTEXT_JSON = Path(".jarvis_cache/diagnostics/pocket_live_context_report.json")
LIVE_CONTEXT_TXT = Path(".jarvis_cache/diagnostics/pocket_live_context_report.txt")
REAL_VALIDATION_JSON = Path(".jarvis_cache/diagnostics/pocket_real_validation.json")
REAL_VALIDATION_TXT = Path(".jarvis_cache/diagnostics/pocket_real_validation.txt")
LIVE_STREAM_SCHEMA_JSON = Path(".jarvis_cache/diagnostics/pocket_live_stream_schema.json")
LIVE_STREAM_SCHEMA_TXT = Path(".jarvis_cache/diagnostics/pocket_live_stream_schema.txt")
CHAFOR_SCHEMA_JSON = Path(".jarvis_cache/diagnostics/pocket_chafor_schema.json")
CHAFOR_SCHEMA_TXT = Path(".jarvis_cache/diagnostics/pocket_chafor_schema.txt")
LIVE_HISTORY_ABSENCE_JSON = Path(".jarvis_cache/diagnostics/pocket_live_history_absence.json")
LIVE_HISTORY_ABSENCE_TXT = Path(".jarvis_cache/diagnostics/pocket_live_history_absence.txt")
LIVE_HISTORY_TRACE_JSON = Path(".jarvis_cache/diagnostics/pocket_live_history_trace.json")
LIVE_HISTORY_TRACE_TXT = Path(".jarvis_cache/diagnostics/pocket_live_history_trace.txt")
LIVE_PERIOD_TRACE_JSON = Path(".jarvis_cache/diagnostics/pocket_live_period_trace.json")
LIVE_PERIOD_TRACE_TXT = Path(".jarvis_cache/diagnostics/pocket_live_period_trace.txt")
LIVE_HTTP_HISTORY_TRACE_JSON = Path(".jarvis_cache/diagnostics/pocket_live_http_history_trace.json")
LIVE_HTTP_HISTORY_TRACE_TXT = Path(".jarvis_cache/diagnostics/pocket_live_http_history_trace.txt")
MULTI_CONTEXT_VALIDATION_JSON = Path(".jarvis_cache/diagnostics/pocket_multi_context_validation.json")
MULTI_CONTEXT_VALIDATION_TXT = Path(".jarvis_cache/diagnostics/pocket_multi_context_validation.txt")
BUCKET_ISOLATION_JSON = Path(".jarvis_cache/diagnostics/pocket_bucket_isolation_report.json")
BUCKET_ISOLATION_TXT = Path(".jarvis_cache/diagnostics/pocket_bucket_isolation_report.txt")


def write_runtime_architecture_report(source: PocketReadOnlyLiveSource) -> dict:
    payload = source.status()
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT_TXT.write_text(_text(payload), encoding="utf-8")
    assert_report_is_sanitized((REPORT_JSON, REPORT_TXT))
    return payload


def _text(payload: dict) -> str:
    runtime = payload.get("runtime", {})
    metrics = runtime.get("metrics", {})
    lines = [
        "Pocket Read-Only Runtime Architecture",
        f"transport={payload.get('transport', {}).get('transport')}",
        f"running={runtime.get('running')}",
        f"connection_state={runtime.get('connection_state')}",
        f"events_received={metrics.get('events_received')}",
        f"events_routed={payload.get('events_routed')}",
        f"history_batches={metrics.get('history_batches')}",
        f"historical_candles={metrics.get('historical_candles_written')}",
        f"realtime_ticks={metrics.get('ticks_processed')}",
        f"realtime_candles_created={metrics.get('realtime_candles_created')}",
        f"realtime_candles_updated={metrics.get('realtime_candles_updated')}",
        f"buckets={runtime.get('buckets')}",
        f"readiness={runtime.get('readiness')}",
        f"unknown_events={runtime.get('unknown_events')}",
        f"guard_blocks={runtime.get('guard_blocks')}",
        f"last_error={runtime.get('last_error')}",
    ]
    return "\n".join(lines)


def write_live_observation_reports(source: PocketReadOnlyLiveSource, metadata: dict | None = None) -> dict:
    metadata = metadata or {}
    status = source.status()
    transport = source.transport
    runtime = status.get("runtime", {})
    metrics = runtime.get("metrics", {})
    observation = {
        "observation_mode": metadata.get("observation_mode", "FAKE_CDP_ONLY"),
        "real_observation_authorized": bool(metadata.get("real_observation_authorized", False)),
        "cdp_port": metadata.get("cdp_port"),
        "chrome_started": bool(metadata.get("chrome_started", False)),
        "real_target_observed": bool(metadata.get("real_target_observed", False)),
        "observer_started": True,
        "target_found": status.get("transport", {}).get("target_found"),
        "target_url_sanitized": status.get("transport", {}).get("target_url_sanitized"),
        "sockets_observed": status.get("transport", {}).get("sockets_observed"),
        "socket_candidates": _socket_candidates(transport),
        "market_socket_found": status.get("transport", {}).get("market_socket_found"),
        "market_socket_reason": _market_socket_reason(transport),
        "frames_sent_observed": status.get("transport", {}).get("frames_sent_observed"),
        "frames_received_observed": status.get("transport", {}).get("frames_received_observed"),
        "events_parsed": status.get("transport", {}).get("market_events_received"),
        "change_symbol_events": getattr(transport, "change_symbol_events", 0),
        "history_batches": metrics.get("history_batches"),
        "historical_candles": metrics.get("historical_candles_written"),
        "stream_events": getattr(transport, "stream_events", 0),
        "ticks": metrics.get("ticks_processed"),
        "asset_catalog_events": getattr(transport, "asset_catalog_events", 0),
        "contexts_published": getattr(transport, "contexts_published", 0),
        "buckets_created": runtime.get("buckets"),
        "readiness": runtime.get("readiness"),
        "sensitive_events_discarded": status.get("transport", {}).get("sensitive_events_discarded"),
        "non_market_frames_ignored": getattr(transport, "non_market_frames_ignored", 0),
        "unknown_events": runtime.get("unknown_events"),
        "payload_shapes": getattr(transport, "payload_shapes", {}),
        "errors": getattr(transport, "errors", []),
        "outbound_messages_originated_by_friday": 0,
        "observer_stopped_cleanly": runtime.get("connection_state") == "STOPPED" and status.get("transport", {}).get("running") is False,
    }
    socket_report = {"sockets": _socket_report(transport)}
    context = runtime.get("current_context", {})
    bucket_key = None
    if context.get("asset") and context.get("period"):
        bucket_key = f"POCKET:{context['asset']}:{context['period']}"
    context_report = {
        "old_asset": None,
        "new_asset": context.get("asset"),
        "old_period": None,
        "new_period": context.get("period"),
        "timeframe": context.get("timeframe"),
        "origin": "CDP_OBSERVATION",
        "reason": "ATOMIC_CONTEXT_FROM_ALLOWED_MARKET_EVENT" if context.get("asset") and context.get("period") else "NO_CONTEXT_PUBLISHED",
        "bucket_key": bucket_key,
        "bucket_exists": bucket_key in (runtime.get("buckets") or {}) if bucket_key else False,
        "history_count": context.get("history_count"),
        "readiness": context.get("history_state"),
        "timestamp": context.get("last_update"),
    }
    _write_pair(LIVE_OBSERVATION_JSON, LIVE_OBSERVATION_TXT, observation, "Pocket Live Observation")
    _write_pair(SOCKET_OBSERVATION_JSON, SOCKET_OBSERVATION_TXT, socket_report, "Pocket Socket Observation")
    _write_pair(LIVE_CONTEXT_JSON, LIVE_CONTEXT_TXT, context_report, "Pocket Live Context")
    assert_report_is_sanitized(
        (
            LIVE_OBSERVATION_JSON,
            LIVE_OBSERVATION_TXT,
            SOCKET_OBSERVATION_JSON,
            SOCKET_OBSERVATION_TXT,
            LIVE_CONTEXT_JSON,
            LIVE_CONTEXT_TXT,
        )
    )
    return observation


def write_real_validation_report(source: PocketReadOnlyLiveSource, metadata: dict | None = None) -> dict:
    metadata = metadata or {}
    status = source.status()
    transport = source.transport
    runtime = status.get("runtime", {})
    metrics = runtime.get("metrics", {})
    market_socket = _market_socket(transport)
    buckets = runtime.get("buckets") or {}
    context = runtime.get("current_context") or {}
    payload = {
        "observation_mode": metadata.get("observation_mode", "REAL_PASSIVE_CDP"),
        "target_found": status.get("transport", {}).get("target_found"),
        "market_socket_found": status.get("transport", {}).get("market_socket_found"),
        "socket_url": market_socket.url_sanitized if market_socket else None,
        "events_found": sorted(market_socket.event_names) if market_socket else [],
        "payload_shapes": getattr(transport, "payload_shapes", {}),
        "history_batches": metrics.get("history_batches"),
        "historical_candles": metrics.get("historical_candles_written"),
        "stream_events": getattr(transport, "stream_events", 0),
        "ticks": metrics.get("ticks_processed"),
        "candles": sum(int(count) for count in buckets.values()),
        "assets": int(runtime.get("asset_catalog_count") or 0),
        "periods": _periods_from_buckets(buckets),
        "readiness": runtime.get("readiness"),
        "current_asset": context.get("asset"),
        "current_period": context.get("period"),
        "observer_stopped_cleanly": runtime.get("connection_state") == "STOPPED" and status.get("transport", {}).get("running") is False,
        "outbound_messages_originated_by_friday": 0,
    }
    if isinstance(transport, PocketCDPObservationTransport):
        payload["history_category"] = transport.live_history_trace.final_category()
        payload["period_source"] = transport.live_period_trace.final_period_source()
        payload["atomic_context_classification"] = transport.live_period_trace.context_classification()
    _write_pair(REAL_VALIDATION_JSON, REAL_VALIDATION_TXT, payload, "Pocket Real Passive CDP Validation")
    assert_report_is_sanitized((REAL_VALIDATION_JSON, REAL_VALIDATION_TXT))
    return payload


def write_live_schema_trace_reports(source: PocketReadOnlyLiveSource) -> dict:
    transport = source.transport
    if not isinstance(transport, PocketCDPObservationTransport):
        stream = {"event_name": "updateStream", "samples_count": 0, "compatibility": "INSUFFICIENT_EVIDENCE"}
        chafor = {"event_name": "chafor", "samples_count": 0, "classification": "UNKNOWN"}
        history = {"category": "HISTORY_EVENT_UNKNOWN"}
    else:
        trace = transport.live_schema_trace
        stream = trace.update_stream_report()
        chafor = trace.chafor_report()
        history = trace.history_absence_report(market_socket_found=transport.market_socket_request_id is not None)
    _write_pair(LIVE_STREAM_SCHEMA_JSON, LIVE_STREAM_SCHEMA_TXT, stream, "Pocket Live updateStream Schema")
    _write_pair(CHAFOR_SCHEMA_JSON, CHAFOR_SCHEMA_TXT, chafor, "Pocket chafor Schema")
    _write_pair(LIVE_HISTORY_ABSENCE_JSON, LIVE_HISTORY_ABSENCE_TXT, history, "Pocket Live History Absence")
    assert_report_is_sanitized(
        (
            LIVE_STREAM_SCHEMA_JSON,
            LIVE_STREAM_SCHEMA_TXT,
            CHAFOR_SCHEMA_JSON,
            CHAFOR_SCHEMA_TXT,
            LIVE_HISTORY_ABSENCE_JSON,
            LIVE_HISTORY_ABSENCE_TXT,
        )
    )
    return {"stream": stream, "chafor": chafor, "history": history}


def write_live_history_period_trace_reports(source: PocketReadOnlyLiveSource) -> dict:
    transport = source.transport
    if not isinstance(transport, PocketCDPObservationTransport):
        history = {"final_category": "HISTORY_EVENT_UNKNOWN", "timing": {}}
        period = {"final_period_source": "UNKNOWN", "context_classification": "UNKNOWN"}
        http = {"candidate_count": 0, "candidates": []}
        sockets = {"sockets": []}
    else:
        history = transport.live_history_trace.history_report()
        period = transport.live_period_trace.report()
        http = transport.live_history_trace.http_report()
        sockets = {"socket_audit": socket_rows(transport.live_history_trace.socket_report())}
        history["socket_audit"] = sockets["socket_audit"]
    _write_pair(LIVE_HISTORY_TRACE_JSON, LIVE_HISTORY_TRACE_TXT, history, "Pocket Live History Trace")
    _write_pair(LIVE_PERIOD_TRACE_JSON, LIVE_PERIOD_TRACE_TXT, period, "Pocket Live Period Trace")
    _write_pair(LIVE_HTTP_HISTORY_TRACE_JSON, LIVE_HTTP_HISTORY_TRACE_TXT, http, "Pocket Live HTTP History Trace")
    assert_report_is_sanitized(
        (
            LIVE_HISTORY_TRACE_JSON,
            LIVE_HISTORY_TRACE_TXT,
            LIVE_PERIOD_TRACE_JSON,
            LIVE_PERIOD_TRACE_TXT,
            LIVE_HTTP_HISTORY_TRACE_JSON,
            LIVE_HTTP_HISTORY_TRACE_TXT,
        )
    )
    return {"history": history, "period": period, "http": http, "sockets": sockets}


def write_multi_context_validation_reports(source: PocketReadOnlyLiveSource) -> dict:
    validation = validate_multi_context_source(source)
    isolation = build_bucket_isolation_report(source.runtime)
    _write_pair(MULTI_CONTEXT_VALIDATION_JSON, MULTI_CONTEXT_VALIDATION_TXT, validation, "Pocket Multi Context Validation")
    _write_pair(BUCKET_ISOLATION_JSON, BUCKET_ISOLATION_TXT, isolation, "Pocket Bucket Isolation")
    assert_report_is_sanitized((MULTI_CONTEXT_VALIDATION_JSON, MULTI_CONTEXT_VALIDATION_TXT, BUCKET_ISOLATION_JSON, BUCKET_ISOLATION_TXT))
    return {"validation": validation, "isolation": isolation}


def _write_pair(json_path: Path, txt_path: Path, payload: dict, title: str) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    txt_path.write_text(_plain_text(title, payload), encoding="utf-8")


def _plain_text(title: str, payload: dict) -> str:
    lines = [title]
    for key, value in payload.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)


def _socket_candidates(transport: object) -> list[str]:
    if not isinstance(transport, PocketCDPObservationTransport):
        return []
    return [socket.request_id for socket in transport.sockets.values() if socket.classification in {"CANDIDATE", "MARKET_SOCKET"}]


def _market_socket_reason(transport: object) -> str | None:
    if not isinstance(transport, PocketCDPObservationTransport) or transport.market_socket_request_id is None:
        return None
    socket = transport.sockets.get(transport.market_socket_request_id)
    return socket.classification_reason if socket else None


def _socket_report(transport: object) -> list[dict]:
    if not isinstance(transport, PocketCDPObservationTransport):
        return []
    rows = []
    for socket in transport.sockets.values():
        rows.append(
            {
                "sanitized_host": socket.host,
                "sanitized_path": socket.path,
                "target_id_masked": _mask(socket.target_id),
                "request_id_masked": _mask(socket.request_id),
                "frames_sent_count": socket.frames_sent_count,
                "frames_received_count": socket.frames_received_count,
                "event_names": sorted(event for event in socket.event_names if event not in {"auth", "auth/success"}),
                "classification": socket.classification,
                "classification_reason": socket.classification_reason,
            }
        )
    return rows


def _market_socket(transport: object):
    if not isinstance(transport, PocketCDPObservationTransport) or transport.market_socket_request_id is None:
        return None
    return transport.sockets.get(transport.market_socket_request_id)


def _periods_from_buckets(buckets: dict) -> list[int]:
    periods = set()
    for key in buckets:
        parts = str(key).split(":")
        if len(parts) == 3:
            try:
                periods.add(int(parts[2]))
            except ValueError:
                continue
    return sorted(periods)




def _mask(value: str) -> str:
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"
