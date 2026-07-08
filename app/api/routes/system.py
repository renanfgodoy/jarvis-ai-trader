from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/info")
def system_info() -> dict:
    """Retorna informações básicas do sistema."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "api_prefix": settings.api_prefix,
        "default_market_provider": settings.default_market_provider,
    }
