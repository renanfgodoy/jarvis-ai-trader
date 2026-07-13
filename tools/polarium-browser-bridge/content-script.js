(() => {
  const PAGE_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_PAGE';
  const EXTENSION_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_CONTENT';
  const status = {
    bridge_active: true,
    relay_active: true,
    relay_ready_at: Date.now(),
    received_count: 0,
    accepted_count: 0,
    rejected_count: 0,
    last_event_name: null,
    last_error_code: null,
    historical_diagnostic: {
      first_candles_seen_main: 0,
      first_candles_relayed: 0,
      first_candles_received_backend: 0,
      first_candles_adapter_accepted: 0,
      first_candles_parsed: 0,
      first_candles_stored: 0,
      first_candles_collection_count: 0,
      first_candles_last_error_code: null,
      event_name: null,
      direction: null,
      top_level_type: null,
      top_level_keys: [],
      msg_type: null,
      msg_keys: [],
      body_type: null,
      body_keys: [],
      candidate_collection_path: null,
      candidate_collection_length: null,
      received_at: null,
      relay_ready_at: null,
      websocket_created_at: null
    }
  };

  function isBridgeMessage(event) {
    return event.source === window && event.data && event.data.source === PAGE_EVENT_SOURCE && event.data.type === 'MARKET_EVENT';
  }

  function runtimeMessagingAvailable() {
    return (
      typeof chrome !== 'undefined' &&
      chrome.runtime &&
      chrome.runtime.id &&
      typeof chrome.runtime.sendMessage === 'function'
    );
  }

  function markExtensionContextInvalidated() {
    status.rejected_count += 1;
    status.relay_active = false;
    status.last_error_code = 'EXTENSION_CONTEXT_INVALIDATED';
    status.historical_diagnostic.first_candles_last_error_code = 'EXTENSION_CONTEXT_INVALIDATED';
  }

  function isFirstCandlesPayload(payload) {
    return payload && typeof payload === 'object' && payload.event_name === 'first-candles';
  }

  function mergeHistoricalDiagnostic(payload) {
    if (!isFirstCandlesPayload(payload)) return payload;
    const diagnostic = payload.diagnostic && typeof payload.diagnostic === 'object' ? payload.diagnostic : {};
    const mergedDiagnostic = {
      ...diagnostic,
      relay_ready_at: status.relay_ready_at
    };
    status.historical_diagnostic = {
      ...status.historical_diagnostic,
      ...mergedDiagnostic,
      first_candles_seen_main: 1,
      first_candles_collection_count: mergedDiagnostic.candidate_collection_length || 0,
      first_candles_relayed: status.historical_diagnostic.first_candles_relayed,
      first_candles_last_error_code: null
    };
    return { ...payload, diagnostic: mergedDiagnostic };
  }

  function forwardToBackground(payload) {
    if (!status.relay_active) {
      status.rejected_count += 1;
      status.last_error_code = 'EXTENSION_CONTEXT_INVALIDATED';
      return;
    }
    if (!runtimeMessagingAvailable()) {
      markExtensionContextInvalidated();
      return;
    }

    try {
      const relayPayload = mergeHistoricalDiagnostic(payload);
      if (isFirstCandlesPayload(relayPayload)) {
        status.historical_diagnostic.first_candles_relayed += 1;
      }
      chrome.runtime.sendMessage({ source: EXTENSION_EVENT_SOURCE, type: 'FORWARD_MARKET_EVENT', payload: relayPayload }, (response) => {
        if (chrome.runtime.lastError) {
          const errorMessage = String(chrome.runtime.lastError.message || '');
          if (errorMessage.includes('Extension context invalidated')) {
            markExtensionContextInvalidated();
            return;
          }
          status.rejected_count += 1;
          status.last_error_code = 'FORWARD_FAILED';
          if (isFirstCandlesPayload(relayPayload)) {
            status.historical_diagnostic.first_candles_last_error_code = 'FORWARD_FAILED';
          }
          return;
        }
        if (!response || response.ok !== true) {
          status.rejected_count += 1;
          status.last_error_code = response?.error || 'FORWARD_FAILED';
          if (isFirstCandlesPayload(relayPayload)) {
            status.historical_diagnostic.first_candles_last_error_code = status.last_error_code;
          }
          return;
        }
        status.accepted_count += 1;
        status.last_error_code = null;
        if (isFirstCandlesPayload(relayPayload)) {
          status.historical_diagnostic.first_candles_last_error_code = null;
        }
      });
    } catch (error) {
      const errorMessage = String(error && error.message ? error.message : error);
      if (errorMessage.includes('Extension context invalidated')) {
        markExtensionContextInvalidated();
        return;
      }
      status.rejected_count += 1;
      status.last_error_code = 'FORWARD_FAILED';
    }
  }

  window.addEventListener('message', (event) => {
    if (!isBridgeMessage(event)) return;
    status.received_count += 1;
    const payload = event.data.payload;
    if (!payload || typeof payload !== 'object') {
      status.rejected_count += 1;
      status.last_error_code = 'INVALID_PAGE_MESSAGE';
      return;
    }

    status.last_event_name = payload.event_name || null;
    forwardToBackground(payload);
  });

  window.__FRIDAY_TRADE_POLARIUM_BRIDGE_CONTENT__ = {
    status() {
      return { ...status };
    }
  };
})();
