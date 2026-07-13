from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKET_CHART = ROOT / "frontend/src/pages/MarketChart.tsx"
REAL_CANDLE_CHART = ROOT / "frontend/src/components/chart/RealCandleChart/index.tsx"
USE_REAL_CANDLES = ROOT / "frontend/src/hooks/useRealCandles.ts"
SYNC_SOURCE = ROOT / "frontend/src/components/chart/RealCandleChart/sync.ts"
SIDEBAR = ROOT / "frontend/src/components/Sidebar/index.tsx"
MAIN_LAYOUT = ROOT / "frontend/src/layouts/MainLayout.tsx"
APP_NAVIGATION = ROOT / "frontend/src/hooks/useAppNavigation.ts"
BACKEND_CONFIG = ROOT / "app/core/config.py"


def test_compact_workspace_uses_real_series_controls() -> None:
    source = MARKET_CHART.read_text()

    assert "IQ Option" in source
    assert "formatRawSize" in source
    assert "useRealCandles" not in source
    assert "Polarium Browser Live" not in source
    assert "Seguir Polarium" not in source
    assert "Active ID" not in source


def test_compact_workspace_does_not_invent_trade_decisions() -> None:
    source = MARKET_CHART.read_text()

    assert "Nenhuma estratégia carregada" in source
    assert "Nenhuma selecionada" in source
    assert "Aguardando configuração" in source
    assert "Nenhuma análise ativa" in source
    assert "0 avaliadas" in source
    assert "Nenhum cálculo operacional" in source
    assert "AGUARDAR" not in source
    assert "CALL" not in source
    assert "PUT" not in source
    assert "probabilidade" not in source.lower()
    assert "score" not in source.lower()


def test_compact_workspace_uses_responsive_chart_height() -> None:
    source = MARKET_CHART.read_text()

    assert "h-[calc(100dvh-218px)]" in source
    assert "min-h-[420px]" in source
    assert "max-h-[700px]" in source
    assert "h-[620px]" not in source


def test_real_candle_chart_allows_compact_height_without_changing_default() -> None:
    source = REAL_CANDLE_CHART.read_text()

    assert "chartClassName = 'h-[620px]'" in source
    assert "compact = false" in source
    assert "className={`relative ${chartClassName}`}" in source
    assert "function formatRawSize" in source


def test_real_candles_hook_uses_series_endpoint_and_no_fixed_ids() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "/market/chart/series" in source
    assert "DEFAULT_ACTIVE_ID" not in source
    assert "DEFAULT_RAW_SIZE" not in source
    assert "followPolarium" in source
    assert "enabled?: boolean" in source
    assert "if (!enabled)" in source
    assert "}, [enabled, followPolarium, requestedActiveId, requestedRawSize]);" in source


def test_real_chart_uses_observed_symbol_as_display_label() -> None:
    page = MARKET_CHART.read_text()
    chart = REAL_CANDLE_CHART.read_text()
    hook = USE_REAL_CANDLES.read_text()

    assert "symbol={displayedSymbol !== 'Não disponível' ? displayedSymbol : null}" in page
    assert "assetLabel: activeSymbol ?? 'Não disponível'" in hook
    assert "symbol ?? 'Ativo não identificado'" in chart


def test_auto_selection_requires_atomic_chart_probe_pair_with_candles() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "resolveActiveSeries(statusPayload, nextAvailableSeries)" in source
    assert "const tracedCount = status.last_trace?.chart_api_probe?.count" in source
    assert "tracedCount > 0" in source
    assert "hasAvailableSeries(availableSeries, tracedContext)" in source


def test_auto_selection_does_not_fabricate_pairs_from_independent_lists() -> None:
    source = USE_REAL_CANDLES.read_text()
    resolver = source.split("export function resolveActiveSeries", 1)[1].split("export function hasAvailableSeries", 1)[0]

    assert "active_ids_seen" not in resolver
    assert "raw_sizes_seen" not in resolver


def test_hook_preserves_displayed_candles_during_empty_or_incomplete_polling() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "shouldPreserveDisplayedCandles" in source
    assert "shouldKeepPreviousCandles" in source
    assert "if (!payload.candles.length && previousCandles.length)" in source
    assert "return previousCandles" in source
    assert "candlesLengthRef.current > 0" in source


