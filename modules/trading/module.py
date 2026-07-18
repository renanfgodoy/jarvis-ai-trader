from __future__ import annotations

from shared.contracts import PlatformRequest, PlatformResponse
from sdk import BaseModule, ModuleRequest

from modules.trading.manifest import TRADING_MANIFEST
from modules.trading.metadata import TRADING_METADATA
from modules.trading.models import TradingRequest, TradingResponse
from modules.trading.services import TradingAnalyzer


class TradingModule(BaseModule):
    def __init__(self, analyzer: TradingAnalyzer | None = None) -> None:
        super().__init__(manifest=TRADING_MANIFEST, metadata=TRADING_METADATA)
        self.analyzer = analyzer or TradingAnalyzer()

    def run_sdk(self, request: ModuleRequest):
        return super().execute(request)

    def execute(self, request: TradingRequest) -> TradingResponse:
        return self.analyzer.analyze(self, request)

    def handle(self, request: PlatformRequest) -> PlatformResponse:
        return PlatformResponse(request_id=request.request_id, module=self.manifest().name, status="placeholder")
