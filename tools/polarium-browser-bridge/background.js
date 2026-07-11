const JARVIS_ENDPOINT = 'http://127.0.0.1:8000/api/v1/polarium/browser-bridge/message';
const CONTENT_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_CONTENT';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || message.source !== CONTENT_EVENT_SOURCE || message.type !== 'FORWARD_MARKET_EVENT') {
    return false;
  }

  fetch(JARVIS_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Friday-Trade-Bridge': 'POLARIUM_AUTHORIZED_BROWSER'
    },
    body: JSON.stringify(message.payload)
  })
    .then((response) => sendResponse({ ok: response.ok, status: response.status }))
    .catch(() => sendResponse({ ok: false, error: 'FORWARD_FAILED' }));

  return true;
});