def test_manual_selection_is_prioritized_when_follow_polarium_is_disabled() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "const validManualContext = manualContext && (hasAvailableSeries(nextAvailableSeries, manualContext) || sameSeries(manualContext, displayedContext))" in source
    assert ": validManualContext ?? displayedContext ?? fallbackContext" in source


def test_follow_polarium_keeps_last_valid_auto_series_across_polling_gaps() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "lastValidAutoContextRef" in source
    assert "lastValidAutoContextRef.current = autoContext" in source
    assert "? autoContext ?? lastValidAutoContextRef.current ?? displayedContext ?? fallbackContext" in source


def test_follow_polarium_interval_is_not_recreated_by_each_chart_update() -> None:
    source = USE_REAL_CANDLES.read_text()

    assert "displayedContextRef.current = activeId !== null && rawSize !== null" in source
    assert "}, [enabled, followPolarium, requestedActiveId, requestedRawSize]);" in source


def test_monotonic_stream_preserves_six_candles_when_api_returns_two() -> None:
    source = SYNC_SOURCE.read_text()

    assert "mergeCandlesByTime" in source
    assert "for (const candle of previous)" in source
    assert "for (const candle of next)" in source
    assert "mergedByTime.set(candle.time, candle)" in source


def test_monotonic_stream_empty_response_preserves_history() -> None:
    source = SYNC_SOURCE.read_text()

    assert "if (!next.length)" in source
    assert "return trimToLatest(previous, limit)" in source


def test_monotonic_stream_updates_same_timestamp_and_appends_new_timestamp() -> None:
    source = SYNC_SOURCE.read_text()

    assert "mergedByTime.set(candle.time, candle)" in source
    assert "classifyRealCandleSync(previous, candles)" in source
    assert "return 'update'" in source
    assert "return next[next.length - 1].time > previous[previous.length - 1].time ? 'append' : 'reset'" in source


def test_iq_option_live_polling_uses_small_refresh_and_preserves_history() -> None:
    source = MARKET_CHART.read_text()

    assert "const IQ_BOOTSTRAP_LIMIT = 1000" in source
    assert "const IQ_REFRESH_LIMIT = 5" in source
    assert "const IQ_POLL_INTERVAL_MS = 5000" in source
    assert "const shouldRefresh = refresh && hasLoadedInitialCandles" in source
    assert "limit: String(shouldRefresh ? IQ_REFRESH_LIMIT : IQ_BOOTSTRAP_LIMIT)" in source
    assert "params.set('refresh_limit', String(IQ_REFRESH_LIMIT))" in source
    assert "mergeIqOptionCandles(previousCandles, nextCandles)" in source
    assert "mergeCandlesByTime(previousCandles, contextCandles, IQ_BOOTSTRAP_LIMIT)" in source
    assert "window.setInterval" in source


def test_iq_option_realtime_polling_uses_worker_cache_without_replacing_chart() -> None:
    source = MARKET_CHART.read_text()
    chart = REAL_CANDLE_CHART.read_text()

    assert "const IQ_REALTIME_POLL_INTERVAL_MS = 1000" in source
    assert "const IQ_REALTIME_TIMEOUT_MS = 3000" in source
    assert "/market/providers/iq-option/realtime-candles" in source
    assert "function loadIqRealtime" in source
    assert "parseIqSourceMode(payload)" in source
    assert "setIqSourceMode(sourceMode)" in source
    assert "window.clearInterval(realtimeIntervalId)" in source
    assert "if (fallbackPollingEnabled)" in source
    assert "type IQSourceMode = 'CHECKING' | 'NEAR_REALTIME' | 'SNAPSHOT' | 'STALE' | 'NO_DATA'" in source
    assert "candleSeries.update(data[data.length - 1])" in chart


def test_iq_option_realtime_push_uses_sse_with_polling_fallback() -> None:
    source = MARKET_CHART.read_text()

    assert "new EventSource(`${API_BASE_URL}/market/providers/iq-option/realtime-candles/stream?" in source
    assert "eventSource.addEventListener('candle'" in source
    assert "eventSource.addEventListener('heartbeat'" in source
    assert "eventSource.onerror" in source
    assert "fallbackPollingEnabled = true" in source
    assert "setIqDeliveryState('POLLING_FALLBACK')" in source
    assert "setIqDeliveryState('SSE')" in source
    assert "setIqDeliveryState('CONNECTING')" in source
    assert "setIqDeliveryState('DISCONNECTED')" in source
    assert "IQ_PUSH_HEARTBEAT_TIMEOUT_MS" in source
    assert "eventSource?.close()" in source


