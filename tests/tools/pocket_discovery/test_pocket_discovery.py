from __future__ import annotations

import json
from pathlib import Path

from tools.pocket_discovery.har_loader import load_har
from tools.pocket_discovery.http_analyzer import analyze_http_endpoints
from tools.pocket_discovery.report_generator import generate_pocket_discovery_reports
from tools.pocket_discovery.sanitizer import REDACTED, REDACTED_KEY, sanitize, sanitize_url
from tools.pocket_discovery.socketio_parser import parse_socketio_frame
from tools.pocket_discovery.websocket_analyzer import analyze_websockets


def test_socketio_parser_confirms_change_symbol_shape() -> None:
    frame = parse_socketio_frame('42["changeSymbol",{"asset":"EURUSD_otc","period":300}]')

    assert frame.frame_kind == "SOCKET_IO_EVENT"
    assert frame.event_name == "changeSymbol"
    assert frame.payload == {"asset": "EURUSD_otc", "period": 300}
    assert frame.payload_keys == ("asset", "period")


def test_socketio_parser_handles_binary_event_prefix_observed_in_har() -> None:
    frame = parse_socketio_frame('451-["updateStream",{"asset":"EURUSD_otc","price":1.1}]')

    assert frame.frame_kind == "SOCKET_IO_BINARY_EVENT"
    assert frame.event_name == "updateStream"
    assert frame.payload_keys == ("asset", "price")


def test_socketio_parser_handles_base64_encoded_json_payload() -> None:
    frame = parse_socketio_frame("W1siRVVSVVNEX290YyIsMTcwMDAwMDAwMCwxLjFdXQ==")

    assert frame.frame_kind == "ENCODED_JSON"
    assert frame.payload_type == "list"
    assert frame.parse_error is None


def test_sanitizer_redacts_sensitive_keys_and_values() -> None:
    payload = {
        "Authorization": "Bearer abc.def.ghi",
        "email": "renan@example.com",
        "asset": "EURUSD_otc",
        "nested": {"ssid": "secret-session", "period": 300},
    }

    sanitized = sanitize(payload)

    assert sanitized[REDACTED_KEY] == REDACTED
    assert sanitized["nested"][REDACTED_KEY] == REDACTED
    assert sanitized["asset"] == "EURUSD_otc"
    assert sanitized["nested"]["period"] == 300


def test_sanitize_url_keeps_query_keys_but_redacts_sensitive_values() -> None:
    url = sanitize_url("wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket&token=secret")

    assert "EIO=4" in url
    assert "transport=websocket" in url
    assert "%5BREDACTED_KEY%5D=%5BREDACTED%5D" in url
    assert "secret" not in url


def test_websocket_analyzer_catalogs_market_socket_events(tmp_path: Path) -> None:
    har_path = _write_har(tmp_path / "pocket.har", _sample_har())
    result = load_har(har_path)

    sockets = analyze_websockets(result.path, result.har or {})

    assert len(sockets) == 1
    assert sockets[0].classification == "MARKET_SOCKET"
    assert sockets[0].transport == "websocket"
    assert sockets[0].socket_io_version == "4"
    assert set(sockets[0].event_names) >= {"changeSymbol", "updateStream", "updateHistoryNewFast", "updateAssets"}
    assert sockets[0].frames_sent == 1
    assert sockets[0].frames_received == 4


def test_report_generator_writes_sanitized_reports_and_catalog(tmp_path: Path) -> None:
    har_path = _write_har(tmp_path / "pocket.har", _sample_har())
    report_json = tmp_path / "pocket_discovery_report.json"
    report_txt = tmp_path / "pocket_discovery_report.txt"
    catalog_json = tmp_path / "pocket_event_catalog.json"
    catalog_txt = tmp_path / "pocket_event_catalog.txt"
    protocol_md = tmp_path / "pocket_protocol_map.md"

    report = generate_pocket_discovery_reports(
        (str(har_path),),
        report_json=report_json,
        report_txt=report_txt,
        catalog_json=catalog_json,
        catalog_txt=catalog_txt,
        protocol_md=protocol_md,
    )

    assert report.websocket_count == 1
    assert report.confirmed_preliminary_change_symbol is True
    assert report.viability_classification in {"GOOD", "EXCELLENT"}
    assert report.adapter_decision.startswith("PODE AVANCAR")
    assert "changeSymbol" in catalog_txt.read_text()
    assert "updateHistoryNewFast" in protocol_md.read_text()
    for path in (report_json, report_txt, catalog_json, catalog_txt, protocol_md):
        text = path.read_text()
        assert "sensitive-token" not in text
        assert "renan@example.com" not in text


