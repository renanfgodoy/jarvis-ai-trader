from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Thread
from typing import Any, Mapping

from app.core.config import Settings
from app.market.providers.base import MarketProvider, ProviderFactory, ProviderRegistry
from app.market.providers.pocket.builders import FakePocketProviderBuilder, PocketProviderBuilder
from app.market.providers.pocket.cdp_client import PocketLocalCDPClient
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime

POCKET_CHART_UNSAFE_CONFIGURATION = "POCKET_CHART_UNSAFE_CONFIGURATION"


@dataclass(frozen=True, slots=True)
class ProviderManagerConfig:
    provider_v2_enabled: bool = False
    current_provider: str = "POLARIUM"
    pocket_chart_integration_enabled: bool = False
    pocket_cdp_enabled: bool = False
    pocket_real_observation_authorized: bool = False
    pocket_read_only: bool = True
    pocket_live_connection_enabled: bool = False
    pocket_cdp_debug_port: int = 9230
    pocket_cdp_profile_dir: str = ".jarvis_private/chrome-pocket-profile"
    pocket_trade_url: str = "https://pocketoption.com/"
    pocket_history_required: int = 50


@dataclass(frozen=True, slots=True)
class ProviderManagerStatus:
    enabled: bool
    current_provider: str
    registered_providers: tuple[str, ...]
    running_providers: tuple[str, ...]
    provider_running: bool
    context: Mapping[str, Any] | None
    readiness: Mapping[str, Any] | None
    health: Mapping[str, Any] | None
    safe_configuration: bool
    last_error_code: str | None = None
    outbound_messages_originated_by_friday: int = 0
    errors: tuple[str, ...] = field(default_factory=tuple)