def test_iq_option_realtime_push_applies_candles_on_next_animation_frame() -> None:
    source = MARKET_CHART.read_text()

    assert "window.requestAnimationFrame" in source
    assert "window.cancelAnimationFrame(animationFrameId)" in source
    assert "pendingPushEvent" in source
    assert "eventsCoalesced" in source
    assert "mergeIqOptionCandles(previousCandles, [latestPushEvent.candle as RealChartCandle])" in source
    assert "deliveryMsForEvent(latestPushEvent, appliedAt)" in source


def test_iq_option_realtime_push_uses_sequence_and_context_guards() -> None:
    source = MARKET_CHART.read_text()

    assert "lastAppliedPushSequence" in source
    assert "event.sequence <= lastAppliedPushSequence" in source
    assert "matchesIqRealtimeContext(event, expectedSymbol, expectedRawSize, iqMarketType)" in source
    assert "event.provider === 'IQ_OPTION'" in source
    assert "event.symbol === symbol" in source
    assert "event.raw_size === rawSize" in source
    assert "event.market_type === marketType" in source


def test_iq_option_realtime_push_does_not_interpolate_or_create_prices() -> None:
    source = MARKET_CHART.read_text()

    assert "parseIqRealtimeStreamEvent" in source
    assert "Number(candleRecord.open)" in source
    assert "Number(candleRecord.high)" in source
    assert "Number(candleRecord.low)" in source
    assert "Number(candleRecord.close)" in source
    assert "interpolate" not in source.lower()
    assert "synthetic" not in source.lower()


def test_iq_option_realtime_push_hud_shows_delivery_metrics() -> None:
    source = MARKET_CHART.read_text()

    assert "Diagnóstico DEV" in source
    assert "Eventos de candle" in source
    assert "Atualizações do gráfico" in source
    assert "Eventos coalescidos" in source
    assert "Latência local média" in source
    assert "Latência local p95" in source
    assert "Última resposta" in source
    assert "Próxima vela" in source
    assert "Sequência" in source
    assert "Fallbacks" in source
    assert "expanded ? 'Recolher' : 'Expandir'" in source
    assert "onToggle={() => setIqDiagnosticsExpanded" in source


def test_iq_option_operator_mode_uses_human_market_status() -> None:
    source = MARKET_CHART.read_text()

    assert "type FridayUiMode = 'OPERATOR' | 'DEVELOPER'" in source
    assert "FRIDAY_UI_MODE_STORAGE_KEY" in source
    assert "readStoredFridayUiMode()" in source
    assert "return localStorage.getItem(FRIDAY_UI_MODE_STORAGE_KEY) === 'DEVELOPER' ? 'DEVELOPER' : 'OPERATOR'" in source
    assert "MERCADO ATIVO" in source
    assert "MERCADO LENTO" in source
    assert "DADOS LIMITADOS" in source
    assert "DADOS ATRASADOS" in source
    assert "VERIFICANDO MERCADO" in source
    assert "break-words" not in source
    assert "break-all" not in source
    assert "[word-break:normal]" in source
    assert "[overflow-wrap:normal]" in source
    assert "[hyphens:none]" in source


def test_friday_v1_operator_mode_hides_technical_status_bar() -> None:
    source = MARKET_CHART.read_text()
    chart = REAL_CANDLE_CHART.read_text()
    header = (ROOT / "frontend/src/components/Header/index.tsx").read_text()
    sidebar = SIDEBAR.read_text()

    assert "function CompactStatusBar" not in source
    assert "function StatusPill" not in source
    assert "text-ellipsis" not in source
    assert "<Control label=\"Provider\">" not in source
    assert "<CompactStatusBar" not in source
    assert "FridayStrategyEnginePanel" in source
    assert "MarketHealthBadge" in source
    assert "OperatorContextPanel" not in source
    assert "fridayUiMode === 'DEVELOPER'" in source
    assert "StatusPill" not in header
    assert "Hora local" not in header
    assert "Usuário" not in header
    assert "Ambiente" not in sidebar
    assert "Execução real bloqueada" not in sidebar
    assert "Candle Store" not in chart
    assert "Aguardando candles reais salvos no CandleStore" not in chart


