from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PocketProviderConfig:
    pocket_provider_enabled: bool = False
    pocket_live_connection_enabled: bool = False
    pocket_read_only: bool = True
    pocket_history_required: int = 50
    preserve_store_on_stop: bool = False
    pocket_cdp_enabled: bool = False
    pocket_cdp_debug_port: int = 9230
    pocket_cdp_profile_dir: str = ".jarvis_private/chrome-pocket-profile"
    pocket_cdp_open_browser: bool = True
    pocket_cdp_observation_only: bool = True
    pocket_real_observation_authorized: bool = False
    pocket_close_browser_on_stop: bool = False
    pocket_trade_url: str = "https://pocketoption.com/"
