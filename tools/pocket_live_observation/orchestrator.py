from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.error import URLError
from urllib.request import urlopen

from app.market.providers.pocket.cdp_client import PocketLocalCDPClient
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.diagnostics import (
    write_live_history_period_trace_reports,
    write_live_observation_reports,
    write_live_schema_trace_reports,
    write_multi_context_validation_reports,
    write_real_validation_report,
)
from app.market.providers.pocket.errors import PocketRuntimeError
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime

POCKET_UNSAFE_OBSERVATION_CONFIGURATION = "POCKET_UNSAFE_OBSERVATION_CONFIGURATION"
POCKET_CHROME_EXECUTABLE_NOT_FOUND = "POCKET_CHROME_EXECUTABLE_NOT_FOUND"

ObservationMode = str


@dataclass(frozen=True)
class ObservationDecision:
    mode: ObservationMode
    error_code: str | None = None


@dataclass(frozen=True)
class PocketChromeProcess:
    process: subprocess.Popen | None
    chrome_started: bool
    command: tuple[str, ...]


def resolve_pocket_observation_mode(config: PocketProviderConfig) -> ObservationDecision:
    if not config.pocket_real_observation_authorized:
        return ObservationDecision("FAKE_CDP_ONLY")
    safe = (
        config.pocket_cdp_enabled
        and config.pocket_cdp_observation_only
        and config.pocket_read_only
        and not config.pocket_live_connection_enabled
    )
    if safe:
        return ObservationDecision("REAL_PASSIVE_CDP")
    return ObservationDecision("BLOCKED_UNSAFE_CONFIGURATION", POCKET_UNSAFE_OBSERVATION_CONFIGURATION)


def config_from_env(env: Mapping[str, str] | None = None) -> PocketProviderConfig:
    values = env or os.environ
    return PocketProviderConfig(
        pocket_live_connection_enabled=_bool(values.get("POCKET_LIVE_CONNECTION_ENABLED"), False),
        pocket_read_only=_bool(values.get("POCKET_READ_ONLY"), True),
        pocket_cdp_enabled=_bool(values.get("POCKET_CDP_ENABLED"), False),
        pocket_cdp_debug_port=_int(values.get("POCKET_CDP_DEBUG_PORT"), 9230),
        pocket_cdp_profile_dir=values.get("POCKET_CDP_PROFILE_DIR") or ".jarvis_private/chrome-pocket-profile",
        pocket_cdp_open_browser=_bool(values.get("POCKET_CDP_OPEN_BROWSER"), True),
        pocket_cdp_observation_only=_bool(values.get("POCKET_CDP_OBSERVATION_ONLY"), True),
        pocket_real_observation_authorized=_bool(values.get("POCKET_REAL_OBSERVATION_AUTHORIZED"), False),
        pocket_close_browser_on_stop=_bool(values.get("POCKET_CLOSE_BROWSER_ON_STOP"), False),
        pocket_trade_url=values.get("POCKET_TRADE_URL") or "https://pocketoption.com/",
        preserve_store_on_stop=True,
    )


def build_chrome_command(config: PocketProviderConfig, *, executable: str | None = None) -> tuple[str, ...]:
    chrome = executable or os.environ.get("POCKET_CHROME_EXECUTABLE") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return (
        chrome,
        f"--remote-debugging-port={config.pocket_cdp_debug_port}",
        f"--user-data-dir={config.pocket_cdp_profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        config.pocket_trade_url,
    )


def start_chrome(config: PocketProviderConfig, *, executable: str | None = None) -> PocketChromeProcess:
    command = build_chrome_command(config, executable=executable)
    if not Path(command[0]).exists():
        raise PocketRuntimeError(POCKET_CHROME_EXECUTABLE_NOT_FOUND, "Pocket Chrome executable was not found.")
    Path(config.pocket_cdp_profile_dir).mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(command)
    return PocketChromeProcess(process=process, chrome_started=True, command=command)


def wait_for_cdp_endpoint(config: PocketProviderConfig, *, timeout_seconds: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{config.pocket_cdp_debug_port}/json/version", timeout=1.0) as response:
                return response.status == 200
        except (OSError, URLError):
            time.sleep(0.25)
    return False


def run_real_passive_observation(config: PocketProviderConfig) -> dict:
    print("Modo: REAL_PASSIVE_CDP")
    print(f"Chrome dedicado: iniciando na porta {config.pocket_cdp_debug_port}")
    print("Faça login manualmente na conta DEMO da Pocket.")
    print("Nenhuma mensagem será enviada pela Friday.")
    print("Pressione Control + C para encerrar.")
    chrome = start_chrome(config)
    if not wait_for_cdp_endpoint(config):
        raise PocketRuntimeError("POCKET_CDP_ENDPOINT_UNAVAILABLE", "Pocket CDP endpoint did not become available.")
    print("Aguardando target Pocket...")
    runtime = PocketMarketRuntime(config=config)
    transport = PocketCDPObservationTransport(PocketLocalCDPClient(port=config.pocket_cdp_debug_port), config=config)
    transport.live_history_trace.mark_chrome_started()
    source = PocketReadOnlyLiveSource(transport, runtime)
    try:
        source.start()
    except KeyboardInterrupt:
        pass
    finally:
        source.stop()
        if config.pocket_close_browser_on_stop and chrome.process is not None:
            chrome.process.terminate()
    report = write_live_observation_reports(
        source,
        {
            "observation_mode": "REAL_PASSIVE_CDP",
            "real_observation_authorized": config.pocket_real_observation_authorized,
            "cdp_port": config.pocket_cdp_debug_port,
            "chrome_started": chrome.chrome_started,
            "real_target_observed": source.status().get("transport", {}).get("target_found"),
        },
    )
    write_real_validation_report(
        source,
        {
            "observation_mode": "REAL_PASSIVE_CDP",
        },
    )
    write_live_schema_trace_reports(source)
    write_live_history_period_trace_reports(source)
    write_multi_context_validation_reports(source)
    return report


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