class ProviderManager:
    def __init__(
        self,
        config: ProviderManagerConfig,
        *,
        factory: ProviderFactory | None = None,
        registry: ProviderRegistry | None = None,
        diagnostics_path: Path | str = ".jarvis_cache/diagnostics",
    ) -> None:
        self.config = config
        self.factory = factory or ProviderFactory()
        self.registry = registry or ProviderRegistry()
        self.diagnostics_path = Path(diagnostics_path)
        self._running: set[str] = set()
        self._errors: list[str] = []
        self._pocket_runtime: PocketMarketRuntime | None = None
        self._pocket_live_source: PocketReadOnlyLiveSource | None = None
        self._pocket_thread: Thread | None = None
        self._initialized = False
        self.outbound_messages_originated_by_friday = 0

    @classmethod
    def from_settings(cls, settings: Settings) -> "ProviderManager":
        return cls(
            ProviderManagerConfig(
                provider_v2_enabled=settings.market_provider_v2_enabled,
                current_provider=settings.market_provider_current.upper(),
                pocket_chart_integration_enabled=settings.pocket_chart_integration_enabled,
                pocket_cdp_enabled=settings.pocket_cdp_enabled,
                pocket_real_observation_authorized=settings.pocket_real_observation_authorized,
                pocket_read_only=settings.pocket_read_only,
                pocket_live_connection_enabled=settings.pocket_live_connection_enabled,
                pocket_cdp_debug_port=settings.pocket_cdp_port,
                pocket_cdp_profile_dir=settings.pocket_cdp_profile_dir,
                pocket_trade_url=settings.pocket_trade_url,
                pocket_history_required=settings.pocket_history_required,
            )
        )

    def initialize(self) -> None:
        if self._initialized:
            return
        self._register_builders()
        if self.config.provider_v2_enabled and self.config.current_provider == "POCKET":
            self._ensure_pocket_registered()
            self.registry.set_current("POCKET")
        self._initialized = True
        self.write_diagnostics()

    def current_provider(self) -> MarketProvider | None:
        return self.registry.current()

    def get_provider(self, provider_name: str | None = None) -> MarketProvider:
        requested = (provider_name or self.config.current_provider).upper()
        if requested == "POCKET" and not self.registry.exists("POCKET"):
            self._ensure_pocket_registered()
        return self.registry.get(requested)

    def start_current(self) -> None:
        if not self.config.provider_v2_enabled or self.config.current_provider != "POCKET":
            return
        self._validate_pocket_chart_configuration()
        provider = self.get_provider("POCKET")
        if "POCKET" in self._running:
            return
        provider.start()
        self._running.add("POCKET")
        if self.config.pocket_cdp_enabled:
            self._start_pocket_observer()
        self.write_diagnostics()

    def stop_current(self) -> None:
        provider = self.registry.current()
        if provider is None:
            return
        provider_name = provider.provider_name()
        if provider_name == "POCKET":
            self._stop_pocket_observer()
        if provider_name in self._running:
            provider.stop()
            self._running.discard(provider_name)
        self.write_diagnostics()

    def shutdown(self) -> None:
        self._stop_pocket_observer()
        for provider_name in tuple(self._running):
            try:
                self.registry.get(provider_name).stop()
            finally:
                self._running.discard(provider_name)
        self.write_diagnostics()

    def status(self) -> ProviderManagerStatus:
        provider = self.registry.current()
        context: Mapping[str, Any] | None = None
        readiness: Mapping[str, Any] | None = None
        health: Mapping[str, Any] | None = None
        if provider is not None:
            provider_context = provider.get_context()
            context = asdict(provider_context)
            if provider_context.symbol and provider_context.period:
                readiness = asdict(provider.get_readiness(provider_context.symbol, provider_context.period))
            health = asdict(provider.health())
        safe_configuration = self._is_pocket_chart_configuration_safe() if self.config.current_provider == "POCKET" else True
        return ProviderManagerStatus(
            enabled=self.config.provider_v2_enabled,
            current_provider=self.config.current_provider,
            registered_providers=self.registry.list(),
            running_providers=tuple(sorted(self._running)),
            provider_running=self.config.current_provider in self._running,
            context=context,
            readiness=readiness,
            health=health,
            safe_configuration=safe_configuration,
            last_error_code=self._errors[-1] if self._errors else None,
            outbound_messages_originated_by_friday=self.outbound_messages_originated_by_friday,
            errors=tuple(self._errors),
        )

    def status_dict(self) -> dict[str, Any]:
        return asdict(self.status())

    def write_diagnostics(self, extra: Mapping[str, Any] | None = None) -> None:
        self.diagnostics_path.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            **self.status_dict(),
            "chart_requests": 0,
            "chart_responses": 0,
            "frontend_active_key": None,
            "frontend_received_count": 0,
            "frontend_rendered_count": 0,
            "stale_responses_ignored": 0,
            "cross_provider_fallbacks": 0,
            "errors": tuple(self._errors),
        }
        if extra:
            payload.update(dict(extra))
        (self.diagnostics_path / "pocket_chart_integration_report.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.diagnostics_path / "pocket_chart_integration_report.txt").write_text(
            _diagnostic_text(payload),
            encoding="utf-8",
        )

    def _register_builders(self) -> None:
        if not self.factory.has_builder("POCKET"):
            self.factory.register_builder("POCKET", PocketProviderBuilder())
        if not self.factory.has_builder("FAKE_POCKET"):
            self.factory.register_builder("FAKE_POCKET", FakePocketProviderBuilder())

    def _ensure_pocket_registered(self) -> None:
        if self.registry.exists("POCKET"):
            return
        runtime = self._pocket_runtime or PocketMarketRuntime(config=self._pocket_config())
        self._pocket_runtime = runtime
        self.registry.register(self.factory.create("POCKET", {"runtime": runtime}))

    def _start_pocket_observer(self) -> None:
        if self._pocket_thread and self._pocket_thread.is_alive():
            return
        if self._pocket_runtime is None:
            self._ensure_pocket_registered()
        assert self._pocket_runtime is not None
        client = PocketLocalCDPClient(port=self.config.pocket_cdp_debug_port)
        transport = PocketCDPObservationTransport(client, config=self._pocket_config())
        self._pocket_live_source = PocketReadOnlyLiveSource(transport, self._pocket_runtime)

        def _run() -> None:
            try:
                assert self._pocket_live_source is not None
                self._pocket_live_source.start()
            except Exception as exc:  # pragma: no cover - runtime safety boundary
                self._errors.append(type(exc).__name__)
                self.write_diagnostics()

        self._pocket_thread = Thread(target=_run, name="pocket-provider-v2-observer", daemon=True)
        self._pocket_thread.start()

    def _stop_pocket_observer(self) -> None:
        if self._pocket_live_source is not None:
            self._pocket_live_source.stop()
        if self._pocket_thread and self._pocket_thread.is_alive():
            self._pocket_thread.join(timeout=5)
        self._pocket_live_source = None
        self._pocket_thread = None

    def _pocket_config(self) -> PocketProviderConfig:
        return PocketProviderConfig(
            pocket_provider_enabled=self.config.provider_v2_enabled and self.config.current_provider == "POCKET",
            pocket_live_connection_enabled=self.config.pocket_live_connection_enabled,
            pocket_read_only=self.config.pocket_read_only,
            pocket_history_required=self.config.pocket_history_required,
            preserve_store_on_stop=True,
            pocket_cdp_enabled=self.config.pocket_cdp_enabled,
            pocket_cdp_debug_port=self.config.pocket_cdp_debug_port,
            pocket_cdp_profile_dir=self.config.pocket_cdp_profile_dir,
            pocket_real_observation_authorized=self.config.pocket_real_observation_authorized,
            pocket_trade_url=self.config.pocket_trade_url,
        )

    def _validate_pocket_chart_configuration(self) -> None:
        if self._is_pocket_chart_configuration_safe():
            return
        self._errors.append(POCKET_CHART_UNSAFE_CONFIGURATION)
        self.write_diagnostics()
        raise RuntimeError(POCKET_CHART_UNSAFE_CONFIGURATION)

    def _is_pocket_chart_configuration_safe(self) -> bool:
        return (
            self.config.provider_v2_enabled
            and self.config.current_provider == "POCKET"
            and self.config.pocket_chart_integration_enabled
            and self.config.pocket_cdp_enabled
            and self.config.pocket_real_observation_authorized
            and self.config.pocket_read_only
            and not self.config.pocket_live_connection_enabled
        )


def _diagnostic_text(payload: Mapping[str, Any]) -> str:
    lines = ["Pocket Chart Integration Diagnostic"]
    for key in sorted(payload):
        lines.append(f"{key}: {payload[key]}")
    return "\n".join(lines) + "\n"
