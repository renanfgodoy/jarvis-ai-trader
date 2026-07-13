from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.market.providers.errors import ProviderCredentialsMissingError, ProviderDisabledError, ProviderValidationError
from app.market.providers.iq_option.series_integrity import IQOptionSeriesIntegrityAnalyzer
from app.market.providers.models import MarketCandleRequest
from app.market.runtime import iq_option_provider_config, iq_option_provider_runtime, market_candle_store, market_chart_runtime_service

router = APIRouter(prefix="/market/providers", tags=["Market Providers"])


@router.get("")
def list_market_providers() -> dict:
    return {"providers": [{"provider": "IQ_OPTION", "enabled": iq_option_provider_config.enabled, "read_only": True}]}


@router.get("/iq-option/status")
def iq_option_status() -> dict:
    status = iq_option_provider_runtime.provider.connection_status().sanitized()
    status["metrics"] = iq_option_provider_runtime.provider.metrics.sanitized()
    return status


@router.get("/iq-option/runtime/status")
def iq_option_runtime_status() -> dict:
    return iq_option_provider_runtime.runtime_status()


@router.post("/iq-option/connect")
async def iq_option_connect(request: Request) -> dict:
    body = await _safe_json_body(request)
    if any(key.lower() in {"email", "password", "token", "cookie", "authorization", "bearer", "ssid"} for key in body):
        raise HTTPException(status_code=400, detail={"error_code": "CREDENTIALS_NOT_ACCEPTED_BY_ENDPOINT"})
    try:
        return iq_option_provider_runtime.provider.connect().sanitized()
    except ProviderDisabledError as exc:
        raise HTTPException(status_code=403, detail={"error_code": exc.error_code}) from exc
    except ProviderCredentialsMissingError as exc:
        raise HTTPException(status_code=400, detail={"error_code": exc.error_code}) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"error_code": getattr(exc, "error_code", "IQ_OPTION_CONNECT_FAILED")}) from exc


@router.post("/iq-option/disconnect")
def iq_option_disconnect() -> dict:
    iq_option_provider_runtime.stop_polling()
    iq_option_provider_runtime.stop_realtime()
    return iq_option_provider_runtime.provider.disconnect().sanitized()


@router.get("/iq-option/assets")
def iq_option_assets(market_type: str = Query(default="OTC")) -> dict:
    result = iq_option_provider_runtime.list_assets_cached(market_type=market_type)
    if result.last_error_code and not result.assets:
        raise HTTPException(status_code=502, detail={"error_code": result.last_error_code})
    return {
        "provider": "IQ_OPTION",
        "market_type": market_type,
        "cache": result.sanitized(),
        "assets": [asset.sanitized() for asset in result.assets],
    }


