from fastapi import APIRouter, Query

from app.models.candle import Timeframe
from app.models.scanner import AssetScannerResponse
from app.services.asset_scanner import AssetScannerService

router = APIRouter(prefix="/scanner", tags=["Asset Scanner"])


@router.get("/top-assets", response_model=AssetScannerResponse)
def scan_top_assets(
    timeframe: Timeframe = Query(default="M1", description="Timeframe analisado pelo scanner"),
    candle_limit: int = Query(default=50, ge=22, le=500, description="Quantidade de candles por ativo"),
    top: int = Query(default=12, ge=1, le=20, description="Quantidade de ativos retornados no ranking"),
    bankroll: float = Query(default=200.0, gt=0, description="Banca usada para simular aprovação de risco"),
    payout: float = Query(default=80.0, ge=0, le=100, description="Payout estimado para validação de risco"),
) -> AssetScannerResponse:
    """Analisa múltiplos ativos e retorna os melhores candidatos para observação."""
    return AssetScannerService().scan(
        timeframe=timeframe,
        candle_limit=candle_limit,
        top=top,
        bankroll=bankroll,
        payout=payout,
    )
