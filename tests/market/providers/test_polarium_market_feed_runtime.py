from __future__ import annotations

import pytest

from app.market.providers.polarium.bootstrap import BootstrapRequestFactory, HistoricalBootstrapManager
from app.market.providers.polarium.market_router import PolariumMarketRouter
from app.market.providers.polarium.market_socket import PolariumMarketSocketDiscovery
from app.market.providers.polarium.market_store_adapter import PolariumCandleStoreAdapter
from app.market.providers.polarium.parser import PolariumMarketFeedParser
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.providers.polarium.runtime_guard import PolariumRuntimeGuard, PolariumRuntimeGuardViolation
from app.market.store import CandleStore


def candles_generated_payload(active_id: int = 1857, *, start: int = 1_783_720_000) -> dict:
    return {
        "name": "candles-generated",
        "msg": {
            "result": {
                "active_id": active_id,
                "at": start,
                "bid": 1.1234,
                "ask": 1.1236,
                "value": 1.1235,
                "candles": {
                    "60": plural_candle(start, 60),
                    "300": plural_candle(start - 240, 300),
                    "900": plural_candle(start - 840, 900),
                },
            }
        },
    }


def candle_generated_payload(active_id: int = 1857, raw_size: int = 60, *, start: int = 1_783_720_000) -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                **candle(start, raw_size, close=1.1240),
            }
        },
    }


def page_native_get_first_candles(active_id: int, raw_size: int = 60) -> dict:
    return {
        "name": "sendMessage",
        "msg": {
            "name": "get-first-candles",
            "body": {
                "active_id": active_id,
                "size": raw_size,
            },
        },
    }


def page_native_subscribe_candle(active_id: int, raw_size: int = 60) -> dict:
    return {
        "name": "subscribeMessage",
        "msg": {
            "name": "candle-generated",
            "params": {"routingFilters": {"active_id": active_id, "size": raw_size}},
        },
    }


def first_candles_history_payload(active_id: int, raw_size: int, *, count: int, symbol: str = "USD/BRL OTC", start: int = 1_783_720_000) -> dict:
    if raw_size in {300, 900} and start % raw_size != 0:
        start += raw_size - (start % raw_size)
    return {
        "name": "first-candles",
        "msg": {
            "body": {
                "active_id": active_id,
                "symbol": symbol,
                "size": raw_size,
                "candles": [
                    {
                        **candle(start + index * raw_size, raw_size, close=1.1000 + index / 1000),
                        "size": raw_size,
                    }
                    for index in range(count)
                ],
            }
        },
    }


def candle(start: int, raw_size: int, *, close: float) -> dict:
    return {
        "from": start,
        "to": start + raw_size,
        "open": 1.1230,
        "close": close,
        "min": 1.1220,
        "max": 1.1265,
        "volume": 0,
    }


def plural_candle(start: int, raw_size: int, *, open_price: float = 1.1230, low: float = 1.1220, high: float = 1.1265) -> dict:
    return {
        "from": start,
        "to": start + raw_size,
        "open": open_price,
        "min": low,
        "max": high,
        "volume": 0,
    }


def test_runtime_guard_allows_only_read_only_market_outbound() -> None:
    guard = PolariumRuntimeGuard()

    guard.validate_outbound(
        {
            "name": "subscribeMessage",
            "msg": {"name": "candles-generated", "params": {"routingFilters": {"active_id": 1857}}},
        }
    )
    guard.validate_outbound(
        {
            "name": "unsubscribeMessage",
            "msg": {"name": "candle-generated", "params": {"routingFilters": {"active_id": 1857, "size": 60}}},
        }
    )

    with pytest.raises(PolariumRuntimeGuardViolation):
        guard.validate_outbound({"name": "subscribeMessage", "msg": {"name": "portfolio.position-changed"}})
    with pytest.raises(PolariumRuntimeGuardViolation):
        guard.validate_outbound(
            {
                "name": "subscribeMessage",
                "msg": {"name": "candles-generated", "params": {"routingFilters": {"active_id": 1857, "size": 60}}},
            }
        )


