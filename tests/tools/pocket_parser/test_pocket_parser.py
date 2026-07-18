from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.pocket_parser.asset_parser import parse_change_symbol, parse_update_assets
from tools.pocket_parser.candle_normalizer import normalize_candle
from tools.pocket_parser.engineio_parser import parse_engineio_frame
from tools.pocket_parser.history_parser import parse_history_batch
from tools.pocket_parser.offline_store import PocketOfflineStore
from tools.pocket_parser.replay_engine import PocketOfflineReplayEngine
from tools.pocket_parser.report_generator import generate_reports
from tools.pocket_parser.socketio_parser import parse_socketio_frame
from tools.pocket_parser.stream_parser import parse_update_stream
from tools.pocket_parser.validator import assert_report_is_sanitized

PRIVATE_HARS = (
    Path(".jarvis_private/pocket_hars/pocketoption.com.har"),
    Path(".jarvis_private/pocket_hars/pocketoption.com(1).har"),
)


def test_engineio_parser_classifies_core_frames() -> None:
    assert parse_engineio_frame("0{}").kind == "ENGINE_OPEN"
    assert parse_engineio_frame("2").kind == "PING"
    assert parse_engineio_frame("3").kind == "PONG"
    assert parse_engineio_frame("40").kind == "SOCKET_CONNECT"
    assert parse_engineio_frame("41").kind == "SOCKET_DISCONNECT"
    assert parse_engineio_frame('42["changeSymbol",{"asset":"EURUSD_otc","period":60}]').kind == "SOCKET_EVENT"
    assert parse_engineio_frame('42["broken"').kind == "PARSE_ERROR"


def test_socketio_parser_handles_payload_shapes() -> None:
    assert parse_socketio_frame('42["x",{"a":1}]').payload_type == "dict"
    assert parse_socketio_frame('42["x",[{"a":1}]]').payload_type == "list"
    assert parse_socketio_frame('42["x",null]').payload_type is None
    assert parse_socketio_frame('42["x"]').event_name == "x"
    assert parse_socketio_frame('42["x"').parse_error is not None


@pytest.mark.parametrize(
    ("asset", "period", "timeframe", "display"),
    [
        ("EURUSD_otc", 60, "M1", "EURUSD OTC"),
        ("EURUSD_otc", 300, "M5", "EURUSD OTC"),
        ("AUDUSD_otc", 900, "M15", "AUDUSD OTC"),
        ("USDBRL_otc", 300, "M5", "USDBRL OTC"),
    ],
)
def test_change_symbol_parser(asset: str, period: int, timeframe: str, display: str) -> None:
    parsed = parse_change_symbol({"asset": asset, "period": period})

    assert parsed.asset == asset
    assert parsed.period == period
    assert parsed.timeframe == timeframe
    assert parsed.display_name == display
    assert parsed.is_otc is True


@pytest.mark.parametrize("payload", [{"period": 60}, {"asset": "EURUSD_otc"}, {"asset": "EURUSD_otc", "period": 1}, []])
def test_change_symbol_rejects_invalid_payload(payload: object) -> None:
    with pytest.raises(ValueError):
        parse_change_symbol(payload)


def test_history_parser_normalizes_sorts_and_deduplicates() -> None:
    payload = {
        "asset": "EURUSD_otc",
        "period": 300,
        "history": [[1700000000.1, 1.1]],
        "candles": [
            [1700000300, 1.1, 1.2, 1.3, 1.0, 10],
            [1700000000, 1.0, 1.1, 1.2, 0.9, 10],
            [1700000000, 1.0, 1.1, 1.2, 0.9, 10],
        ],
    }

    batch, rejections = parse_history_batch(payload, source_har="fixture.har", session_index=1, frame_index=1)

    assert batch is not None
    assert rejections == []
    assert len(batch.candles) == 2
    assert batch.candles[0].timestamp == 1700000000
    assert batch.candles[0].high == 1.2
    assert batch.candles[0].low == 0.9


