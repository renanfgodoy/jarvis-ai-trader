(() => {
  const PAGE_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_PAGE';
  const EXTENSION_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_CONTENT';
  const status = {
    bridge_active: true,
    relay_active: true,
    received_count: 0,
    accepted_count: 0,
    rejected_count: 0,
    last_event_name: null,
    last_error_code: null
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
      chrome.runtime.sendMessage({ source: EXTENSION_EVENT_SOURCE, type: 'FORWARD_MARKET_EVENT', payload }, (response) => {
        if (chrome.runtime.lastError) {
          const errorMessage = String(chrome.runtime.lastError.message || '');
          if (errorMessage.includes('Extension context invalidated')) {
            markExtensionContextInvalidated();
            return;
          }
          status.rejected_count += 1;
          status.last_error_code = 'FORWARD_FAILED';
          return;
        }
        if (!response || response.ok !== true) {
          status.rejected_count += 1;
          status.last_error_code = response?.error || 'FORWARD_FAILED';
          return;
        }
        status.accepted_count += 1;
        status.last_error_code = null;
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