def test_iq_option_delivery_states_are_explicit_and_do_not_mark_connecting_as_sse() -> None:
    source = MARKET_CHART.read_text()

    assert "type IQDeliveryState = 'CONNECTING' | 'SSE' | 'POLLING_FALLBACK' | 'RECONNECTING' | 'DISCONNECTED'" in source
    assert "if (deliveryState === 'SSE') return 'SSE'" in source
    assert "if (deliveryState === 'POLLING_FALLBACK') return 'POLLING 1s'" in source
    assert "return 'CONECTANDO'" in source
    assert "Abrindo EventSource" in source
    assert "Polling de segurança" in source


def test_friday_v1_developer_mode_preserves_diagnostics_without_running_by_default() -> None:
    source = MARKET_CHART.read_text()

    assert "const [fridayUiMode, setFridayUiMode]" in source
    assert "{fridayUiMode === 'DEVELOPER' && (" in source
    assert "Diagnóstico DEV" in source
    assert "Latência local média" in source
    assert "Eventos de candle" in source
    assert "Fallbacks" in source
    assert "Provider" in source
    assert "CandleStore" in source
    assert "raw_size" in source
    assert "DEV" in source
    assert "OPERADOR" in source


def test_friday_strategy_engine_foundation_contract_is_present() -> None:
    source = MARKET_CHART.read_text()

    assert "type FridayStrategyDefinition" in source
    assert "type FridayStrategyConfluence" in source
    assert "id: string" in source
    assert "name: string" in source
    assert "description: string" in source
    assert "author: string" in source
    assert "version: string" in source
    assert "supportedMarkets: IQMarketType[]" in source
    assert "supportedTimeframes: number[]" in source
    assert "status: FridayStrategyStatus" in source
    assert "readiness: FridayStrategyReadiness" in source
    assert "confluences: FridayStrategyConfluence[]" in source
    assert "const FRIDAY_STRATEGIES: FridayStrategyDefinition[] = []" in source


def test_friday_strategy_engine_persists_only_interface_selection() -> None:
    source = MARKET_CHART.read_text()

    assert "const FRIDAY_STRATEGY_STORAGE_KEY = 'friday.strategy.selected'" in source
    assert "const [selectedStrategyId, setSelectedStrategyId]" in source
    assert "localStorage.setItem(FRIDAY_STRATEGY_STORAGE_KEY, selectedStrategyId)" in source
    assert "localStorage.removeItem(FRIDAY_STRATEGY_STORAGE_KEY)" in source
    assert "onSelectStrategy={setSelectedStrategyId}" in source


def test_friday_strategy_engine_initial_state_is_empty_and_neutral() -> None:
    source = MARKET_CHART.read_text()

    assert "FRIDAY STRATEGY" in source
    assert "Nenhuma estratégia carregada" in source
    assert "Nenhuma selecionada" in source
    assert "Aguardando configuração" in source
    assert "Confluências" in source
    assert "0 avaliadas" in source
    assert "Decisão" in source
    assert "Nenhuma análise ativa" in source
    assert "Selecione uma estratégia para iniciar a leitura do mercado." in source
    assert "Nenhum cálculo operacional, estatística ou decisão é gerado nesta fundação." in source
    assert "Backtest" not in source


def test_operator_experience_removes_administrative_header_and_sidebar() -> None:
    header = (ROOT / "frontend/src/components/Header/index.tsx").read_text()
    sidebar = SIDEBAR.read_text()
    layout = MAIN_LAYOUT.read_text()

    assert "API" not in header
    assert "Provider" not in header
    assert "Conta" not in header
    assert "Moeda" not in header
    assert "OFFLINE" not in header
    assert "Hora local" not in header
    assert "Usuário" not in header
    assert "brand.operatorName" not in header
    assert "useSystemStatus" not in layout
    assert "Ambiente" not in sidebar
    assert "brand.environment" not in sidebar
    assert "brand.version" not in sidebar


def test_operator_experience_keeps_only_essential_controls_and_strategy_panel() -> None:
    source = MARKET_CHART.read_text()

    assert "<Control label=\"Mercado\">" in source
    assert "<Control label=\"Ativo\">" in source
    assert "<Control label=\"Timeframe\">" in source
    assert "Próxima vela" in source
    assert "MarketHealthBadge" in source
    assert "FridayStrategyEnginePanel" in source
    assert "OperatorContextPanel" not in source


