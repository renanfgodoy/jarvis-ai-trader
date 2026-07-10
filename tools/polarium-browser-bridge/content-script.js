(() => {
  const JARVIS_ENDPOINT = 'http://127.0.0.1:8000/api/v1/polarium/live/bridge-message';
  const RELEVANT_EVENTS = new Set([
    'marginal-balance',
    'balances',
    'subscription-balance-changed',
    'candle-generated',
    'digital-option-client-price-generated'
  ]);

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

    const name = value.name || value.event || value.type;
    if (name && RELEVANT_EVENTS.has(String(name))) return value;

    // Some WS protocols wrap the payload inside msg/body/data.
    for (const key of ['msg', 'body', 'data', 'payload']) {
      if (value[key]) {
        const candidate = normalizePayload(value[key]);
        if (candidate) return candidate;
      }
    }
    return null;
  }

  async function forwardToJarvis(payload) {
    try {
      await fetch(JARVIS_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payload,
          force_demo: true,
          source: 'POLARIUM_BROWSER_BRIDGE'
        })
      });
    } catch (error) {
      // Silent by design: if J.A.R.V.I.S backend is offline, Polarium must keep working.
    }
  }

  const NativeWebSocket = window.WebSocket;
  if (!NativeWebSocket || NativeWebSocket.__jarvisPatched) return;

  function JarvisWebSocket(url, protocols) {
    const socket = protocols ? new NativeWebSocket(url, protocols) : new NativeWebSocket(url);

    socket.addEventListener('message', (event) => {
      const parsed = parseJsonCandidate(event.data);
      const payload = normalizePayload(parsed);
      if (payload) forwardToJarvis(payload);
    });

    return socket;
  }

  JarvisWebSocket.prototype = NativeWebSocket.prototype;
  JarvisWebSocket.CONNECTING = NativeWebSocket.CONNECTING;
  JarvisWebSocket.OPEN = NativeWebSocket.OPEN;
  JarvisWebSocket.CLOSING = NativeWebSocket.CLOSING;
  JarvisWebSocket.CLOSED = NativeWebSocket.CLOSED;
  JarvisWebSocket.__jarvisPatched = true;

  Object.defineProperty(window, 'WebSocket', {
    configurable: true,
    writable: true,
    value: JarvisWebSocket
  });

  window.postMessage({ source: 'JARVIS_POLARIUM_BRIDGE', status: 'INSTALLED' }, '*');
})();
