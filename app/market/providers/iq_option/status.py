from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IQOptionProviderMetrics:
    connections: int = 0
    connection_failures: int = 0
    asset_requests: int = 0
    candle_requests: int = 0
    candle_batches: int = 0
    candles_received: int = 0
    candles_accepted: int = 0
    candles_rejected: int = 0
    poll_cycles: int = 0
    poll_failures: int = 0
    reconnects: int = 0

    def sanitized(self) -> dict:
        return {
            "connections": self.connections,
            "connection_failures": self.connection_failures,
            "asset_requests": self.asset_requests,
            "candle_requests": self.candle_requests,
            "candle_batches": self.candle_batches,
            "candles_received": self.candles_received,
            "candles_accepted": self.candles_accepted,
            "candles_rejected": self.candles_rejected,
            "poll_cycles": self.poll_cycles,
            "poll_failures": self.poll_failures,
            "reconnects": self.reconnects,
        }
