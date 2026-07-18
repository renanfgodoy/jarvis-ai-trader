from __future__ import annotations

from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.diagnostics import write_runtime_architecture_report
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.replay_transport import PocketReplayTransport
from app.market.providers.pocket.runtime import PocketMarketRuntime

DEFAULT_HARS = (
    ".jarvis_private/pocket_hars/pocketoption.com.har",
    ".jarvis_private/pocket_hars/pocketoption.com(1).har",
)


def main() -> None:
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=50, preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(PocketReplayTransport(DEFAULT_HARS), runtime)
    source.start()
    source.stop()
    payload = write_runtime_architecture_report(source)
    status = payload["runtime"]
    metrics = status["metrics"]
    print("Pocket Read-Only Runtime Demo")
    print("transport: REPLAY")
    print(f"sessions: {payload['transport'].get('sessions')}")
    print(f"events_received: {metrics.get('events_received')}")
    print(f"history_batches: {metrics.get('history_batches')}")
    print(f"historical_candles: {metrics.get('historical_candles_written')}")
    print(f"realtime_ticks: {metrics.get('ticks_processed')}")
    print(f"buckets: {len(status.get('buckets') or {})}")
    print(f"readiness: {status.get('readiness')}")
    print("runtime_guard: READ_ONLY")
    print("live_connection: DISABLED")


if __name__ == "__main__":
    main()
