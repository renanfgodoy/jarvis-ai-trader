class BacktestingService:
    """Serviço base do Backtesting Engine. Será expandido na Sprint 9."""

    def status(self) -> dict:
        return {"module": "backtesting", "status": "initialized", "sprint": 1}
