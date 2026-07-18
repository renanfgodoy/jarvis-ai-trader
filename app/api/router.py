from fastapi import APIRouter

from app.api.routes import core_demo, health, market_chart, market_provider_v2, market_providers, risk, system, vision

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(core_demo.router)
api_router.include_router(market_chart.router)
api_router.include_router(market_provider_v2.router)
api_router.include_router(market_providers.router)
api_router.include_router(risk.router)
api_router.include_router(vision.router)