def test_bootstrap_payload_uses_read_only_get_first_candles_and_starts_bootstrapping() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    payload = runtime.bootstrap_payload(2298, 60)

    assert payload["name"] == "sendMessage"
    assert payload["msg"]["name"] == "get-first-candles"
    assert payload["msg"]["body"] == {"active_id": 2298, "size": 60}


def test_runtime_guard_drops_non_market_inbound_without_payload_storage() -> None:
    guard = PolariumRuntimeGuard()

    assert guard.classify_inbound({"name": "candles-generated", "msg": {"result": {}}}) == "allow"
    assert guard.classify_inbound({"name": "currency-updated", "msg": {"body": {"ignored": True}}}) == "drop"
    assert guard.classify_inbound({"name": "portfolio.position-changed", "msg": {"body": {}}}) == "forbidden"


def test_parser_separates_plural_multitimeframe_from_singular() -> None:
    parser = PolariumMarketFeedParser()

    plural = parser.parse(candles_generated_payload())
    singular = parser.parse(candle_generated_payload(raw_size=60))

    assert plural.event_name == "candles-generated"
    assert plural.active_id == 1857
    assert [item.raw_size for item in plural.candles] == [60, 300, 900]
    assert plural.bid == 1.1234
    assert plural.ask == 1.1236
    assert plural.value == 1.1235
    assert plural.candles[0].close == 1.1235
    assert plural.candles[0].start_timestamp == 1_783_720_000
    assert singular.event_name == "candle-generated"
    assert [item.raw_size for item in singular.candles] == [60]


def test_plural_ohlc_mapping_uses_min_max_value_and_from_without_close_field() -> None:
    parser = PolariumMarketFeedParser()
    payload = {
        "name": "candles-generated",
        "msg": {
            "active_id": 85,
            "at": 1_783_907_961_000_000_000,
            "ask": 161.5014,
            "bid": 161.5013,
            "value": 161.50135,
            "candles": {
                "60": {
                    "from": 1_783_907_940,
                    "to": 1_783_908_000,
                    "open": 161.51515,
                    "min": 161.50135,
                    "max": 161.51515,
                    "volume": 0,
                }
            },
        },
    }

    event = parser.parse(payload)
    candle = event.candles[0]

    assert event.active_id == 85
    assert candle.raw_size == 60
    assert candle.start_timestamp == 1_783_907_940
    assert candle.end_timestamp == 1_783_908_000
    assert candle.open == 161.51515
    assert candle.low == 161.50135
    assert candle.high == 161.51515
    assert candle.close == 161.50135


def test_plural_value_expands_low_high_without_clamping_or_inventing_price() -> None:
    parser = PolariumMarketFeedParser()
    payload = candles_generated_payload(start=1_783_720_000)
    payload["msg"]["result"]["value"] = 1.1300
    payload["msg"]["result"]["candles"]["60"] = plural_candle(1_783_720_000, 60, open_price=1.1230, low=1.1220, high=1.1265)

    candle = parser.parse(payload).candles[0]

    assert candle.close == 1.1300
    assert candle.low == 1.1220
    assert candle.high == 1.1300


def test_plural_missing_value_drops_instead_of_defaulting_close() -> None:
    parser = PolariumMarketFeedParser()
    payload = candles_generated_payload()
    del payload["msg"]["result"]["value"]

    with pytest.raises(Exception) as exc:
        parser.parse(payload)

    assert "MISSING_NUMERIC_FIELD:value" in str(exc.value)


def test_router_updates_shared_candle_store_by_active_id_and_timeframe() -> None:
    store = CandleStore()
    parser = PolariumMarketFeedParser()
    router = PolariumMarketRouter(PolariumCandleStoreAdapter(store))

    results = router.route(parser.parse(candles_generated_payload(active_id=76)))

    assert [result.status for result in results] == ["added", "added", "added"]
    assert len(store.series(active_id=76, raw_size=60)) == 1
    assert len(store.series(active_id=76, raw_size=300)) == 1
    assert len(store.series(active_id=76, raw_size=900)) == 1


