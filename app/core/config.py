from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centraliza as configurações principais do projeto."""

    app_name: str = "J.A.R.V.I.S AI TRADER"
    app_version: str = "0.3.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    bankroll_base: float = 200.0
    risk_percentage: float = 5.0
    max_daily_wins: int = 3
    max_daily_losses: int = 2

    default_market_provider: str = "simulated"
    default_symbol: str = "EURUSD-OTC"
    default_timeframe: str = "M1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
