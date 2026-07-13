from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYNC_SOURCE = ROOT / "frontend/src/components/chart/RealCandleChart/sync.ts"
CHART_SOURCE = ROOT / "frontend/src/components/chart/RealCandleChart/index.tsx"
HOOK_SOURCE = ROOT / "frontend/src/hooks/useRealCandles.ts"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sync_contract_detects_new_candle() -> None:
    source = read_source(SYNC_SOURCE)

    assert "next.length === previous.length + 1" in source
    assert "time > previous[previous.length - 1].time" in source
    assert "return next[next.length - 1].time > previous[previous.length - 1].time ? 'append' : 'reset'" in source


def test_sync_contract_detects_updated_current_candle() -> None:
    source = read_source(SYNC_SOURCE)

    assert "previous.length === next.length" in source
    assert "previous[previous.length - 1].time === next[next.length - 1].time" in source
    assert "return 'update'" in source


def test_sync_contract_handles_unchanged_and_empty_series() -> None:
    source = read_source(SYNC_SOURCE)

    assert "previous.length === 0 && next.length === 0" in source
    assert "return 'unchanged'" in source
    assert "previous.length === 0 || next.length === 0" in source
    assert "return 'reset'" in source


def test_real_candle_chart_uses_incremental_updates_without_recreating_chart() -> None:
    source = read_source(CHART_SOURCE)

    assert source.count("createChart(") == 1
    assert "candleSeries.update(data[data.length - 1])" in source
    assert "candleSeries.setData(data)" in source
    assert "syncAction === 'append' || syncAction === 'update'" in source


def test_use_real_candles_polls_and_skips_unnecessary_renders() -> None:
    source = read_source(HOOK_SOURCE)

    assert "window.setInterval" in source
    assert "SYNC_INTERVAL_MS" in source
    assert "isRequestInFlight" in source
    assert "reconcileRealCandleSeries(previousCandles, payload.candles, DEFAULT_LIMIT)" in source
    assert "Object.is(updatedCandles, previousCandles) ? previousCandles : updatedCandles" in source


def test_sync_merges_partial_responses_without_shrinking_history() -> None:
    source = read_source(SYNC_SOURCE)

    assert "mergeCandlesByTime(previous, next, limit)" in source
    assert "const mergedByTime = new Map<number, TCandle>()" in source
    assert "for (const candle of previous)" in source
    assert "for (const candle of next)" in source
    assert "mergedByTime.set(candle.time, candle)" in source


def test_sync_sorts_deduplicates_and_trims_only_oldest_candles() -> None:
    source = read_source(SYNC_SOURCE)

    assert ".sort((left, right) => left.time - right.time)" in source
    assert "return candles.slice(candles.length - limit)" in source
    assert "trimToLatest(merged, limit)" in source


def test_hook_guards_against_stale_or_wrong_context_responses() -> None:
    source = read_source(HOOK_SOURCE)

    assert "requestSequenceRef" in source
    assert "lastAppliedRequestRef" in source
    assert "requestSequence <= lastAppliedRequestRef.current" in source
    assert "if (!sameSeries(payloadContext, nextDisplayedContext))" in source
