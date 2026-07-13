from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


AppEnvironment = Literal["development", "test", "production"]


class Settings(BaseSettings):
    """Centraliza as configurações principais do projeto."""

    app_name: str = "J.A.R.V.I.S AI TRADER"
    app_version: str = "0.24.0"
    environment: AppEnvironment = "development"
    api_prefix: str = "/api/v1"

    bankroll_base: float = 200.0
    risk_percentage: float = 5.0
    max_daily_wins: int = 3
    max_daily_losses: int = 2
    max_gale_allowed: int = 1
    minimum_payout: float = 75.0

    default_market_provider: str = "simulated"
    default_symbol: str = "EURUSD-OTC"
    default_timeframe: str = "M1"
    market_persistence_database_path: str = ".jarvis_cache/market/candles.sqlite3"
    market_persistence_retention_per_series: int = 1000
    market_candle_min_timestamp: int = 1_500_000_000
    market_candle_future_tolerance_seconds: int = 300

    iq_option_provider_enabled: bool = True
    iq_option_read_only: bool = True
    iq_option_account_mode: str = "PRACTICE"
    iq_option_default_candle_limit: int = 200
    iq_option_poll_interval_seconds: float = 1.0
    iq_option_email: str | None = None
    iq_option_password: str | None = None

    polarium_provider_enabled: bool = False

    # V0.21.0 — Polarium OAuth Session Engine
    # These settings are optional. Keep secrets only in the local .env.
    polarium_oauth_client_id: str | None = None
    polarium_oauth_authorize_url: str = "https://api.trade.polariumbroker.com/auth/oauth.v5/authorize"
    polarium_oauth_token_url: str = "https://api.trade.polariumbroker.com/auth/oauth.v5/token"
    polarium_oauth_redirect_uri: str = "http://127.0.0.1:8000/api/v1/polarium/oauth/callback"
    polarium_oauth_scope: str = "full offline_access"
    polarium_ws_url: str = "wss://ws.trade.polariumbroker.com/echo/websocket"

    # Backward-compatible ignored fields from older labs, so the backend does not crash
    # if the user's .env still has them. We do not use password login in V0.21.
    polarium_direct_login_url: str | None = None
    polarium_direct_email: str | None = None
    polarium_direct_password: str | None = None
    polarium_direct_ws_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def is_development_runtime_enabled(self) -> bool:
        return self.environment in {"development", "test"}


settings = Settings()
