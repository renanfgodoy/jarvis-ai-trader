class MarketReaderService:
    """Serviço base do Market Reader. Será expandido na Sprint 2."""

    def status(self) -> dict:
        return {"module": "market_reader", "status": "initialized", "sprint": 1}