def test_iq_option_polling_cannot_replace_bootstrap_before_first_candles() -> None:
    source = MARKET_CHART.read_text()

    assert "let hasLoadedInitialCandles = false" in source
    assert "const shouldRefresh = refresh && hasLoadedInitialCandles" in source
    assert "if (shouldRefresh)" in source
    assert "hasLoadedInitialCandles = true" in source


def test_iq_option_polling_validates_response_context_before_merge() -> None:
    source = MARKET_CHART.read_text()

    assert "const expectedSymbol = iqSymbol" in source
    assert "const expectedRawSize = iqRawSize" in source
    assert "payload.provider !== 'IQ_OPTION'" in source
    assert "payload.symbol !== expectedSymbol" in source
    assert "Number(payload.raw_size) !== expectedRawSize" in source
    assert "mergeIqOptionCandles(previousCandles, nextCandles)" in source


def test_iq_option_context_hides_follow_polarium_and_uses_plain_counter() -> None:
    source = MARKET_CHART.read_text()

    assert "Seguir Polarium" not in source
    assert "IQ Option Read Only" in source
    assert "value={`${iqCandles.length} candles`}" in source
    assert "504 de 100" not in source


def test_iq_only_market_chart_does_not_mount_polarium_runtime() -> None:
    source = MARKET_CHART.read_text()

    assert "useRealCandles" not in source
    assert "browser-bridge/status" not in source
    assert "/market/chart/series" not in source
    assert "active_id" not in source
    assert "POLARIUM" not in source
    assert "controller.abort()" in source
    assert "window.clearInterval(intervalId)" in source


def test_iq_option_assets_use_connect_and_controlled_retry() -> None:
    source = MARKET_CHART.read_text()

    assert "ensureIqOptionConnected(iqConnectPromiseRef)" in source
    assert "const IQ_ASSET_RETRY_DELAYS_MS = [1000, 2000, 4000]" in source
    assert "attempt <= IQ_ASSET_RETRY_DELAYS_MS.length" in source
    assert "isRetryableIqAssetError(error)" in source
    assert "chooseIqSymbol(current, assets, iqMarketType)" in source
    assert "marketType === 'OTC' ? 'EURUSD-OTC' : 'EURUSD'" in source
    assert "asset.symbol === preferredSymbol" in source
    assert "Tentar novamente" in source


def test_iq_option_assets_warm_connection_even_when_status_is_connected() -> None:
    source = MARKET_CHART.read_text()
    ensure_connection = source.split("async function ensureIqOptionConnected", 1)[1].split("export function parseIqAssetsResponse", 1)[0]

    assert "logIqFlow('status_request_finished', { connected: Boolean(status.connected) })" in ensure_connection
    assert "if (status.connected)" not in ensure_connection
    assert "logIqFlow('connect_started', { alreadyConnected: Boolean(status.connected) })" in ensure_connection
    assert "fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/connect`" in ensure_connection


def test_iq_flow_audit_uses_sanitized_development_logs() -> None:
    source = MARKET_CHART.read_text()

    assert "logIqFlow('assets_request_started'" in source
    assert "logIqFlow('assets_request_finished'" in source
    assert "bootstrap_request_finished" in source
    assert "logIqFlow('chart_props'" in source
    assert "console.info('[IQ_FLOW]', event, metadata)" in source
    assert "if (!import.meta.env.DEV) return" in source


def test_iq_flow_parses_real_api_contracts() -> None:
    source = MARKET_CHART.read_text()

    assert "export function parseIqAssetsResponse" in source
    assert "Array.isArray(record?.assets)" in source
    assert "Array.isArray(nestedData?.assets)" in source
    assert "export function parseIqCandlesResponse" in source
    assert "Array.isArray(chart?.candles)" in source
    assert "Number(chart?.count ?? rawCandles.length)" in source