def test_store_updates_same_polarium_timestamp_and_appends_new_window() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    first = runtime.process_message(candles_generated_payload(76, start=1_783_720_000), now_ms=1_000)
    updated_payload = candles_generated_payload(76, start=1_783_720_000)
    updated_payload["msg"]["result"]["value"] = 1.1245
    updated = runtime.process_message(updated_payload, now_ms=2_000)
    appended = runtime.process_message(candles_generated_payload(76, start=1_783_720_060), now_ms=3_000)

    series = store.series(active_id=76, raw_size=60)
    assert first.stored == 3
    assert updated.updated == 3
    assert appended.stored == 3
    assert len(series) == 2
    assert series[0].start_timestamp == 1_783_720_000
    assert series[0].close == 1.1245
    assert series[1].start_timestamp == 1_783_720_060


def test_runtime_tracks_latest_live_active_id_and_timeframes_for_visual_selection() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(candles_generated_payload(1857), now_ms=1_000)

    status = runtime.status().sanitized()
    assert status["latest_active_id"] == 1857
    assert status["latest_raw_sizes"] == [60, 300, 900]


def test_runtime_resolves_symbol_from_session_metadata_without_fallback() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    runtime.process_message(
        {
            "name": "instrument-metadata",
            "msg": {
                "body": {
                    "items": [
                        {"active_id": 76, "symbol": "EUR/USD OTC", "display_name": "EUR/USD OTC"},
                        {"active_id": 2298, "symbol": "USD/BRL OTC", "display_name": "USD/BRL OTC"},
                    ]
                }
            },
        },
        now_ms=1_000,
    )
    result = runtime.process_message(candles_generated_payload(2298), now_ms=2_000)

    series = store.series(active_id=2298, raw_size=60)
    status = runtime.status().sanitized()
    assert result.status == "processed"
    assert series[0].symbol == "USD/BRL OTC"
    assert status["latest_active_id"] == 2298
    assert status["latest_symbol"] == "USD/BRL OTC"
    assert status["session_context"]["latest_market_event_active_id"] == 2298
    assert status["session_context"]["active_id"] is None
    assert status["session_context"]["analysis_blocked"] is True


def test_page_native_selection_defines_visible_context_before_server_candles() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(
        {"name": "asset-metadata", "msg": {"body": {"active_id": 2298, "symbol": "USD/BRL OTC"}}},
        origin="PAGE_NATIVE",
        now_ms=1_000,
    )
    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["active_id"] == 2298
    assert context["visible_active_id"] == 2298
    assert context["symbol"] == "USD/BRL OTC"
    assert context["display_name"] == "USD/BRL OTC"
    assert context["timeframe"] == "M1"
    assert context["feed_status"] == "BOOTSTRAPPING"
    assert context["history_state"] == "BOOTSTRAPPING"
    assert context["analysis_blocked"] is True


def test_runtime_does_not_reuse_previous_symbol_when_active_id_changes_unresolved() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    first = candles_generated_payload(76)
    first["msg"]["result"]["symbol"] = "EUR/USD OTC"
    runtime.process_message(first, now_ms=1_000)
    runtime.process_message(candles_generated_payload(2298, start=1_783_720_060), now_ms=2_000)

    assert store.series(active_id=76, raw_size=60)[0].symbol == "EUR/USD OTC"
    assert store.series(active_id=2298, raw_size=60)[0].symbol is None
    assert runtime.status().sanitized()["latest_symbol"] is None
    assert runtime.status().sanitized()["session_context"]["display_name"] == "Não disponível"
    assert runtime.status().sanitized()["session_context"]["analysis_blocked"] is True


def test_runtime_bootstraps_real_first_candles_history_for_active_context() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    result = runtime.process_message(
        {
            "name": "first-candles",
            "msg": {
                "body": {
                    "active_id": 2298,
                    "symbol": "USD/BRL OTC",
                    "candles": [
                        candle(1_783_720_000, 60, close=5.4100),
                        candle(1_783_720_060, 60, close=5.4200),
                    ],
                    "size": 60,
                }
            },
        },
        now_ms=1_000,
    )

    series = store.series(active_id=2298, raw_size=60)
    assert result.status == "processed"
    assert result.processed == 2
    assert [item.start_timestamp for item in series] == [1_783_720_000, 1_783_720_060]
    assert {item.symbol for item in series} == {"USD/BRL OTC"}


