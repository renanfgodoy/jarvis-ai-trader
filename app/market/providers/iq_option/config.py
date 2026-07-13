from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class IQOptionProviderConfig:
    enabled: bool
    email: str | None
    password: str | None
    account_mode: str
    read_only: bool
    default_candle_limit: int
    poll_interval_seconds: float

    @property
    def configured(self) -> bool:
        return bool(self.email and self.password)


def load_iq_option_config() -> IQOptionProviderConfig:
    return IQOptionProviderConfig(
        enabled=settings.iq_option_provider_enabled,
        email=settings.iq_option_email,
        password=settings.iq_option_password,
        account_mode=settings.iq_option_account_mode,
        read_only=settings.iq_option_read_only,
        default_candle_limit=settings.iq_option_default_candle_limit,
        poll_interval_seconds=settings.iq_option_poll_interval_seconds,
    )
