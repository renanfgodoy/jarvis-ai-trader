from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools.pocket_discovery.event_catalog import build_event_catalog
from tools.pocket_discovery.har_loader import load_har
from tools.pocket_discovery.http_analyzer import analyze_http_endpoints
from tools.pocket_discovery.models import EventCatalogEntry, PocketDiscoveryReport, WebSocketSummary
from tools.pocket_discovery.protocol_mapper import build_protocol_map
from tools.pocket_discovery.websocket_analyzer import analyze_websockets

DEFAULT_REPORT_JSON = Path(".jarvis_cache/diagnostics/pocket_discovery_report.json")
DEFAULT_REPORT_TXT = Path(".jarvis_cache/diagnostics/pocket_discovery_report.txt")
DEFAULT_CATALOG_JSON = Path(".jarvis_cache/diagnostics/pocket_event_catalog.json")
DEFAULT_CATALOG_TXT = Path(".jarvis_cache/diagnostics/pocket_event_catalog.txt")
DEFAULT_PROTOCOL_MD = Path(".jarvis_cache/diagnostics/pocket_protocol_map.md")


def generate_pocket_discovery_reports(
    har_paths: tuple[str, ...],
    *,
    report_json: Path = DEFAULT_REPORT_JSON,
    report_txt: Path = DEFAULT_REPORT_TXT,
    catalog_json: Path = DEFAULT_CATALOG_JSON,
    catalog_txt: Path = DEFAULT_CATALOG_TXT,
    protocol_md: Path = DEFAULT_PROTOCOL_MD,
) -> PocketDiscoveryReport:
    load_results = tuple(load_har(path) for path in har_paths)
    sockets: list[WebSocketSummary] = []
    http_endpoints = []
    for result in load_results:
        if result.har is None:
            continue
        sockets.extend(analyze_websockets(result.path, result.har))
        http_endpoints.extend(analyze_http_endpoints(result.path, result.har))

    event_catalog = build_event_catalog(tuple(sockets))
    missing = tuple(result.path for result in load_results if not result.exists or not result.valid_json)
    report = PocketDiscoveryReport(
        har_paths=har_paths,
        missing_hars=missing,
        total_requests=sum(result.entry_count for result in load_results),
        websocket_count=len(sockets),
        main_socket=_main_socket(sockets),
        protocol=_protocol(sockets),
        sent_events=_events_by_direction(event_catalog, "sent"),
        received_events=_events_by_direction(event_catalog, "received"),
        confirmed_preliminary_change_symbol=_confirmed_preliminary_change_symbol(event_catalog),
        sockets=tuple(sockets),
        http_endpoints=tuple(http_endpoints),
        event_catalog=event_catalog,
        viability_classification=_viability_classification(missing, event_catalog),
        technical_score=_technical_score(missing, event_catalog),
        adapter_decision=_adapter_decision(missing, event_catalog),
        risks=_risks(missing, event_catalog),
        gaps=_gaps(missing, event_catalog),
    )
    _write_outputs(report, report_json, report_txt, catalog_json, catalog_txt, protocol_md)
    return report


def _write_outputs(
    report: PocketDiscoveryReport,
    report_json: Path,
    report_txt: Path,
    catalog_json: Path,
    catalog_txt: Path,
    protocol_md: Path,
) -> None:
    for path in (report_json, report_txt, catalog_json, catalog_txt, protocol_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(_report_payload(report), indent=2, ensure_ascii=False), encoding="utf-8")
    report_txt.write_text(_report_text(report), encoding="utf-8")
    catalog_json.write_text(json.dumps([asdict(entry) for entry in report.event_catalog], indent=2, ensure_ascii=False), encoding="utf-8")
    catalog_txt.write_text(_catalog_text(report.event_catalog), encoding="utf-8")
    protocol_md.write_text(build_protocol_map(report), encoding="utf-8")


