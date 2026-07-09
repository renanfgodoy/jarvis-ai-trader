from fastapi import APIRouter, Query

from app.core.config import settings
from app.models.risk import RiskCheckRequest, RiskCheckResponse
from app.services.risk_manager import RiskManagerService

router = APIRouter(prefix="/risk", tags=["Risk Manager"])


@router.get("/check", response_model=RiskCheckResponse)
def check_risk(
    bankroll: float = Query(default=settings.bankroll_base, gt=0, description="Banca atual"),
    entry_value: float | None = Query(default=None, gt=0, description="Valor da entrada. Se vazio, usa 5% da banca"),
    daily_wins: int = Query(default=0, ge=0, description="WINs do dia"),
    daily_losses: int = Query(default=0, ge=0, description="LOSSes do dia"),
    gale_used: int = Query(default=0, ge=0, description="Gales usados na operação"),
    payout: float = Query(default=80.0, ge=0, le=100, description="Payout estimado"),
) -> RiskCheckResponse:
    """Valida se uma operação respeita as regras oficiais de proteção de banca."""
    request = RiskCheckRequest(
        bankroll=bankroll,
        entry_value=entry_value,
        daily_wins=daily_wins,
        daily_losses=daily_losses,
        gale_used=gale_used,
        payout=payout,
    )
    return RiskManagerService().check(request)
