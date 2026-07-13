from __future__ import annotations

from fastapi import APIRouter, Query

from app.market.chart.models import ChartSeries, ChartSeriesSummary
from app.market.runtime import market_chart_runtime_service

router = APIRouter(prefix="/market/chart", tags=["Market Chart"])


@router.get("/series")
def get_market_chart_series() -> dict:
    """Return read-only Candle Store series metadata for compact analysis screens."""

    return {
        "series": [_series_summary_to_response(summary) for summary in market_chart_runtime_service.get_available_series()],
    }


@router.get("")
def get_market_chart(
    active_id: int = Query(..., ge=1, description="Provider active_id stored in Candle Store."),
    raw_size: int = Query(..., ge=1, description="Provider raw candle size stored in Candle Store."),
    limit: int = Query(default=200, ge=1, le=1000, description="Maximum number of candles to return."),
) -> dict:
    """Return chart-ready candles from the read-only Candle Store API."""

    series = market_chart_runtime_service.get_series(active_id=active_id, raw_size=raw_size, limit=limit)
    return _series_to_response(series)


def _series_to_response(series: ChartSeries) -> dict:
    return {
        "provider": series.provider,
        "active_id": series.active_id,
        "symbol": series.symbol,
        "raw_size": series.raw_size,
        "count": len(series.candles),
        "candles": [
            {
                "time": candle.time,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
            }
            for candle in series.candles
        ],
    }


def _series_summary_to_response(summary: ChartSeriesSummary) -> dict:
    return {
        "provider": summary.provider,
        "active_id": summary.active_id,
        "symbol": summary.symbol,
        "raw_size": summary.raw_size,
        "count": summary.count,
        "latest_time": summary.latest_time,
    }
