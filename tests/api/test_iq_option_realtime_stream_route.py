from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROUTE_SOURCE = ROOT / "app/api/routes/market_providers.py"


def test_iq_option_realtime_sse_route_is_registered_without_removing_http_fallback() -> None:
    source = ROUTE_SOURCE.read_text(encoding="utf-8")

    assert '@router.get("/iq-option/realtime-candles/stream")' in source
    assert '@router.get("/iq-option/realtime-candles")' in source
    assert "StreamingResponse" in source
    assert 'media_type="text/event-stream"' in source
    assert "iq_option_provider_runtime.next_realtime_stream_event" in source


def test_iq_option_realtime_sse_route_uses_sanitized_events_and_cleanup() -> None:
    source = ROUTE_SOURCE.read_text(encoding="utf-8")

    assert "_sse(event.event_type, event.sanitized())" in source
    assert "_sse(\"heartbeat\", heartbeat.sanitized())" in source
    assert "_sse(\"error\", {\"error_code\":" in source
    assert "await request.is_disconnected()" in source
    assert "is_realtime_stream_current(subscription)" in source
    assert "iq_option_provider_runtime.end_realtime_stream(subscription)" in source
    assert "Cache-Control" in source
    assert "X-Accel-Buffering" in source
