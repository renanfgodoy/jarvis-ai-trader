from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check() -> dict:
    """Verifica se a API está online e retorna regras oficiais de risco."""
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
        "official_phrases": [
            "Primeiro proteger a banca. Depois crescer a banca.",
            "Não buscamos mais operações. Buscamos operações melhores.",
        ],
    }