@router.get("/iq-option/candles")
def iq_option_candles(
    symbol: str = Query(..., min_length=3),
    raw_size: int = Query(..., ge=1),
    limit: int = Query(default=1000, ge=1, le=5000),
    refresh_limit: int | None = Query(default=None, ge=1, le=50),
    market_type: str = Query(default="OTC"),
) -> dict:
    load_limit = refresh_limit if refresh_limit is not None else limit
    request = MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=load_limit, market_type=market_type)
    series_before = market_chart_runtime_service.get_provider_series("IQ_OPTION", symbol, raw_size, limit)
    result = None
    try:
        if series_before.candles and refresh_limit is None:
            iq_option_provider_runtime.refresh_history_background(request)
        else:
            result = iq_option_provider_runtime.load_history(request)
    except ProviderValidationError as exc:
        raise HTTPException(status_code=400, detail={"error_code": exc.error_code}) from exc
    except Exception as exc:
        if not series_before.candles:
            raise HTTPException(status_code=502, detail={"error_code": getattr(exc, "error_code", "IQ_OPTION_CANDLES_FAILED")}) from exc
    series = market_chart_runtime_service.get_provider_series("IQ_OPTION", symbol, raw_size, limit)
    return {
        "provider": "IQ_OPTION",
        "market_type": market_type,
        "symbol": symbol,
        "raw_size": raw_size,
        "limit": limit,
        "refresh_limit": refresh_limit,
        "load": result.sanitized() if result is not None else {"from_cache": True, "background_refresh": True},
        "chart": {
            "provider": series.provider,
            "symbol": series.symbol,
            "raw_size": series.raw_size,
            "count": len(series.candles),
            "candles": [
                {"time": candle.time, "open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close}
                for candle in series.candles
            ],
        },
    }


@router.get("/iq-option/realtime-candles")
def iq_option_realtime_candles(
    symbol: str = Query(..., min_length=3),
    raw_size: int = Query(..., ge=1),
    limit: int = Query(default=1000, ge=1, le=5000),
    market_type: str = Query(default="OTC"),
) -> dict:
    request = MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=20, market_type=market_type)
    try:
        result = iq_option_provider_runtime.load_realtime_update(request)
    except ProviderValidationError as exc:
        raise HTTPException(status_code=400, detail={"error_code": exc.error_code}) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"error_code": getattr(exc, "error_code", "IQ_OPTION_REALTIME_FAILED")}) from exc
    series = market_chart_runtime_service.get_provider_series("IQ_OPTION", symbol, raw_size, limit)
    return {
        "provider": "IQ_OPTION",
        "market_type": market_type,
        "symbol": symbol,
        "raw_size": raw_size,
        "limit": limit,
        "source_mode": result.source_mode,
        "load": result.sanitized(),
        "chart": {
            "provider": series.provider,
            "symbol": series.symbol,
            "raw_size": series.raw_size,
            "count": len(series.candles),
            "candles": [
                {"time": candle.time, "open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close}
                for candle in series.candles
            ],
        },
    }


@router.get("/iq-option/realtime-candles/stream")
async def iq_option_realtime_candles_stream(
    request: Request,
    symbol: str = Query(..., min_length=3),
    raw_size: int = Query(..., ge=1),
    market_type: str = Query(default="OTC"),
) -> StreamingResponse:
    candle_request = MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=20, market_type=market_type)
    subscription = iq_option_provider_runtime.begin_realtime_stream(candle_request)

    async def event_stream():
        last_signature = None
        last_heartbeat_at = 0.0
        try:
            while True:
                if await request.is_disconnected():
                    break
                if not iq_option_provider_runtime.is_realtime_stream_current(subscription):
                    break
                now = asyncio.get_running_loop().time()
                if now - last_heartbeat_at >= 10.0:
                    heartbeat = iq_option_provider_runtime.realtime_stream_heartbeat(subscription, candle_request)
                    if heartbeat is not None:
                        yield _sse("heartbeat", heartbeat.sanitized())
                    last_heartbeat_at = now
                try:
                    event, last_signature = await asyncio.to_thread(
                        iq_option_provider_runtime.next_realtime_stream_event,
                        subscription,
                        candle_request,
                        last_signature,
                    )
                except ProviderValidationError as exc:
                    yield _sse("error", {"error_code": exc.error_code})
                    break
                except Exception as exc:
                    yield _sse("error", {"error_code": getattr(exc, "error_code", "IQ_OPTION_REALTIME_STREAM_FAILED")})
                    await asyncio.sleep(1.0)
                    continue
                if event is not None:
                    yield _sse(event.event_type, event.sanitized())
                await asyncio.sleep(0.25)
        finally:
            iq_option_provider_runtime.end_realtime_stream(subscription)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/iq-option/series-integrity")
def iq_option_series_integrity(
    symbol: str = Query(..., min_length=3),
    raw_size: int = Query(..., ge=1),
) -> dict:
    return IQOptionSeriesIntegrityAnalyzer(market_candle_store).analyze(symbol=symbol, raw_size=raw_size).sanitized()


async def _safe_json_body(request: Request) -> dict[str, Any]:
    if not request.headers.get("content-length"):
        return {}
    try:
        body = await request.json()
    except Exception:
        return {}
    return body if isinstance(body, dict) else {}


def _sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n"
