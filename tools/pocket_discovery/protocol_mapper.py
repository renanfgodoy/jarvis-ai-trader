from __future__ import annotations

from tools.pocket_discovery.models import EventCatalogEntry, PocketDiscoveryReport


def build_protocol_map(report: PocketDiscoveryReport) -> str:
    events = {entry.event_name for entry in report.event_catalog}
    lines = [
        "# Pocket Option Protocol Map",
        "",
        "Este mapa foi gerado somente a partir de evidencias sanitizadas dos HARs locais.",
        "",
        "```text",
        "LOGIN MANUAL",
        "    ↓",
        _step("Socket.IO connect", report.protocol == "Socket.IO / Engine.IO"),
        "    ↓",
        _step("sessao autenticada", "auth" in " ".join(events).lower() or bool(report.websocket_count)),
        "    ↓",
        _step("updateAssets", "updateAssets" in events),
        "    ↓",
        _step("changeSymbol(asset, period)", "changeSymbol" in events),
        "    ↓",
        _step("updateHistoryNewFast", "updateHistoryNewFast" in events),
        "    ↓",
        _step("updateCharts", "updateCharts" in events),
        "    ↓",
        _step("updateStream continuo", "updateStream" in events),
        "```",
        "",
        "## Eventos comprovados",
        "",
    ]
    if report.event_catalog:
        for entry in report.event_catalog:
            lines.append(f"- `{entry.event_name}` ({entry.direction}) - {entry.probable_responsibility}; count={entry.count}; confidence={entry.confidence}")
    else:
        lines.append("- Nenhum evento comprovado porque os HARs nao foram carregados.")
    lines.extend(
        [
            "",
            "## Decisao tecnica",
            "",
            f"- Classificacao: `{report.viability_classification}`",
            f"- Nota tecnica: `{report.technical_score}`",
            f"- Decisao: {report.adapter_decision}",
        ]
    )
    return "\n".join(lines)


def _step(label: str, confirmed: bool) -> str:
    return label if confirmed else f"{label} - NAO COMPROVADO"