def test_history_parser_rejects_invalid_ohlc_timestamp_and_schema() -> None:
    payload = {
        "asset": "EURUSD_otc",
        "period": 300,
        "candles": [
            [1700000000, 1.0, 1.1, 0.8, 0.9, 10],
            ["bad", 1.0, 1.1, 1.2, 0.9, 10],
            [1700000300],
        ],
    }

    batch, rejections = parse_history_batch(payload, source_har="fixture.har", session_index=1, frame_index=1)

    assert batch is not None
    assert batch.candles == ()
    assert {item.code for item in rejections} >= {"INVALID_OHLC", "INVALID_TIMESTAMP", "UNKNOWN_CANDLE_SCHEMA"}


def test_candle_normalizer_rejects_unsupported_period() -> None:
    candle, error = normalize_candle([1700000000, 1.0, 1.1, 1.2, 0.9], asset="EURUSD_otc", period=1, source_event="test", source_har="fixture", session_index=1)

    assert candle is None
    assert error == "UNSUPPORTED_PERIOD"


def test_stream_parser_accepts_multiple_assets_and_rejects_bad_rows() -> None:
    ticks, rejections = parse_update_stream(
        [["EURUSD_otc", 1700000000.1, 1.1], ["AUDUSD_otc", 1700000000.2, 0.66], ["AUDUSD_otc", 1700000000.2, 0.66], ["BAD", "x", 1]],
        source_har="fixture.har",
        session_index=1,
        frame_index=3,
        sequence_start=10,
    )

    assert [tick.asset for tick in ticks] == ["EURUSD_otc", "AUDUSD_otc"]
    assert ticks[0].sequence == 10
    assert {item.code for item in rejections} == {"DUPLICATE_TICK", "INVALID_TIMESTAMP"}


def test_update_assets_preserves_unknown_fields_without_promoting_payout() -> None:
    assets = parse_update_assets([[1, "#EURUSD_otc", "EUR/USD OTC", "currency", 3, 92, 60, 30, True, {"x": 1}, [], 0, [], 123, False, [{"time": 60}, {"time": 300}], 0]])

    assert len(assets) == 1
    assert assets[0].symbol == "EURUSD_otc"
    assert assets[0].is_otc is True
    assert assets[0].supported_periods == (60, 300)
    assert assets[0].payout is None
    assert assets[0].is_available is None
    assert assets[0].unknown_numeric_fields


def test_offline_store_buckets_replace_sort_and_last_n() -> None:
    store = PocketOfflineStore()
    c1, _ = normalize_candle([1700000300, 1.1, 1.2, 1.3, 1.0], asset="EURUSD_otc", period=60, source_event="x", source_har="a", session_index=1)
    c2, _ = normalize_candle([1700000000, 1.0, 1.1, 1.2, 0.9], asset="EURUSD_otc", period=60, source_event="x", source_har="a", session_index=1)
    c2b, _ = normalize_candle([1700000000, 1.01, 1.11, 1.21, 0.91], asset="EURUSD_otc", period=60, source_event="x", source_har="a", session_index=1)

    store.add_candles([c1, c2, c2b])  # type: ignore[list-item]

    key = "POCKET:EURUSD_otc:60"
    assert store.list_buckets() == (key,)
    assert store.count(key) == 2
    assert store.first(key).open == 1.01  # type: ignore[union-attr]
    assert len(store.last_n(key, 1)) == 1


def test_replay_engine_processes_synthetic_har_and_reports(tmp_path: Path) -> None:
    har = tmp_path / "pocket.har"
    har.write_text(json.dumps(_sample_har()), encoding="utf-8")
    engine = PocketOfflineReplayEngine()

    result = engine.replay((str(har),))

    assert result.sessions_processed == 1
    assert result.change_symbols
    assert result.history_batches
    assert result.ticks
    assert engine.store.count("POCKET:EURUSD_otc:300") == 2


