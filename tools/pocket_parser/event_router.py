from __future__ import annotations

from tools.pocket_discovery.sanitizer import sanitize
from tools.pocket_parser.asset_parser import parse_change_symbol, parse_update_assets
from tools.pocket_parser.chart_parser import audit_update_charts
from tools.pocket_parser.history_parser import parse_history_batch
from tools.pocket_parser.models import PocketReplayResult, PocketSocketEvent, Rejection
from tools.pocket_parser.offline_store import PocketOfflineStore
from tools.pocket_parser.stream_parser import parse_update_stream

NON_MARKET_EVENTS = {"updateOpenedDeals", "updateClosedDeals", "signals/update", "auth", "auth/success"}


class PocketEventRouter:
    def __init__(self, store: PocketOfflineStore) -> None:
        self.store = store
        self.tick_sequence = 0

    def route(self, event: PocketSocketEvent, result: PocketReplayResult) -> None:
        if event.parse_error:
            result.parse_errors.append(Rejection("PARSE_ERROR", event.event_name or "UNKNOWN", event.source_har, event.session_index, event.frame_index, event.parse_error))
            return
        if event.event_name is None:
            return
        result.socketio_events += 1
        if event.event_name == "changeSymbol":
            try:
                result.change_symbols.append(parse_change_symbol(event.payload, event.timestamp))
            except ValueError as error:
                result.rejections.append(Rejection(str(error), "changeSymbol", event.source_har, event.session_index, event.frame_index, "invalid changeSymbol"))
        elif event.event_name == "updateHistoryNewFast":
            batch, rejections = parse_history_batch(event.payload, source_har=event.source_har, session_index=event.session_index, frame_index=event.frame_index)
            result.rejections.extend(rejections)
            if batch is not None:
                result.history_batches.append(batch)
                self.store.add_candles(batch.candles)
        elif event.event_name == "updateStream":
            ticks, rejections = parse_update_stream(
                event.payload,
                source_har=event.source_har,
                session_index=event.session_index,
                frame_index=event.frame_index,
                sequence_start=self.tick_sequence,
            )
            self.tick_sequence += len(ticks)
            result.ticks.extend(ticks)
            result.rejections.extend(rejections)
        elif event.event_name == "updateAssets":
            result.assets.extend(parse_update_assets(event.payload))
        elif event.event_name == "updateCharts":
            result.chart_updates.extend(audit_update_charts(event.payload))
        elif event.event_name not in NON_MARKET_EVENTS:
            result.unknown_events[event.event_name] = result.unknown_events.get(event.event_name, 0) + 1
            sanitize(event.payload)