def test_session_context_updates_active_id_timeframe_price_and_provider_atomically() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    first = candle_generated_payload(active_id=76, raw_size=60, start=1_783_720_000)
    first["msg"]["body"]["symbol"] = "EUR/USD OTC"
    second = candle_generated_payload(active_id=2298, raw_size=300, start=1_783_720_300)
    second["msg"]["body"]["symbol"] = "USD/BRL OTC"
    second["msg"]["body"]["close"] = 5.4321

    runtime.process_message(page_native_get_first_candles(76, 60), origin="PAGE_NATIVE", now_ms=500)
    runtime.process_message(first, now_ms=1_000)
    runtime.process_message(page_native_get_first_candles(2298, 300), origin="PAGE_NATIVE", now_ms=1_500)
    runtime.process_message(first_candles_history_payload(2298, 300, count=50), now_ms=1_800)
    runtime.process_message(second, now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["provider"] == "POLARIUM"
    assert context["active_id"] == 2298
    assert context["symbol"] == "USD/BRL OTC"
    assert context["display_name"] == "USD/BRL OTC"
    assert context["market_type"] == "POLARIUM_AUTHORIZED_MARKET"
    assert context["raw_size"] == 300
    assert context["timeframe"] == "M5"
    assert context["latest_price"] == 5.4321
    assert context["analysis_blocked"] is False
    assert context["history_state"] == "READY"


def test_realtime_without_history_does_not_mark_analysis_ready() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    realtime = candle_generated_payload(active_id=2298, raw_size=60)
    realtime["msg"]["body"]["symbol"] = "USD/BRL OTC"

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(realtime, origin="SERVER_INBOUND", now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["history_state"] == "BOOTSTRAPPING"
    assert context["history_count"] == 0
    assert context["analysis_blocked"] is True


def test_history_readiness_progresses_limited_then_ready_without_realtime_duplication() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(first_candles_history_payload(2298, 60, count=20), now_ms=2_000)
    limited = runtime.status().sanitized()["session_context"]
    runtime.process_message(first_candles_history_payload(2298, 60, count=50), now_ms=3_000)
    ready = runtime.status().sanitized()["session_context"]
    runtime.process_message(candle_generated_payload(2298, 60, start=1_783_720_000 + 49 * 60), now_ms=4_000)
    after_realtime_update = runtime.status().sanitized()["session_context"]

    assert limited["history_state"] == "LIMITED"
    assert limited["history_progress"] == 20
    assert ready["history_state"] == "READY"
    assert ready["history_progress"] == 50
    assert after_realtime_update["history_count"] == 50


def test_server_inbound_background_event_does_not_change_visible_context() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    selected = candle_generated_payload(2298, raw_size=60, start=1_783_720_000)
    selected["msg"]["body"]["symbol"] = "USD/BRL OTC"
    background = candle_generated_payload(76, raw_size=60, start=1_783_720_060)
    background["msg"]["body"]["symbol"] = "EUR/USD OTC"

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=500)
    runtime.process_message(selected, origin="SERVER_INBOUND", now_ms=1_000)
    runtime.process_message(background, origin="SERVER_INBOUND", now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["active_id"] == 2298
    assert context["symbol"] == "USD/BRL OTC"
    assert context["latest_market_event_active_id"] == 76
    assert {"active_id": 76, "raw_sizes": [60]} in context["background_market_contexts"]


def test_friday_probe_does_not_change_visible_context() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(page_native_get_first_candles(76, 300), origin="FRIDAY_PROBE", now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["active_id"] == 2298
    assert context["raw_size"] == 60


def test_page_native_timeframe_change_updates_visible_raw_size_without_plural_background_override() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(candles_generated_payload(2298), origin="SERVER_INBOUND", now_ms=2_000)
    runtime.process_message(page_native_subscribe_candle(2298, 300), origin="PAGE_NATIVE", now_ms=3_000)
    runtime.process_message(candles_generated_payload(2298, start=1_783_720_300), origin="SERVER_INBOUND", now_ms=4_000)

    context = runtime.status().sanitized()["session_context"]
    assert context["active_id"] == 2298
    assert context["raw_size"] == 300
    assert context["timeframe"] == "M5"
    assert context["available_raw_sizes"] == [60, 300, 900]


def test_socket_discovery_identifies_market_socket_and_reconnect() -> None:
    discovery = PolariumMarketSocketDiscovery()

    discovery.register_socket(request_id="1", url="wss://ws.trade.polariumbroker.com/echo/websocket")
    discovery.observe_frame(request_id="1", message={"name": "authenticated"})
    discovery.observe_frame(request_id="1", message={"name": "timeSync"})
    discovery.observe_frame(request_id="1", message={"name": "candles-generated"})

    assert discovery.market_socket is not None
    assert discovery.market_socket.ready is True
    assert discovery.active_market_socket_count == 1

    discovery.close_socket("1")
    discovery.register_socket(request_id="1", url="wss://ws.trade.polariumbroker.com/echo/websocket")
    assert discovery.reconnects == 1


def test_runtime_processes_two_assets_three_timeframes_and_feed_quality() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    sub_a = runtime.subscribe_payload(1857)
    sub_b = runtime.subscribe_payload(76)
    result_a = runtime.process_message(candles_generated_payload(1857, start=1_783_720_000), now_ms=1_000)
    result_b = runtime.process_message(candles_generated_payload(76, start=1_783_720_060), now_ms=2_000)
    result_a_update = runtime.process_message(candles_generated_payload(1857, start=1_783_720_060), now_ms=3_000)

    assert sub_a["msg"]["name"] == "candles-generated"
    assert "size" not in sub_a["msg"]["params"]["routingFilters"]
    assert sub_b["msg"]["params"]["routingFilters"]["active_id"] == 76
    assert result_a.status == "processed"
    assert result_b.status == "processed"
    assert result_a_update.processed == 3
    assert len(store.series(active_id=1857, raw_size=60)) == 2
    assert len(store.series(active_id=76, raw_size=60)) == 1
    assert len(store.series(active_id=1857, raw_size=300)) == 2
    assert len(store.series(active_id=76, raw_size=900)) == 1

    quality = runtime.feed.feed_quality.snapshot(
        market_type="POLARIUM_AUTHORIZED_MARKET",
        symbol="1857",
        raw_size=60,
        now_ms=20_000,
    )
    assert quality.events_received == 2
    assert quality.ohlc_changes >= 1


def test_runtime_does_not_process_forbidden_or_unrelated_messages() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    forbidden = runtime.process_message({"name": "portfolio.position-changed", "msg": {"body": {}}})
    dropped = runtime.process_message({"name": "currency-updated", "msg": {"body": {}}})

    assert forbidden.status == "dropped"
    assert forbidden.dropped_reason == "FORBIDDEN_INBOUND"
    assert dropped.status == "dropped"
    assert runtime.status().forbidden == 1
    assert runtime.status().dropped == 1


def test_bootstrap_tracks_pending_request_and_sanitized_status() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    request = page_native_get_first_candles(2298, 60)
    request["request_id"] = "req-history-1"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)

    bootstrap = runtime.status().sanitized()["bootstrap"]
    assert bootstrap["state"] == "BOOTSTRAPPING"
    assert bootstrap["request_sent"] is True
    assert bootstrap["request_id_present"] is True
    assert bootstrap["pending_bootstrap_requests"] == 1
    assert bootstrap["bootstrap_attempts"] == 1


def test_first_candles_correlates_request_id_and_candles_by_size_without_active_id() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    request = page_native_get_first_candles(2298, 60)
    request["request_id"] = "req-history-2"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    result = runtime.process_message(
        {
            "name": "first-candles",
            "request_id": "req-history-2",
            "msg": {
                "candles_by_size": {
                    "60": candle(1_783_720_000, 60, close=5.4100),
                    "300": candle(1_783_719_900, 300, close=5.4000),
                }
            },
        },
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    assert result.status == "processed"
    assert result.processed == 1
    assert len(store.series(active_id=2298, raw_size=60)) == 1
    assert len(store.series(active_id=2298, raw_size=300)) == 0
    context = runtime.status().sanitized()["session_context"]
    bootstrap = runtime.status().sanitized()["bootstrap"]
    assert context["history_count"] == 1
    assert bootstrap["matched_bootstrap_responses"] == 1
    assert bootstrap["response_type"] == "first-candles"
    assert bootstrap["received_count"] == 1
    assert bootstrap["valid_count"] == 1


def test_candles_response_correlates_request_id_and_array_history_is_sorted_deduped() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    request = page_native_get_first_candles(2298, 60)
    request["request_id"] = "req-history-3"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(
        {
            "name": "candles",
            "request_id": "req-history-3",
            "msg": {
                "data": {
                    "symbol": "USD/BRL OTC",
                    "candles": [
                        {**candle(1_783_720_120, 60, close=5.4300), "size": 60},
                        {**candle(1_783_720_000, 60, close=5.4100), "size": 60},
                        {**candle(1_783_720_000, 60, close=5.4200), "size": 60},
                    ],
                }
            },
        },
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    series = store.series(active_id=2298, raw_size=60)
    assert [item.start_timestamp for item in series] == [1_783_720_000, 1_783_720_120]
    assert series[0].close == 5.4200
    assert runtime.status().sanitized()["session_context"]["history_count"] == 2


def test_history_response_without_request_id_uses_single_pending_context_safely() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    runtime.process_message(page_native_get_first_candles(2298, 300), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(
        {
            "name": "first-candles",
            "msg": {"candles_by_size": {"300": candle(1_783_720_200, 300, close=5.4100)}},
        },
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    assert len(store.series(active_id=2298, raw_size=300)) == 1
    assert runtime.status().sanitized()["session_context"]["history_count"] == 1


def test_invalid_history_response_does_not_create_candles_and_reports_sanitized_error() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)

    runtime.process_message(page_native_get_first_candles(2298, 60), origin="PAGE_NATIVE", now_ms=1_000)
    result = runtime.process_message(
        {"name": "first-candles", "msg": {"candles_by_size": {"60": {"from": 1_783_720_000, "open": 5.4}}}},
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    bootstrap = runtime.status().sanitized()["bootstrap"]
    assert result.status == "invalid"
    assert len(store.series(active_id=2298, raw_size=60)) == 0
    assert bootstrap["response_received"] is True
    assert bootstrap["last_error"].startswith("MISSING_NUMERIC_FIELD")


def test_bootstrap_does_not_count_realtime_as_history_and_repeated_pending_is_visible() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    request = page_native_get_first_candles(2298, 60)
    request["request_id"] = "req-history-4"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_500)
    runtime.process_message(candle_generated_payload(2298, 60, start=1_783_720_000), origin="SERVER_INBOUND", now_ms=2_000)

    status = runtime.status().sanitized()
    assert status["bootstrap"]["bootstrap_attempts"] == 2
    assert status["session_context"]["history_count"] == 0
    assert status["session_context"]["history_state"] == "BOOTSTRAPPING"


def test_history_count_reaches_ready_threshold_for_visible_context() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    request = page_native_get_first_candles(2298, 60)
    request["request_id"] = "req-history-5"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    response = first_candles_history_payload(2298, 60, count=50)
    response["request_id"] = "req-history-5"
    runtime.process_message(response, origin="SERVER_INBOUND", now_ms=2_000)

    context = runtime.status().sanitized()["session_context"]
    bootstrap = runtime.status().sanitized()["bootstrap"]
    assert context["history_count"] == 50
    assert context["history_state"] == "READY"
    assert bootstrap["state"] == "READY"


def test_bootstrap_request_factory_uses_only_read_only_get_first_candles_envelope() -> None:
    request = BootstrapRequestFactory().create(active_id=2298, raw_size=60, now_ms=1_000, attempt=1)

    assert request.payload["name"] == "sendMessage"
    assert request.payload["request_id"] == "friday_get_first_candles_2298_60_1000_1"
    assert request.payload["msg"] == {"name": "get-first-candles", "body": {"active_id": 2298, "size": 60}}


def test_historical_bootstrap_manager_auto_request_timeout_retry_and_failure() -> None:
    manager = HistoricalBootstrapManager(timeout_ms=10_000, max_retries=1)

    first = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=1_000, socket_ready=True)
    duplicate = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=2_000, socket_ready=True)
    retry = manager.tick(now_ms=11_001, socket_ready=True)
    failed = manager.tick(now_ms=22_000, socket_ready=True)

    assert first.kind == "send"
    assert duplicate.kind == "none"
    assert retry.kind == "retry"
    assert retry.request is not None
    assert retry.request.attempt == 2
    assert failed.kind == "failed"
    assert manager.sanitized()["last_error"] == "BOOTSTRAP_FAILED"


def test_historical_bootstrap_manager_cancels_pending_on_asset_or_timeframe_change() -> None:
    manager = HistoricalBootstrapManager()

    first = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=1_000, socket_ready=True)
    changed_asset = manager.on_visible_context(active_id=76, raw_size=60, now_ms=2_000, socket_ready=True)
    changed_timeframe = manager.on_visible_context(active_id=76, raw_size=300, now_ms=3_000, socket_ready=True)

    assert first.request is not None
    assert changed_asset.request is not None
    assert changed_asset.request.active_id == 76
    assert changed_asset.request.raw_size == 60
    assert changed_timeframe.request is not None
    assert changed_timeframe.request.active_id == 76
    assert changed_timeframe.request.raw_size == 300


def test_historical_bootstrap_manager_correlates_response_by_request_id_and_context() -> None:
    manager = HistoricalBootstrapManager()

    request = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=1_000, socket_ready=True).request
    assert request is not None
    manager.on_response(request_id=request.request_id, active_id=None, raw_size=None)
    completed = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=2_000, socket_ready=True)

    assert completed.kind == "none"
    assert manager.sanitized()["state"] == "READY"

    second = manager.on_visible_context(active_id=76, raw_size=300, now_ms=3_000, socket_ready=True).request
    assert second is not None
    manager.on_response(request_id=None, active_id=76, raw_size=300)
    assert manager.sanitized()["state"] == "READY"