def _report_payload(report: PocketDiscoveryReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["comparison"] = _compare_hars(report)
    payload["technical_notes"] = _technical_notes(report)
    return payload


def _report_text(report: PocketDiscoveryReport) -> str:
    lines = [
        "Friday Trade - Pocket Option Protocol Discovery",
        f"HARs analisados: {', '.join(report.har_paths)}",
        f"HARs ausentes/invalidos: {', '.join(report.missing_hars) if report.missing_hars else 'nenhum'}",
        f"requests_total={report.total_requests}",
        f"websocket_count={report.websocket_count}",
        f"main_socket={report.main_socket}",
        f"protocol={report.protocol}",
        f"sent_events={', '.join(report.sent_events) if report.sent_events else 'nenhum'}",
        f"received_events={', '.join(report.received_events) if report.received_events else 'nenhum'}",
        f"preliminary_change_symbol_confirmed={report.confirmed_preliminary_change_symbol}",
        f"viability={report.viability_classification}",
        f"technical_score={report.technical_score}",
        f"adapter_decision={report.adapter_decision}",
        "",
        "Sockets:",
    ]
    if report.sockets:
        for socket in report.sockets:
            lines.append(
                f"- {socket.classification} {socket.host}{socket.path} transport={socket.transport} "
                f"EIO={socket.socket_io_version} sent={socket.frames_sent} received={socket.frames_received} events={','.join(socket.event_names)}"
            )
    else:
        lines.append("- nenhum socket comprovado")
    lines.extend(["", "Riscos:"])
    lines.extend(f"- {risk}" for risk in report.risks)
    lines.extend(["", "Lacunas:"])
    lines.extend(f"- {gap}" for gap in report.gaps)
    return "\n".join(lines)


def _catalog_text(entries: tuple[EventCatalogEntry, ...]) -> str:
    if not entries:
        return "Nenhum evento catalogado.\n"
    return "\n".join(
        f"{entry.event_name} direction={entry.direction} count={entry.count} keys={','.join(entry.payload_keys)} responsibility={entry.probable_responsibility}"
        for entry in entries
    )


def _main_socket(sockets: list[WebSocketSummary]) -> str | None:
    market_sockets = [socket for socket in sockets if socket.classification == "MARKET_SOCKET"]
    candidates = market_sockets or sockets
    if not candidates:
        return None
    selected = max(candidates, key=lambda socket: socket.frames_sent + socket.frames_received)
    return selected.url_sanitized


def _protocol(sockets: list[WebSocketSummary]) -> str | None:
    if any(socket.socket_io_version or any(frame.frame_kind.startswith("SOCKET_IO") for frame in socket.frames) for socket in sockets):
        return "Socket.IO / Engine.IO"
    if sockets:
        return "WebSocket"
    return None


def _events_by_direction(entries: tuple[EventCatalogEntry, ...], direction: str) -> tuple[str, ...]:
    return tuple(sorted(entry.event_name for entry in entries if entry.direction == direction))


def _confirmed_preliminary_change_symbol(entries: tuple[EventCatalogEntry, ...]) -> bool:
    for entry in entries:
        if entry.event_name != "changeSymbol" or entry.direction != "sent":
            continue
        sample = entry.sample_sanitized
        if isinstance(sample, dict) and sample.get("asset") == "EURUSD_otc" and sample.get("period") == 300:
            return True
    return False


def _technical_score(missing: tuple[str, ...], entries: tuple[EventCatalogEntry, ...]) -> float:
    if missing:
        return 0.0
    events = {entry.event_name for entry in entries}
    score = 0.0
    for event in ("changeSymbol", "updateHistoryNewFast", "updateStream", "updateAssets"):
        if event in events:
            score += 2.0
    if "updateCharts" in events:
        score += 1.0
    if "saveCharts" in events:
        score += 0.5
    return min(score, 10.0)


def _viability_classification(missing: tuple[str, ...], entries: tuple[EventCatalogEntry, ...]) -> str:
    score = _technical_score(missing, entries)
    if score >= 8.5:
        return "EXCELLENT"
    if score >= 7.5:
        return "GOOD"
    if score >= 4.0:
        return "LIMITED"
    return "NOT_RECOMMENDED"


def _adapter_decision(missing: tuple[str, ...], entries: tuple[EventCatalogEntry, ...]) -> str:
    if missing:
        return "NAO AVANCAR: HARs obrigatorios ausentes ou invalidos."
    required = {"changeSymbol", "updateHistoryNewFast", "updateStream", "updateAssets"}
    events = {entry.event_name for entry in entries}
    if required <= events and _technical_score(missing, entries) >= 7.5:
        return "PODE AVANCAR PARA DESENHO DO PocketMarketAdapter READ-ONLY."
    return "NAO AVANCAR AINDA: evidencias insuficientes para adapter."


def _risks(missing: tuple[str, ...], entries: tuple[EventCatalogEntry, ...]) -> tuple[str, ...]:
    risks = ["HAR pode conter credenciais; todos os relatórios usam sanitização local."]
    if missing:
        risks.append("Analise de protocolo bloqueada por HAR ausente ou invalido.")
    if not any(entry.event_name == "updateStream" for entry in entries):
        risks.append("Tempo real nao comprovado.")
    if not any(entry.event_name == "updateHistoryNewFast" for entry in entries):
        risks.append("Historico OHLC nao comprovado.")
    return tuple(risks)


def _gaps(missing: tuple[str, ...], entries: tuple[EventCatalogEntry, ...]) -> tuple[str, ...]:
    if missing:
        return ("Fornecer os dois HARs nos caminhos especificados.",)
    events = {entry.event_name for entry in entries}
    gaps = []
    for event in ("changeSymbol", "updateAssets", "updateHistoryNewFast", "updateStream"):
        if event not in events:
            gaps.append(f"Evento {event} nao comprovado nos HARs.")
    return tuple(gaps)


def _compare_hars(report: PocketDiscoveryReport) -> dict[str, Any]:
    by_har: dict[str, set[str]] = {}
    for socket in report.sockets:
        by_har.setdefault(socket.har_path, set()).update(socket.event_names)
    return {har_path: sorted(events) for har_path, events in by_har.items()}


def _technical_notes(report: PocketDiscoveryReport) -> dict[str, Any]:
    events = {entry.event_name for entry in report.event_catalog}
    return {
        "asset_change": "COMPROVADO" if "changeSymbol" in events else "NAO_COMPROVADO",
        "timeframe": "COMPROVADO_EM_changeSymbol" if report.confirmed_preliminary_change_symbol else "NAO_COMPROVADO",
        "history": "COMPROVADO" if "updateHistoryNewFast" in events or "updateCharts" in events else "NAO_COMPROVADO",
        "ticks": "COMPROVADO" if "updateStream" in events else "NAO_COMPROVADO",
        "assets": "COMPROVADO" if "updateAssets" in events else "NAO_COMPROVADO",
        "payout": "BUSCAR_EM_updateAssets" if "updateAssets" in events else "NAO_COMPROVADO",
        "expiration": "NAO_COMPROVADO",
    }
