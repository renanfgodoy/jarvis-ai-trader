from __future__ import annotations

from typing import Literal


TradingMarket = Literal["OTC", "Forex", "Crypto"]
TradingStrategy = Literal["Trend", "Price Action", "Support Resistance", "SMC", "ICT"]
TradingDecision = Literal["WAIT", "OBSERVE", "DO_NOT_TRADE"]
TradingRisk = Literal["LOW", "MEDIUM", "HIGH"]
