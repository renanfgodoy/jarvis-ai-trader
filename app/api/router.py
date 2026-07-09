from fastapi import APIRouter

from app.api.routes import ai, execution, health, market, providers, quadcode, risk, scanner, signal, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(market.router)
api_router.include_router(ai.router)
api_router.include_router(risk.router)
api_router.include_router(providers.router)
api_router.include_router(providers.manager_router)
api_router.include_router(quadcode.router)
api_router.include_router(signal.router)
api_router.include_router(scanner.router)
api_router.include_router(execution.router)