def test_iq_flow_does_not_abort_shared_connection_promise_or_clear_symbol_on_asset_failure() -> None:
    source = MARKET_CHART.read_text()
    ensure_connection = source.split("async function ensureIqOptionConnected", 1)[1].split("export function parseIqAssetsResponse", 1)[0]
    assets_effect = source.split("async function loadIqAssets", 1)[1].split("useEffect(() => {", 1)[0]

    assert "signal" not in ensure_connection.split("promiseRef.current = (async () =>", 1)[0]
    assert "fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/status`" in ensure_connection
    assert "fallbackIqSymbolAfterAssetsFailure(current, iqMarketType)" in assets_effect
    assert "return marketType === 'OTC' ? 'EURUSD-OTC' : 'EURUSD'" in source
    assert "if (fallbackSymbol)" in source
    assert "setIqError(null)" in source
    assert "setIqSymbol('')" not in assets_effect
    assert "setIqAssets([]);" not in assets_effect


def test_iq_flow_renders_fallback_symbol_option_when_assets_are_unavailable() -> None:
    source = MARKET_CHART.read_text()

    assert "iqSymbol && !iqAssets.some((asset) => asset.symbol === iqSymbol)" in source
    assert "<option value={iqSymbol}>{formatIqSymbol(iqSymbol)}</option>" in source


def test_iq_option_symbol_formatter_only_slashes_currency_pairs() -> None:
    source = MARKET_CHART.read_text()

    assert "function isCurrencyPairSymbol" in source
    assert "currencyCodes.has(symbol.slice(0, 3)) && currencyCodes.has(symbol.slice(3))" in source
    assert "base.length === 6" not in source
    assert "AMA/ZON" not in source


def test_iq_option_feed_counter_uses_local_clock_and_staleness() -> None:
    source = MARKET_CHART.read_text()

    assert "const [nowTick, setNowTick] = useState(() => Date.now())" in source
    assert "window.setInterval(() => setNowTick(Date.now()), 1000)" in source
    assert "type IqFeedStatus = 'LIVE' | 'QUIET' | 'STALE' | 'NO_DATA'" in source
    assert "function getIqFeedState" in source
    assert "const staleAfterSeconds = rawSize * 3" in source
    assert "return { status: 'STALE'" in source
    assert "formatFeedStatus(feedState, iqLastUpdateAt, iqLoading)" in source
    assert "Dados atrasados" in source


def test_iq_flow_sets_market_fallback_symbol_immediately() -> None:
    source = MARKET_CHART.read_text()

    assert "fallbackIqSymbolAfterAssetsFailure('', readStoredMarketType())" in source
    assert "const nextMarketType = event.target.value as IQMarketType" in source
    assert "setIqSymbol(fallbackIqSymbolAfterAssetsFailure('', nextMarketType))" in source


def test_iq_flow_has_bounded_frontend_timeouts() -> None:
    source = MARKET_CHART.read_text()

    assert "const IQ_STATUS_TIMEOUT_MS = 3000" in source
    assert "const IQ_CONNECT_TIMEOUT_MS = 8000" in source
    assert "const IQ_ASSETS_TIMEOUT_MS = 8000" in source
    assert "const IQ_CANDLES_TIMEOUT_MS = 10000" in source
    assert "throw new IqHttpError(408" in source


def test_iq_option_empty_state_does_not_reference_browser_bridge() -> None:
    source = MARKET_CHART.read_text()
    iq_empty = source.split("function IqEmptyChart", 1)[1].split("async function ensureIqOptionConnected", 1)[0]

    assert "Browser Bridge" not in iq_empty
    assert "abrir Polarium" not in iq_empty.lower()
    assert "Conectando à fonte IQ Option" in iq_empty
    assert "Carregando ativos OTC" in iq_empty


def test_polarium_navigation_is_hidden_while_iq_option_is_primary() -> None:
    sidebar = SIDEBAR.read_text()
    navigation = APP_NAVIGATION.read_text()

    assert "Polarium Lab" not in sidebar
    assert "Connections" not in sidebar
    assert "PlugZap" not in sidebar
    assert "FlaskConical" not in sidebar
    assert "pathname === '/connections/polarium' || pathname === '/labs/polarium'" in navigation


def test_main_layout_does_not_poll_polarium_status() -> None:
    source = MAIN_LAYOUT.read_text()

    assert "usePolariumAccount" not in source
    assert "polarium.data" not in source


def test_backend_defaults_disable_polarium_provider_flag() -> None:
    source = BACKEND_CONFIG.read_text()

    assert "iq_option_provider_enabled: bool = True" in source
    assert "polarium_provider_enabled: bool = False" in source
