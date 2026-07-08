from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Plataforma proprietária de apoio à decisão em trading para Renan Godoy.",
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["Root"])
    def root() -> dict:
        return {
            "message": "J.A.R.V.I.S AI TRADER online",
            "version": settings.app_version,
            "docs": "/docs",
        }

    return app


app = create_app()
