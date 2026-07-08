from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/architecture")
def get_architecture() -> dict:
    """Retorna a visão arquitetural inicial da plataforma."""
    return {
        "flow": [
            "Dashboard",
            "API",
            "AI Decision Engine",
            "Market Reader",
            "Database",
            "Machine Learning",
            "Backtesting",
        ],
        "modules": [
            "market_reader",
            "decision_engine",
            "risk_manager",
            "trade_journal",
            "statistics_engine",
            "backtesting",
            "ml_engine",
        ],
        "principles": [
            "SOLID",
            "Clean Code",
            "Modular Architecture",
            "Low Coupling",
            "High Scalability",
            "Testable Code",
        ],
    }
