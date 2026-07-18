from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYNC_SOURCE = ROOT / "frontend/src/components/chart/RealCandleChart/sync.ts"
CHART_SOURCE = ROOT / "frontend/src/components/chart/RealCandleChart/index.tsx"
HOOK_SOURCE = ROOT / "frontend/src/hooks/useRealCandles.ts"
MARKET_CHART_SOURCE = ROOT / "frontend/src/pages/MarketChart.tsx"
LATENCY_AUDIT_SOURCE = ROOT / "frontend/src/utils/latencyAudit.ts"


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
    assert "reconcileRealCandleSeries(previousCandles, nextCandles, DEFAULT_LIMIT)" in source
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


def test_hook_requires_live_polarium_runtime_context_before_auto_selecting_series() -> None:
    source = read_source(HOOK_SOURCE)

    assert "const visibleActiveId = status.sessionContext.visibleActiveId" in source
    assert "if (!status.connected || visibleActiveId === null)" in source
    assert "const fallbackContext = followPolarium ? null : firstAvailableSeries(nextAvailableSeries)" in source
    assert "latestRawSizes" in source
    assert "return { activeId: visibleActiveId, rawSize: rawSizes[0] }" in source


def test_hook_clears_previous_polarium_series_when_live_active_changes_to_empty_series() -> None:
    source = read_source(HOOK_SOURCE)

    assert "isSwitchingSeries && payload.candles.length === 0 && followPolarium" in source
    assert "setCandles([])" in source
    assert "ATIVO NÃO IDENTIFICADO" in source


def test_market_chart_uses_polarium_context_even_before_first_candle() -> None:
    source = read_source(MARKET_CHART_SOURCE)

    assert "const polariumSession = polariumLive.sessionContext" in source
    assert "const polariumConnected = polariumSession.connectionStatus === 'ONLINE'" in source
    assert "const chartSymbol = POLARIUM_BASELINE_MODE ? polariumSession.displayName : polariumConnected ? polariumSession.displayName : displayedSymbol" in source
    assert "sessionContext={polariumSession}" in source


def test_polarium_session_context_is_published_as_single_source_of_truth() -> None:
    source = read_source(HOOK_SOURCE)
    context_source = read_source(ROOT / "frontend/src/contexts/PolariumSessionContext.ts")

    assert "PolariumSessionContext" in context_source
    assert "POLARIUM_SESSION_UPDATED" in context_source
    assert "publishPolariumSessionUpdate" in source
    assert "sessionContext: { ...sessionContext, candles }" in source


def test_polarium_history_bootstrap_progress_blocks_strategy_until_ready() -> None:
    market_chart_source = read_source(MARKET_CHART_SOURCE)
    context_source = read_source(ROOT / "frontend/src/contexts/PolariumSessionContext.ts")

    assert "historyState" in context_source
    assert "historyRequired" in context_source
    assert "bootstrapComplete" in context_source
    assert "formatPolariumHistoryProgress(polariumSession)" in market_chart_source
    assert "CARREGANDO HISTÓRICO" in market_chart_source
    assert "HISTÓRICO INSUFICIENTE" in market_chart_source
    assert "PRONTO PARA ANÁLISE" in market_chart_source


def test_latency_audit_records_frontend_pipeline_stages() -> None:
    chart_source = read_source(CHART_SOURCE)
    hook_source = read_source(HOOK_SOURCE)
    market_chart_source = read_source(MARKET_CHART_SOURCE)
    audit_source = read_source(LATENCY_AUDIT_SOURCE)

    assert "__FRIDAY_LATENCY_AUDIT__" in audit_source
    assert "friday-latency-audit" in audit_source
    assert "t5_frontend_received" in hook_source
    assert "t5_frontend_received" in market_chart_source
    assert "t6_frontend_merge_finished" in hook_source
    assert "t6_frontend_merge_finished" in market_chart_source
    assert "t7_series_update" in chart_source
    assert "t8_request_animation_frame" in market_chart_source
    assert "t9_frame_drawn" in chart_source
