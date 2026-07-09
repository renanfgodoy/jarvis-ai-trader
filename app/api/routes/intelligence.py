from fastapi import APIRouter, Query

from app.models.candle import Timeframe
from app.models.intelligence import MarketIntelligenceResponse, MarketIntelligenceScannerResponse
from app.services.confluence_engine import ConfluenceEngineService
from app.services.market_intelligence import MarketIntelligenceService

router = APIRouter(prefix="/intelligence", tags=["Market Intelligence"])


@router.get("/analyze", response_model=MarketIntelligenceResponse)
def analyze_market_intelligence(
    symbol: str = Query(default="EURUSD-OTC", min_length=3),
    timeframe: Timeframe = Query(default="M1"),
    payout: float = Query(default=80.0, ge=0, le=100),
    minimum_score: int = Query(default=80, ge=0, le=100),
    minimum_payout: float = Query(default=75.0, ge=0, le=100),
    candle_limit: int = Query(default=80, ge=30, le=500),
) -> MarketIntelligenceResponse:
    """Analisa um ativo com score explicável de confluência técnica."""
    return ConfluenceEngineService().analyze(
        symbol=symbol,
        timeframe=timeframe,
        payout=payout,
        minimum_score=minimum_score,
        minimum_payout=minimum_payout,
        candle_limit=candle_limit,
    )


@router.get("/scanner/top", response_model=MarketIntelligenceScannerResponse)
def scan_market_intelligence(
    timeframe: Timeframe = Query(default="M1"),
    top: int = Query(default=12, ge=1, le=20),
    payout: float = Query(default=80.0, ge=0, le=100),
    minimum_score: int = Query(default=80, ge=0, le=100),
    minimum_payout: float = Query(default=75.0, ge=0, le=100),
    candle_limit: int = Query(default=80, ge=30, le=500),
) -> MarketIntelligenceScannerResponse:
    """Retorna Top N por score de confluência, payout e status operacional."""
    return MarketIntelligenceService().scan(
        timeframe=timeframe,
        top=top,
        payout=payout,
        minimum_score=minimum_score,
        minimum_payout=minimum_payout,
        candle_limit=candle_limit,
    )
