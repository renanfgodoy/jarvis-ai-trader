(() => {
  const PAGE_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_PAGE';
  const ALLOWED_EVENTS = new Set([
    'first-candles',
    'candle-generated',
    'candles-generated',
    'timeSync'
  ]);
  const SENSITIVE_MARKERS = [
    'token',
    'access_token',
    'refresh_token',
    'authorization',
    'bearer',
    'cookie',
    'set-cookie',
    'ssid',
    'password',
    'credential',
    'headers',
    'har'
  ];
  const BLOCKED_EVENTS = new Set([
    'authenticate',
    'authenticated',
    'marginal-balance',
    'balances',
    'subscription-balance-changed',
    'portfolio',
    'portfolio.get-history-positions',
    'orders',
    'positions',
    'order',
    'position',
    'execution',
    'result'
  ]);

  if (window.__FRIDAY_TRADE_POLARIUM_BRIDGE_MAIN_INSTALLED__) return;
  window.__FRIDAY_TRADE_POLARIUM_BRIDGE_MAIN_INSTALLED__ = true;

  const status = {
    bridge_active: true,
    main_world: true,
    received_count: 0,
    accepted_count: 0,
    rejected_count: 0,
    last_event_name: null,
    last_error_code: null
  };

  function parseJsonCandidate(data) {
    if (typeof data !== 'string') return null;
    const trimmed = data.trim();
    if (!trimmed) return null;

    const attempts = [trimmed];
    const firstBrace = trimmed.indexOf('{');
    const lastBrace = trimmed.lastIndexOf('}');
    if (firstBrace >= 0 && lastBrace > firstBrace) {
      attempts.push(trimmed.slice(firstBrace, lastBrace + 1));
    }

    for (const item of attempts) {
      try {
        return JSON.parse(item);
      } catch (_) {
        // keep trying
      }
    }
    return null;
  }

  function eventName(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
    if (typeof value.name === 'string') return value.name;
    if (typeof value.event === 'string') return value.event;
    if (typeof value.type === 'string') return value.type;
    if (value.msg && typeof value.msg === 'object' && typeof value.msg.name === 'string') return value.msg.name;
    return null;
  }

  function containsSensitiveMarker(value) {
    if (Array.isArray(value)) return value.some(containsSensitiveMarker);
    if (value && typeof value === 'object') {
      return Object.entries(value).some(([key, child]) => {
        const lowered = String(key).toLowerCase();
        return SENSITIVE_MARKERS.some((marker) => lowered.includes(marker)) || containsSensitiveMarker(child);
      });
    }
    if (typeof value === 'string') {
      return value.toLowerCase().includes('bearer ');
    }
    return false;
  }

  function sanitizeAllowedPayload(value, depth = 0) {
    if (depth > 8) return null;
    if (Array.isArray(value)) return value.slice(0, 200).map((item) => sanitizeAllowedPayload(item, depth + 1)).filter((item) => item !== null);
    if (!value || typeof value !== 'object') return value;
    const output = {};
    for (const [key, child] of Object.entries(value)) {
      const lowered = String(key).toLowerCase();
      if (SENSITIVE_MARKERS.some((marker) => lowered.includes(marker))) continue;
      const sanitized = sanitizeAllowedPayload(child, depth + 1);
      if (sanitized !== null) output[key] = sanitized;
    }
    return output;
  }

  function normalizePayload(value) {
    if (!value) return null;
    if (Array.isArray(value)) {
      for (const item of value) {
        const candidate = normalizePayload(item);
        if (candidate) return candidate;
      }
      return null;
    }
    if (typeof value !== 'object') return null;

    const name = eventName(value);
    if (name) {
      if (BLOCKED_EVENTS.has(String(name)) || !ALLOWED_EVENTS.has(String(name)) || containsSensitiveMarker(value)) return null;
      return {
        event_name: String(name),
        source: 'POLARIUM_AUTHORIZED_BROWSER',
        payload: sanitizeAllowedPayload(value)
      };
    }

    for (const key of ['msg', 'body', 'data']) {
      if (value[key]) {
        const candidate = normalizePayload(value[key]);
        if (candidate) return candidate;
      }
    }
    return null;
  }

  function publishMarketEvent(payload) {
    window.postMessage({ source: PAGE_EVENT_SOURCE, type: 'MARKET_EVENT', payload }, window.location.origin);
  }

  const NativeWebSocket = window.WebSocket;
  if (!NativeWebSocket || NativeWebSocket.__fridayTradeBridgePatched) return;

  function FridayTradeWebSocket(url, protocols) {
    const socket = protocols ? new NativeWebSocket(url, protocols) : new NativeWebSocket(url);

    socket.addEventListener('message', (event) => {
      status.received_count += 1;
      const parsed = parseJsonCandidate(event.data);
      const payload = normalizePayload(parsed);
      if (payload) {
        status.last_event_name = payload.event_name;
        status.accepted_count += 1;
        status.last_error_code = null;
        publishMarketEvent(payload);
      } else {
        status.rejected_count += 1;
      }
    });

    const originalSend = socket.send.bind(socket);
    socket.send = (data) => {
      const parsed = parseJsonCandidate(data);
      const name = eventName(parsed);
      if (name === 'subscribeMessage' || name === 'get-first-candles') {
        status.last_event_name = name;
      }
      return originalSend(data);
    };

    return socket;
  }

  FridayTradeWebSocket.prototype = NativeWebSocket.prototype;
  FridayTradeWebSocket.CONNECTING = NativeWebSocket.CONNECTING;
  FridayTradeWebSocket.OPEN = NativeWebSocket.OPEN;
  FridayTradeWebSocket.CLOSING = NativeWebSocket.CLOSING;
  FridayTradeWebSocket.CLOSED = NativeWebSocket.CLOSED;
  FridayTradeWebSocket.__fridayTradeBridgePatched = true;
  FridayTradeWebSocket.__originalWebSocket = NativeWebSocket;

  Object.defineProperty(window, 'WebSocket', {
    configurable: true,
    writable: true,
    value: FridayTradeWebSocket
  });

  window.__FRIDAY_TRADE_POLARIUM_BRIDGE__ = {
    status() {
      return { ...status };
    }
  };

  window.postMessage({ source: PAGE_EVENT_SOURCE, type: 'INSTALLED' }, window.location.origin);
})();