def test_reports_are_sanitized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    har = tmp_path / "pocket.har"
    har.write_text(json.dumps(_sample_har(include_sensitive=True)), encoding="utf-8")
    engine = PocketOfflineReplayEngine()
    result = engine.replay((str(har),))

    from tools.pocket_parser import report_generator

    monkeypatch.setattr(report_generator, "DEFAULT_DIR", tmp_path)
    monkeypatch.setattr(report_generator, "REPORT_JSON", tmp_path / "parser.json")
    monkeypatch.setattr(report_generator, "REPORT_TXT", tmp_path / "parser.txt")
    monkeypatch.setattr(report_generator, "CANDLE_SCHEMA_JSON", tmp_path / "candle.json")
    monkeypatch.setattr(report_generator, "CANDLE_SCHEMA_TXT", tmp_path / "candle.txt")
    monkeypatch.setattr(report_generator, "TICK_SCHEMA_JSON", tmp_path / "tick.json")
    monkeypatch.setattr(report_generator, "TICK_SCHEMA_TXT", tmp_path / "tick.txt")
    monkeypatch.setattr(report_generator, "ASSET_SCHEMA_JSON", tmp_path / "asset.json")
    monkeypatch.setattr(report_generator, "ASSET_SCHEMA_TXT", tmp_path / "asset.txt")
    monkeypatch.setattr(report_generator, "STORE_JSON", tmp_path / "store.json")
    monkeypatch.setattr(report_generator, "STORE_TXT", tmp_path / "store.txt")

    paths = report_generator.generate_reports(result, engine.store)

    assert_report_is_sanitized(tuple(paths.values()))
    for path in paths.values():
        assert "secret-value" not in path.read_text(encoding="utf-8")


@pytest.mark.skipif(not all(path.exists() for path in PRIVATE_HARS), reason="Private Pocket HARs are not available locally.")
def test_private_hars_create_required_buckets_without_copying_payloads() -> None:
    engine = PocketOfflineReplayEngine()

    result = engine.replay(tuple(str(path) for path in PRIVATE_HARS))

    assert result.sessions_processed == 2
    assert result.change_symbols
    assert result.history_batches
    assert result.ticks
    assert result.assets
    for key in (
        "POCKET:EURUSD_otc:60",
        "POCKET:EURUSD_otc:300",
        "POCKET:AUDUSD_otc:60",
        "POCKET:AUDUSD_otc:900",
        "POCKET:USDBRL_otc:60",
        "POCKET:USDBRL_otc:300",
        "POCKET:USDBRL_otc:900",
    ):
        assert engine.store.count(key) > 0


def _sample_har(*, include_sensitive: bool = False) -> dict:
    secret = {"token": "secret-value"} if include_sensitive else {}
    return {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2026-07-16T12:00:00.000Z",
                    "request": {"url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"},
                    "_webSocketMessages": [
                        {"type": "send", "time": 1, "data": f'42["changeSymbol",{{"asset":"EURUSD_otc","period":300{"," if secret else ""}{json.dumps(secret)[1:-1] if secret else ""}}}]'},
                        {"type": "receive", "time": 2, "data": '42["updateHistoryNewFast",{"asset":"EURUSD_otc","period":300,"history":[[1700000000.1,1.1]],"candles":[[1700000000,1.0,1.1,1.2,0.9,10],[1700000300,1.1,1.2,1.3,1.0,11]]}]'},
                        {"type": "receive", "time": 3, "data": '42["updateStream",[["EURUSD_otc",1700000301.1,1.2]]]'},
                        {"type": "receive", "time": 4, "data": '42["updateAssets",[[1,"#EURUSD_otc","EUR/USD OTC","currency",3,92,60,30,3,1,0,0,[],1700000000,true,[{"time":60},{"time":300}],0,3,-1]]]'},
                        {"type": "receive", "time": 5, "data": '42["updateCharts",[{"chart_id":"chart-1","settings":"{\\"symbol\\":\\"EURUSD_otc\\",\\"chartPeriod\\":6}"}]]'},
                        {"type": "receive", "time": 6, "data": '42["unknownMarketEvent",{"asset":"EURUSD_otc"}]'},
                    ],
                }
            ]
        }
    }

