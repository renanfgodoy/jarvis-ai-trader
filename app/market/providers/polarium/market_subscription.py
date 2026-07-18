from __future__ import annotations

import time


class PolariumMarketSubscriptionFactory:
    def subscribe_candles_generated(self, active_id: int) -> dict:
        return _plural_payload("subscribeMessage", active_id)

    def unsubscribe_candles_generated(self, active_id: int) -> dict:
        return _plural_payload("unsubscribeMessage", active_id)


def _plural_payload(name: str, active_id: int) -> dict:
    return {
        "name": name,
        "request_id": f"friday_runtime_candles_generated_{name}_{active_id}_{int(time.time() * 1000)}",
        "msg": {
            "name": "candles-generated",
            "params": {"routingFilters": {"active_id": active_id}},
        },
    }
