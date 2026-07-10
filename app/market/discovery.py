from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDiscoveryBoundary:
    """Documents the market discovery boundary without changing runtime behavior."""

    selected_asset: str
    timeframe: str
    data_source: str
    availability: str