def test_report_generator_records_missing_hars_without_inventing_viability(tmp_path: Path) -> None:
    report = generate_pocket_discovery_reports(
        (str(tmp_path / "missing.har"),),
        report_json=tmp_path / "report.json",
        report_txt=tmp_path / "report.txt",
        catalog_json=tmp_path / "catalog.json",
        catalog_txt=tmp_path / "catalog.txt",
        protocol_md=tmp_path / "protocol.md",
    )

    assert report.missing_hars == (str(tmp_path / "missing.har"),)
    assert report.websocket_count == 0
    assert report.viability_classification == "NOT_RECOMMENDED"
    assert report.adapter_decision == "NAO AVANCAR: HARs obrigatorios ausentes ou invalidos."


def test_comparison_lists_events_per_har(tmp_path: Path) -> None:
    first = _write_har(tmp_path / "first.har", _sample_har())
    second_payload = _sample_har(extra_event='42["saveCharts",{"asset":"GBPUSD_otc"}]')
    second = _write_har(tmp_path / "second.har", second_payload)
    report_path = tmp_path / "report.json"

    generate_pocket_discovery_reports(
        (str(first), str(second)),
        report_json=report_path,
        report_txt=tmp_path / "report.txt",
        catalog_json=tmp_path / "catalog.json",
        catalog_txt=tmp_path / "catalog.txt",
        protocol_md=tmp_path / "protocol.md",
    )
    payload = json.loads(report_path.read_text())

    assert "changeSymbol" in payload["comparison"][str(first)]
    assert "saveCharts" in payload["comparison"][str(second)]


def test_http_analyzer_ignores_static_chart_assets(tmp_path: Path) -> None:
    har_path = _write_har(
        tmp_path / "static.har",
        {
            "log": {
                "entries": [
                    {
                        "request": {"method": "GET", "url": "https://pocketoption.com/themes/cabinet/svg/icons/v2/chart.svg"},
                        "response": {"status": 200, "headers": [{"name": "content-type", "value": "image/svg+xml"}]},
                    }
                ]
            }
        },
    )
    result = load_har(har_path)

    assert analyze_http_endpoints(result.path, result.har or {}) == ()


def _write_har(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _sample_har(extra_event: str | None = None) -> dict:
    messages = [
        {"type": "send", "time": 1, "data": '42["changeSymbol",{"asset":"EURUSD_otc","period":300,"token":"sensitive-token"}]'},
        {"type": "receive", "time": 2, "data": '42["updateAssets",{"EURUSD_otc":{"payout":92,"open":true,"email":"renan@example.com"}}]'},
        {"type": "receive", "time": 3, "data": '42["updateHistoryNewFast",[{"time":1700000000,"open":1.1,"high":1.2,"low":1.0,"close":1.15}]]'},
        {"type": "receive", "time": 4, "data": '42["updateCharts",{"asset":"EURUSD_otc","period":300}]'},
        {"type": "receive", "time": 5, "data": '42["updateStream",{"asset":"EURUSD_otc","price":1.16,"time":1700000001}]'},
    ]
    if extra_event:
        messages.append({"type": "receive", "time": 6, "data": extra_event})
    return {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2026-07-16T12:00:00.000Z",
                    "request": {
                        "method": "GET",
                        "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket&token=sensitive-token",
                    },
                    "response": {"status": 101, "headers": []},
                    "_webSocketMessages": messages,
                },
                {
                    "request": {"method": "GET", "url": "https://pocketoption.com/api/assets?session=sensitive-token"},
                    "response": {
                        "status": 200,
                        "headers": [{"name": "content-type", "value": "application/json"}],
                        "content": {"text": '{"asset":"EURUSD_otc","token":"sensitive-token"}'},
                    },
                },
            ]
        }
    }
