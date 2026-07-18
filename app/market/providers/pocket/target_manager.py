from __future__ import annotations

from urllib.parse import urlsplit

from app.market.providers.pocket.cdp_models import PocketCDPTarget


class PocketTargetManager:
    def __init__(self, trade_url: str = "https://pocketoption.com/") -> None:
        self.trade_url = trade_url
        parsed = urlsplit(trade_url)
        self.trade_host = parsed.netloc or "pocketoption.com"
        self.trade_path = parsed.path.rstrip("/")

    def select_target(self, targets: tuple[PocketCDPTarget, ...]) -> PocketCDPTarget | None:
        candidates: list[PocketCDPTarget] = []
        for target in targets:
            if target.type != "page":
                continue
            host = urlsplit(target.url).netloc
            if "127.0.0.1" in host or "localhost" in host:
                continue
            if "polarium" in host.lower():
                continue
            if "pocketoption.com" in host or host == self.trade_host:
                candidates.append(target)
        exact = self._configured_path_target(candidates)
        return exact or (candidates[0] if candidates else None)

    def _configured_path_target(self, targets: list[PocketCDPTarget]) -> PocketCDPTarget | None:
        if not self.trade_path:
            return None
        for target in targets:
            if urlsplit(target.url).path.rstrip("/") == self.trade_path:
                return target
        return None