def test_m1_ready_does_not_block_m5_or_m15_bootstrap_requests() -> None:
    manager = HistoricalBootstrapManager()

    m1 = manager.on_visible_context(active_id=2298, raw_size=60, now_ms=1_000, socket_ready=True)
    assert m1.request is not None
    manager.on_response(request_id=m1.request.request_id, active_id=2298, raw_size=60)

    m5 = manager.on_visible_context(active_id=2298, raw_size=300, now_ms=2_000, socket_ready=True)
    assert m5.kind == "send"
    assert m5.request is not None
    assert m5.request.payload["msg"]["body"]["size"] == 300

    manager.on_response(request_id=m5.request.request_id, active_id=2298, raw_size=300)
    m15 = manager.on_visible_context(active_id=2298, raw_size=900, now_ms=3_000, socket_ready=True)
    assert m15.kind == "send"
    assert m15.request is not None
    assert m15.request.payload["msg"]["body"]["size"] == 900


def test_m5_history_response_string_and_numeric_size_keys_are_accepted() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    request = page_native_get_first_candles(2298, 300)
    request["request_id"] = "req-m5"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(
        {
            "name": "first-candles",
            "request_id": "req-m5",
            "msg": {
                "candles_by_size": {
                    "60": candle(1_783_720_020, 60, close=5.3900),
                    300: candle(1_783_720_200, 300, close=5.4100),
                }
            },
        },
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    assert len(store.series(active_id=2298, raw_size=60)) == 0
    assert len(store.series(active_id=2298, raw_size=300)) == 1
    assert runtime.status().sanitized()["session_context"]["history_count"] == 1


def test_m15_history_response_data_size_key_is_accepted_and_selected_only() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    request = page_native_get_first_candles(2298, 900)
    request["request_id"] = "req-m15"

    runtime.process_message(request, origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(
        {
            "name": "candles",
            "request_id": "req-m15",
            "msg": {
                "data": {
                    "300": candle(1_783_720_200, 300, close=5.4000),
                    "900": candle(1_783_720_800, 900, close=5.4100),
                }
            },
        },
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )

    assert len(store.series(active_id=2298, raw_size=300)) == 0
    assert len(store.series(active_id=2298, raw_size=900)) == 1
    assert runtime.status().sanitized()["session_context"]["history_count"] == 1


def test_m1_response_does_not_fill_m5_when_multiple_timeframe_requests_are_pending() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    m1_request = page_native_get_first_candles(2298, 60)
    m1_request["request_id"] = "req-m1-pending"
    m5_request = page_native_get_first_candles(2298, 300)
    m5_request["request_id"] = "req-m5-pending"

    runtime.process_message(m1_request, origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(m5_request, origin="PAGE_NATIVE", now_ms=2_000)
    runtime.process_message(
        {
            "name": "first-candles",
            "request_id": "req-m1-pending",
            "msg": {"body": {"active_id": 2298, "size": 60, "candles": [{**candle(1_783_720_000, 60, close=5.4000), "size": 60}]}},
        },
        origin="SERVER_INBOUND",
        now_ms=3_000,
    )

    context = runtime.status().sanitized()["session_context"]
    assert len(store.series(active_id=2298, raw_size=60)) == 1
    assert len(store.series(active_id=2298, raw_size=300)) == 0
    assert context["raw_size"] == 300
    assert context["history_count"] == 0


def test_m5_and_m15_readiness_are_independent_and_realtime_does_not_increment_history() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(page_native_get_first_candles(2298, 300), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(first_candles_history_payload(2298, 300, count=50), origin="SERVER_INBOUND", now_ms=2_000)
    m5_context = runtime.status().sanitized()["session_context"]
    runtime.process_message(candle_generated_payload(2298, 300, start=1_783_720_200), origin="SERVER_INBOUND", now_ms=3_000)
    m5_after_realtime = runtime.status().sanitized()["session_context"]

    runtime.process_message(page_native_get_first_candles(2298, 900), origin="PAGE_NATIVE", now_ms=4_000)
    m15_bootstrapping = runtime.status().sanitized()["session_context"]
    runtime.process_message(first_candles_history_payload(2298, 900, count=50), origin="SERVER_INBOUND", now_ms=5_000)
    m15_context = runtime.status().sanitized()["session_context"]

    assert m5_context["raw_size"] == 300
    assert m5_context["history_state"] == "READY"
    assert m5_context["history_count"] == 50
    assert m5_after_realtime["history_count"] == 50
    assert m15_bootstrapping["raw_size"] == 900
    assert m15_bootstrapping["history_count"] == 0
    assert m15_context["history_state"] == "READY"
    assert m15_context["history_count"] == 50


def test_m5_and_m15_history_reject_unaligned_timestamps() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())

    runtime.process_message(page_native_get_first_candles(2298, 300), origin="PAGE_NATIVE", now_ms=1_000)
    m5 = runtime.process_message(
        {"name": "first-candles", "msg": {"candles_by_size": {"300": candle(1_783_720_000, 300, close=5.4100)}}},
        origin="SERVER_INBOUND",
        now_ms=2_000,
    )
    runtime.process_message(page_native_get_first_candles(2298, 900), origin="PAGE_NATIVE", now_ms=3_000)
    m15 = runtime.process_message(
        {"name": "first-candles", "msg": {"candles_by_size": {"900": candle(1_783_720_200, 900, close=5.4200)}}},
        origin="SERVER_INBOUND",
        now_ms=4_000,
    )

    assert m5.status == "invalid"
    assert m5.dropped_reason == "DROP_INVALID_HISTORICAL_TIMESTAMP"
    assert m15.status == "invalid"
    assert m15.dropped_reason == "DROP_INVALID_HISTORICAL_TIMESTAMP"
