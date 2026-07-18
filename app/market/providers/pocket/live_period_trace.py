from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.market.providers.pocket.cdp_models import PocketObservedFrame, PocketObservedSocket
from app.market.providers.pocket.live_schema_trace import structural_shape
from tools.pocket_discovery.models import ParsedSocketIOFrame
from tools.pocket_parser.asset_parser import parse_change_symbol
from tools.pocket_parser.chart_parser import audit_update_charts
from tools.pocket_parser.utils import SUPPORTED_PERIODS

PERIOD_TO_TIMEFRAME = {60: "M1", 300: "M5", 900: "M15"}


@dataclass
class PocketLivePeriodTrace:
    period_sources: list[dict[str, Any]] = field(default_factory=list)
    atomic_contexts: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    last_atomic_asset: str | None = None
    last_atomic_period: int | None = None

    def record_event(
        self,
        *,
        event_name: str | None,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        if not event_name:
            return
        if event_name == "changeSymbol":
            self._record_change_symbol(payload, parsed, frame, socket)
        elif event_name == "chafor":
            self._record_chafor(payload, parsed, frame, socket)
        elif event_name == "updateCharts":
            self._record_update_charts(payload, parsed, frame, socket)
        elif event_name == "updateAssets":
            self._record_shape_source(event_name, payload, parsed, frame, socket, source_classification="ASSET_CATALOG")

    def report(self) -> dict[str, Any]:
        return {
            "period_mapping": PERIOD_TO_TIMEFRAME,
            "sources": self.period_sources[:100],
            "source_count": len(self.period_sources),
            "atomic_contexts": self.atomic_contexts[:100],
            "atomic_context_count": len(self.atomic_contexts),
            "conflicts": self.conflicts[:50],
            "final_period_source": self.final_period_source(),
            "context_classification": self.context_classification(),
            "current_asset": self.last_atomic_asset,
            "current_period": self.last_atomic_period,
            "current_timeframe": PERIOD_TO_TIMEFRAME.get(self.last_atomic_period or 0),
            "analysis_blocked": self.last_atomic_asset is None or self.last_atomic_period is None,
            "analysis_block_reason": None if self.last_atomic_asset and self.last_atomic_period else "POCKET_HISTORY_NOT_READY",
        }

    def final_period_source(self) -> str:
        if any(item.get("classification") == "PERIOD_SOURCE_CONFIRMED_CHANGE_SYMBOL" for item in self.period_sources):
            return "changeSymbol"
        if any(item.get("classification") == "PERIOD_SOURCE_CANDIDATE_CHAFOR" for item in self.period_sources):
            return "chafor"
        if any(item.get("classification") == "PERIOD_SOURCE_CANDIDATE_UPDATE_CHARTS" for item in self.period_sources):
            return "updateCharts"
        return "UNKNOWN"

    def context_classification(self) -> str:
        if self.conflicts:
            return "CONTEXT_SOURCE_CONFLICT"
        if self.last_atomic_asset and self.last_atomic_period:
            return "ATOMIC_CONTEXT_CONFIRMED"
        if self.period_sources:
            return "PARTIAL_CONTEXT_IGNORED"
        return "UNKNOWN"

    def _record_change_symbol(
        self,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        try:
            changed = parse_change_symbol(payload, frame.timestamp)
        except ValueError:
            self._record_shape_source("changeSymbol", payload, parsed, frame, socket, source_classification="PERIOD_INVALID")
            return
        self._record_source(
            event_name="changeSymbol",
            direction=frame.direction,
            timestamp=frame.timestamp,
            socket_classification=socket.classification,
            frame_prefix=parsed.raw_type,
            asset=changed.asset,
            period=changed.period,
            period_path="$.period",
            asset_path="$.asset",
            classification="PERIOD_SOURCE_CONFIRMED_CHANGE_SYMBOL",
            confidence="HIGH",
        )
        self._publish_atomic_context(changed.asset, changed.period, "changeSymbol", frame.timestamp)

    def _record_chafor(
        self,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        asset, period = _extract_asset_period(payload)
        classification = "PERIOD_SOURCE_CANDIDATE_CHAFOR" if asset and period in SUPPORTED_PERIODS else "MARKET_CONTROL_ONLY"
        self._record_source(
            event_name="chafor",
            direction=frame.direction,
            timestamp=frame.timestamp,
            socket_classification=socket.classification,
            frame_prefix=parsed.raw_type,
            asset=asset,
            period=period,
            period_path=_period_path(payload),
            asset_path=_asset_path(payload),
            classification=classification,
            confidence="MEDIUM" if classification == "PERIOD_SOURCE_CANDIDATE_CHAFOR" else "LOW",
        )
        if asset and period in SUPPORTED_PERIODS:
            self._publish_atomic_context(asset, int(period), "chafor", frame.timestamp)

    def _record_update_charts(
        self,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        audits = audit_update_charts(payload)
        for item in audits:
            asset = item.get("symbol") if isinstance(item.get("symbol"), str) else None
            period = _coerce_period(item.get("chart_period") or item.get("fast_timeframe"))
            self._record_source(
                event_name="updateCharts",
                direction=frame.direction,
                timestamp=frame.timestamp,
                socket_classification=socket.classification,
                frame_prefix=parsed.raw_type,
                asset=asset,
                period=period,
                period_path="settings.chartPeriod|settings.fastTimeframe",
                asset_path="settings.symbol",
                classification="PERIOD_SOURCE_CANDIDATE_UPDATE_CHARTS" if period in SUPPORTED_PERIODS else "VISUAL_STATE_ONLY",
                confidence="MEDIUM" if period in SUPPORTED_PERIODS else "LOW",
            )
            if asset and period in SUPPORTED_PERIODS:
                self._publish_atomic_context(asset, int(period), "updateCharts", frame.timestamp)

    def _record_shape_source(
        self,
        event_name: str,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
        *,
        source_classification: str,
    ) -> None:
        shape = structural_shape(payload)
        self.period_sources.append(
            {
                "event_name": event_name,
                "direction": frame.direction,
                "timestamp": frame.timestamp,
                "socket_classification": socket.classification,
                "frame_prefix": parsed.raw_type,
                "asset_path": shape["candidate_asset_paths"][:5],
                "period_path": [],
                "asset": None,
                "period": None,
                "timeframe": None,
                "classification": source_classification,
                "confidence": "LOW",
            }
        )

    def _record_source(
        self,
        *,
        event_name: str,
        direction: str,
        timestamp: float | None,
        socket_classification: str,
        frame_prefix: str,
        asset: str | None,
        period: int | None,
        period_path: str | None,
        asset_path: str | None,
        classification: str,
        confidence: str,
    ) -> None:
        self.period_sources.append(
            {
                "event_name": event_name,
                "direction": direction,
                "timestamp": timestamp,
                "socket_classification": socket_classification,
                "frame_prefix": frame_prefix,
                "asset_path": asset_path,
                "period_path": period_path,
                "asset": asset,
                "period": period,
                "timeframe": PERIOD_TO_TIMEFRAME.get(period or 0),
                "classification": classification,
                "confidence": confidence,
            }
        )

    def _publish_atomic_context(self, asset: str, period: int, source: str, timestamp: float | None) -> None:
        if period not in SUPPORTED_PERIODS:
            self.atomic_contexts.append({"source": source, "asset": asset, "period": period, "classification": "STALE_PERIOD_IGNORED", "timestamp": timestamp})
            return
        if self.last_atomic_asset and self.last_atomic_period and (asset, period) != (self.last_atomic_asset, self.last_atomic_period):
            self.conflicts.append(
                {
                    "old_asset": self.last_atomic_asset,
                    "old_period": self.last_atomic_period,
                    "new_asset": asset,
                    "new_period": period,
                    "source": source,
                    "timestamp": timestamp,
                }
            )
        self.last_atomic_asset = asset
        self.last_atomic_period = period
        self.atomic_contexts.append(
            {
                "source": source,
                "asset": asset,
                "period": period,
                "timeframe": PERIOD_TO_TIMEFRAME[period],
                "classification": "ATOMIC_CONTEXT_CONFIRMED",
                "timestamp": timestamp,
                "bucket_key": f"POCKET:{asset}:{period}",
            }
        )


def _extract_asset_period(payload: object) -> tuple[str | None, int | None]:
    if isinstance(payload, dict):
        asset = payload.get("asset") or payload.get("symbol")
        period = _coerce_period(payload.get("period") or payload.get("timeframe") or payload.get("tf"))
        return (asset if isinstance(asset, str) else None, period)
    if isinstance(payload, list):
        flat = list(_flatten(payload))
        asset = next((item for item in flat if isinstance(item, str) and (item.endswith("_otc") or item.isupper())), None)
        period = next((_coerce_period(item) for item in flat if _coerce_period(item) in SUPPORTED_PERIODS), None)
        return asset, period
    return None, None


def _asset_path(payload: object) -> str | None:
    if isinstance(payload, dict):
        if "asset" in payload:
            return "$.asset"
        if "symbol" in payload:
            return "$.symbol"
    if isinstance(payload, list):
        return "$[][]"
    return None


def _period_path(payload: object) -> str | None:
    if isinstance(payload, dict):
        for key in ("period", "timeframe", "tf"):
            if key in payload:
                return f"$.{key}"
    if isinstance(payload, list):
        return "$[][]"
    return None


def _coerce_period(value: object) -> int | None:
    if isinstance(value, str) and value.upper() in {"M1", "M5", "M15"}:
        return {"M1": 60, "M5": 300, "M15": 900}[value.upper()]
    try:
        period = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return period


def _flatten(value: object):
    if isinstance(value, list):
        for item in value:
            yield from _flatten(item)
    else:
        yield value
