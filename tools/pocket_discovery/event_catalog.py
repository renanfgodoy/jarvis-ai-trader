from __future__ import annotations

from collections import defaultdict

from tools.pocket_discovery.models import Direction, EventCatalogEntry, WebSocketSummary
from tools.pocket_discovery.sanitizer import payload_shape


RESPONSIBILITY_BY_EVENT = {
    "changeSymbol": "Troca de ativo/timeframe",
    "updateStream": "Tempo real/ticks",
    "updateCharts": "Atualizacao de grafico/candles",
    "updateHistoryNewFast": "Historico de candles",
    "updateAssets": "Lista/estado de ativos",
    "saveCharts": "Persistencia/cache de grafico da pagina",
}


def build_event_catalog(sockets: tuple[WebSocketSummary, ...]) -> tuple[EventCatalogEntry, ...]:
    groups: dict[tuple[str, Direction], list] = defaultdict(list)
    for socket in sockets:
        for frame in socket.frames:
            if frame.event_name:
                if frame.frame_kind == "SOCKET_IO_BINARY_EVENT" and isinstance(frame.sample_sanitized, dict) and frame.sample_sanitized.get("_placeholder") is True:
                    continue
                groups[(frame.event_name, frame.direction)].append(frame)

    entries: list[EventCatalogEntry] = []
    for (event_name, direction), frames in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1])):
        first = frames[0]
        last = frames[-1]
        entries.append(
            EventCatalogEntry(
                event_name=event_name,
                direction=direction,
                count=len(frames),
                first_seen=first.timestamp,
                last_seen=last.timestamp,
                payload_shape=payload_shape(first.sample_sanitized),
                payload_keys=first.payload_keys,
                sample_sanitized=first.sample_sanitized,
                probable_responsibility=RESPONSIBILITY_BY_EVENT.get(event_name, "Nao classificado"),
                confidence="HIGH" if event_name in RESPONSIBILITY_BY_EVENT else "LOW",
            )
        )
    return tuple(entries)
