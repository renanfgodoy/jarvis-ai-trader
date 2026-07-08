from fastapi import APIRouter

from app.api.routes import ai, health, market, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(market.router)
api_router.include_router(ai.router)
