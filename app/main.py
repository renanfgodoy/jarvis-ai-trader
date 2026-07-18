from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes import dev_market_selection
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        pass


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Plataforma proprietária de apoio à decisão em trading para Renan Godoy.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    app.include_router(dev_market_selection.router)

    @app.get("/", tags=["Root"])
    def root() -> dict:
        return {
            "message": "Friday AI Platform online",
            "version": settings.app_version,
            "docs": "/docs",
            "market_snapshot": f"{settings.api_prefix}/market/snapshot",
            "ai_decision": f"{settings.api_prefix}/ai/decision",
            "risk_check": f"{settings.api_prefix}/risk/check",
            "tradingview_webhook": f"{settings.api_prefix}/providers/tradingview/webhook",
            "signal_analyze": f"{settings.api_prefix}/signal/analyze",
            "quadcode_status": f"{settings.api_prefix}/quadcode/status",
            "dashboard_frontend": "http://127.0.0.1:5173",
            "live_tick": f"{settings.api_prefix}/live/tick",
            "live_websocket": "/api/v1/live/workspace/ws",
        }

    return app


app = create_app()
