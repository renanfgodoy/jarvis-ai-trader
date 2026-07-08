from fastapi import APIRouter

from app.core.config import settings
from app.core.constants import OFFICIAL_PHRASES

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check() -> dict:
    """Confirma que a API está online e retorna informações básicas do sistema."""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "risk_profile": {
            "bankroll_base": settings.bankroll_base,
            "risk_percentage": settings.risk_percentage,
            "max_daily_wins": settings.max_daily_wins,
            "max_daily_losses": settings.max_daily_losses,
        },
        "official_phrases": OFFICIAL_PHRASES,
    }
