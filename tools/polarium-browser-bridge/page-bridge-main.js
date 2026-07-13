(() => {
  const PAGE_EVENT_SOURCE = 'FRIDAY_TRADE_POLARIUM_BRIDGE_PAGE';
  const ALLOWED_EVENTS = new Set([
    'candles',
    'candles-generated',
    'get-first-candles',
    'first-candles',
    'candle-generated',
    'sendMessage',
    'subscribeMessage',
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
  const MARKET_VALUE_KEYS = new Set(['open', 'close', 'min', 'max', 'high', 'low', 'o', 'c', 'h', 'l']);
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
  const DISCOVERY_EVENTS = new Set([
    'candles',
    'candles-generated',
    'get-first-candles',
    'first-candles',
    'sendMessage',
    'subscribeMessage'
  ]);
  const RUNTIME_SCAN_KEYWORDS = [
    'chart',
    'charts',
    'candle',
    'candles',
    'bar',
    'bars',
    'history',
    'series',
    'datafeed',
    'market',
    'price',
    'ohlc',
    'active',
    'asset',
    'store',
    'cache',
    'redux',
    'mobx',
    'zustand',
    'tradingview',
    'lightweight',
    'quadcode'
  ];
  const RUNTIME_SCAN_LIMITS = {
    depth: 5,
    objects: 350,
    candidates: 12,
    nodes: 120,
    milliseconds: 180
  };

  if (window.__FRIDAY_TRADE_POLARIUM_BRIDGE_MAIN_INSTALLED__) return;
  window.__FRIDAY_TRADE_POLARIUM_BRIDGE_MAIN_INSTALLED__ = true;

  const status = {
    bridge_active: true,
    main_world: true,
    page_bridge_installed_at: Date.now(),
    websocket_created_at: null,
    websocket_opened_at: null,
    received_count: 0,
    accepted_count: 0,
    rejected_count: 0,
    last_event_name: null,
    last_error_code: null,
    current_symbol: null,
    symbol_found: false,
    symbol_source: null,
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
    },
    historical_series_discovery: {
      candidate_events_seen: 0,
      candidate_requests_seen: 0,
      candidate_responses_seen: 0,
      last_request_event_name: null,
      last_response_event_name: null,
      last_collection_path: null,
      last_collection_length: null,
      last_distinct_timestamps: 0,
      last_distinct_raw_sizes: 0,
      last_distinct_active_ids: 0,
      historical_series_confirmed: false,
      historical_series_event_name: null,
      historical_series_request_ref: null,
      last_error_code: null
    },
    outbound_candle_request_diagnostic: {
      seen_main: 0,
      relayed: 0,
      event_name: null,
      inner_event_name: null,
      direction: null,
      top_level_type: null,
      top_level_keys: [],
      msg_type: null,
      msg_keys: [],
      body_type: null,
      body_keys: [],
      has_active_id: false,
      has_size: false,
      has_count: false,
      has_from: false,
      has_to: false,
      has_limit: false,
      has_offset: false,
      has_chunk_size: false,
      numeric_field_names: [],
      string_field_names: [],
      array_paths: [],
      object_paths: [],
      request_ref: null,
      correlation_status: null,
      correlated_response_event_name: null,
      correlated_response_collection_path: null,
      correlated_response_collection_length: null,
      correlated_response_distinct_timestamps: 0,
      received_at: null,
      last_error_code: null
    },
    outbound_request_shapes: [],
    historical_transport_discovery: {
      fetch_requests_seen: 0,
      fetch_responses_seen: 0,
      xhr_requests_seen: 0,
      xhr_responses_seen: 0,
      websocket_candidates_seen: 0,
      last_transport: null,
      last_method: null,
      last_url_host: null,
      last_url_path_sanitized: null,
      last_status_code: null,
      last_content_type: null,
      candidate_collection_path: null,
      candidate_collection_type: null,
      candidate_collection_length: null,
      distinct_timestamps: 0,
      distinct_raw_sizes: 0,
      distinct_active_ids: 0,
      historical_candidate_found: false,
      historical_quality: null,
      historical_transport: null,
      historical_request_ref: null,
      page_bridge_installed_at: null,
      fetch_interceptor_installed_at: null,
      xhr_interceptor_installed_at: null,
      websocket_created_at: null,
      first_historical_candidate_at: null,
      last_error_code: null
    },
    historical_transport_shapes: [],
    runtime_store_discovery: {
      scan_started_at: null,
      scan_completed_at: null,
      scan_duration_ms: null,
      window_globals_scanned: 0,
      react_nodes_scanned: 0,
      redux_candidates: 0,
      mobx_candidates: 0,
      zustand_candidates: 0,
      chart_engine_candidates: 0,
      datafeed_candidates: 0,
      storage_candidates: 0,
      worker_candidates: 0,
      candidate_found: false,
      candidate_type: null,
      candidate_ref: null,
      candidate_path: null,
      candidate_collection_type: null,
      candidate_collection_length: null,
      candidate_distinct_timestamps: 0,
      candidate_distinct_raw_sizes: 0,
      candidate_distinct_active_ids: 0,
      candidate_quality: null,
      candidate_readable_passively: false,
      last_error_code: null
    },
    runtime_store_candidates: [],
    candles_generated_diagnostic: {
      seen_main: 0,
      relayed: 0,
      received_backend: 0,
      top_level_type: null,
      top_level_keys: [],
      msg_type: null,
      msg_keys: [],
      body_type: null,
      body_keys: [],
      nested_array_paths: [],
      nested_object_paths: [],
      candidate_collection_path: null,
      candidate_collection_type: null,
      candidate_collection_length: null,
      distinct_timestamps: 0,
      distinct_raw_sizes: 0,
      distinct_active_ids: 0,
      request_ref: null,
      direction: null,
      received_at: null,
      last_error_code: null,
      historical_series_confirmed: false
    }
  };
  const requestRefs = new Map();
  let requestRefCounter = 0;
  const requestShapes = new Map();
  const transportShapes = new Map();
  const runtimeStoreCandidates = new Map();
  const fetchInterceptorInstalledAt = Date.now();
  const xhrInterceptorInstalledAt = Date.now();

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

  function parseTransportBody(text) {
    if (typeof text !== 'string') return null;
    const trimmed = text.trim();
    if (!trimmed || trimmed.length > 1000000) return null;
    try {
      return JSON.parse(trimmed);
    } catch (_) {
      return parseJsonCandidate(trimmed);
    }
  }

  function eventName(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
    if (typeof value.name === 'string') return value.name;
    if (typeof value.event === 'string') return value.event;
    if (typeof value.type === 'string') return value.type;
    if (value.msg && typeof value.msg === 'object' && typeof value.msg.name === 'string') return value.msg.name;
    return null;
  }

  function requestRef(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value) || value.request_id === undefined || value.request_id === null) return null;
    const key = String(value.request_id);
    if (!requestRefs.has(key)) {
      requestRefCounter += 1;
      requestRefs.set(key, `request-${requestRefCounter}`);
    }
    return requestRefs.get(key);
  }

  function containsSensitiveMarker(value) {
    if (Array.isArray(value)) return value.some(containsSensitiveMarker);
    if (value && typeof value === 'object') {
      return Object.entries(value).some(([key, child]) => {
        const lowered = String(key).toLowerCase();
        return hasSensitiveMarkerText(lowered) || containsSensitiveMarker(child);
      });
    }
    if (typeof value === 'string') {
      return value.toLowerCase().includes('bearer ');
    }
    return false;
  }

  function hasSensitiveMarkerText(text) {
    if (String(text).toLowerCase().includes('bearer ')) return true;
    const lowered = String(text).toLowerCase();
    return SENSITIVE_MARKERS.some((marker) => {
      if (marker === 'har') {
        return lowered.split(/[^a-z0-9]+/).filter(Boolean).includes('har');
      }
      return lowered.includes(marker);
    });
  }

  function sanitizeAllowedPayload(value, depth = 0) {
    if (depth > 8) return null;
    if (Array.isArray(value)) return value.slice(-200).map((item) => sanitizeAllowedPayload(item, depth + 1)).filter((item) => item !== null);
    if (!value || typeof value !== 'object') return value;
    const output = {};
    for (const [key, child] of Object.entries(value)) {
      const lowered = String(key).toLowerCase();
      if (lowered === 'request_id' || hasSensitiveMarkerText(lowered)) continue;
      const sanitized = sanitizeAllowedPayload(child, depth + 1);
      if (sanitized !== null) output[key] = sanitized;
    }
    return output;
  }

  function valueType(value) {
    if (Array.isArray(value)) return 'array';
    if (value === null) return 'null';
    return typeof value;
  }

  function safeKeys(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return [];
    return Object.keys(value)
      .filter((key) => {
        const lowered = String(key).toLowerCase();
        return !MARKET_VALUE_KEYS.has(lowered) && !hasSensitiveMarkerText(lowered);
      })
      .slice(0, 80);
  }

  function sanitizeObservedSymbol(value) {
    if (typeof value !== 'string') return null;
    const text = value.replace(/\s+/g, ' ').trim();
    if (text.length < 2 || text.length > 40) return null;
    const lowered = text.toLowerCase();
    if (hasSensitiveMarkerText(lowered)) return null;
    if (!/[a-z]/i.test(text)) return null;
    if (!/^[A-Za-z0-9/._ -]+$/.test(text)) return null;
    if (!(/[A-Z]{2,6}\s*\/\s*[A-Z]{2,6}/i.test(text) || /[A-Z]{3,12}\s+OTC/i.test(text) || /[A-Z]{6,12}\s*OTC/i.test(text))) {
      return null;
    }
    return text;
  }

  function findSymbolInObject(value, depth = 0) {
    if (depth > 4 || !value || typeof value !== 'object') return null;
    const keys = ['symbol', 'asset_symbol', 'assetSymbol', 'active_name', 'activeName', 'asset_name', 'assetName', 'name_short', 'ticker'];
    for (const key of keys) {
      const symbol = sanitizeObservedSymbol(value[key]);
      if (symbol) return { symbol, source: 'main_world_object' };
    }
    for (const [key, child] of Object.entries(value)) {
      if (hasSensitiveMarkerText(String(key).toLowerCase())) continue;
      if (child && typeof child === 'object') {
        const found = findSymbolInObject(child, depth + 1);
        if (found) return found;
      }
    }
    return null;
  }

  function findSymbolInDom() {
    if (!document || typeof document.querySelectorAll !== 'function') return null;
    const selectors = [
      '[data-testid*="asset" i]',
      '[data-test*="asset" i]',
      '[class*="asset" i]',
      '[class*="active" i]',
      '[class*="instrument" i]',
      '[class*="symbol" i]',
      '[class*="pair" i]'
    ];
    for (const selector of selectors) {
      let nodes = [];
      try {
        nodes = Array.from(document.querySelectorAll(selector)).slice(0, 40);
      } catch (_) {
        nodes = [];
      }
      for (const node of nodes) {
        const symbol = sanitizeObservedSymbol(node && node.textContent ? node.textContent : '');
        if (symbol) return { symbol, source: 'polarium_dom' };
      }
    }
    return null;
  }

  function observedSymbolSnapshot(value) {
    const fromPayload = findSymbolInObject(value);
    const observed = fromPayload || findSymbolInDom();
    if (observed) {
      status.current_symbol = observed.symbol;
      status.symbol_found = true;
      status.symbol_source = observed.source;
      return observed;
    }
    return null;
  }

  function collectionCandidate(value, path = '', depth = 0) {
    if (depth > 8 || !value || typeof value !== 'object') return null;
    if (Array.isArray(value)) {
      for (let index = 0; index < value.length; index += 1) {
        const candidate = collectionCandidate(value[index], `${path}.${index}`, depth + 1);
        if (candidate) return candidate;
      }
      return null;
    }

    if (Array.isArray(value.candles)) {
      return { path: path ? `${path}.candles` : 'candles', length: value.candles.length };
    }
    if (value.candles_by_size && typeof value.candles_by_size === 'object' && !Array.isArray(value.candles_by_size)) {
      return { path: path ? `${path}.candles_by_size` : 'candles_by_size', length: Object.keys(value.candles_by_size).length };
    }

    for (const key of ['msg', 'body', 'data', 'payload', 'params']) {
      if (value[key]) {
        const candidate = collectionCandidate(value[key], path ? `${path}.${key}` : key, depth + 1);
        if (candidate) return candidate;
      }
    }
    return null;
  }

  function collectStructurePaths(value, path = '', depth = 0, output = { arrays: [], objects: [] }) {
    if (depth > 6 || output.arrays.length + output.objects.length >= 80 || !value || typeof value !== 'object') return output;
    if (Array.isArray(value)) {
      if (path) output.arrays.push(path);
      value.slice(0, 20).forEach((item, index) => collectStructurePaths(item, path ? `${path}.${index}` : String(index), depth + 1, output));
      return output;
    }
    if (path) output.objects.push(path);
    for (const [key, child] of Object.entries(value)) {
      const lowered = String(key).toLowerCase();
      if (hasSensitiveMarkerText(lowered)) continue;
      collectStructurePaths(child, path ? `${path}.${key}` : key, depth + 1, output);
    }
    return output;
  }

  function looksLikeCandleShape(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
    return ['from', 'timestamp', 'start_timestamp', 'startTimestamp', 'start', 'at', 'open', 'close', 'min', 'max', 'o', 'c'].some((key) => key in value);
  }

  function structuralCollectionCandidate(value, path = '', depth = 0) {
    if (depth > 6 || !value || typeof value !== 'object') return null;
    if (Array.isArray(value)) {
      const inspected = value.slice(0, 20).filter((item) => item && typeof item === 'object' && !Array.isArray(item));
      const candleLike = inspected.filter(looksLikeCandleShape).length;
      if (inspected.length && candleLike >= Math.max(1, Math.floor(inspected.length / 2))) {
        return { path, type: 'array', length: value.length };
      }
      for (let index = 0; index < value.length && index < 20; index += 1) {
        const candidate = structuralCollectionCandidate(value[index], path ? `${path}.${index}` : String(index), depth + 1);
        if (candidate) return candidate;
      }
      return null;
    }
    const keys = Object.keys(value);
    const numericKeys = keys.filter((key) => /^\d+$/.test(String(key)));
    if (keys.length && numericKeys.length === keys.length && Object.values(value).some((item) => item && typeof item === 'object' && !Array.isArray(item))) {
      return { path, type: 'object_indexed_by_raw_size', length: keys.length };
    }
    const children = Object.values(value).slice(0, 20).filter((item) => item && typeof item === 'object' && !Array.isArray(item));
    const candleLike = children.filter(looksLikeCandleShape).length;
    if (children.length && candleLike >= Math.max(1, Math.floor(children.length / 2))) {
      return { path, type: 'object', length: Object.keys(value).length };
    }
    for (const [key, child] of Object.entries(value)) {
      const lowered = String(key).toLowerCase();
      if (hasSensitiveMarkerText(lowered)) continue;
      const candidate = structuralCollectionCandidate(child, path ? `${path}.${key}` : key, depth + 1);
      if (candidate) return candidate;
    }
    return null;
  }

  function sanitizeUrlParts(input) {
    try {
      const url = new URL(String(input), window.location.href);
      const host = url.hostname.includes('polarium') || url.hostname.includes('quadcode') ? url.hostname : 'external';
      const path = url.pathname
        .split('/')
        .map((part) => (/^\d+$/.test(part) || part.length > 48 ? ':id' : part))
        .join('/');
      return { host, path };
    } catch (_) {
      return { host: null, path: null };
    }
  }

  function uniqueCount(values) {
    return new Set(values.filter((item) => item !== null && item !== undefined)).size;
  }

  function collectCandleMetadata(value, output = { timestamps: [], rawSizes: [], activeIds: [] }, inherited = {}) {
    if (!value || typeof value !== 'object') return output;
    if (Array.isArray(value)) {
      value.forEach((item) => collectCandleMetadata(item, output, inherited));
      return output;
    }
    const active_id = value.active_id ?? value.activeId ?? value.active ?? inherited.active_id;
    const raw_size = value.size ?? value.raw_size ?? value.rawSize ?? inherited.raw_size;
    const timestamp = value.from ?? value.timestamp ?? value.start_timestamp ?? value.startTimestamp;
    if (active_id !== undefined) output.activeIds.push(active_id);
    if (raw_size !== undefined) output.rawSizes.push(raw_size);
    if (timestamp !== undefined) output.timestamps.push(timestamp);

    if (value.candles_by_size && typeof value.candles_by_size === 'object' && !Array.isArray(value.candles_by_size)) {
      for (const [size, candle] of Object.entries(value.candles_by_size)) {
        collectCandleMetadata(candle, output, { active_id, raw_size: size });
      }
    }
    if (Array.isArray(value.candles)) {
      collectCandleMetadata(value.candles, output, { active_id, raw_size });
    } else if (value.candles && typeof value.candles === 'object') {
      for (const [size, candle] of Object.entries(value.candles)) {
        collectCandleMetadata(candle, output, { active_id, raw_size: size });
      }
    }
    for (const key of ['msg', 'body', 'data', 'payload', 'params']) {
      if (value[key]) collectCandleMetadata(value[key], output, { active_id, raw_size });
    }
    return output;
  }

  function fieldPresence(value) {
    const metadata = collectCandleMetadata(value);
    const text = JSON.stringify(value || {});
    return {
      active_id_present: metadata.activeIds.length > 0 || text.includes('"active_id"') || text.includes('"activeId"'),
      size_present: metadata.rawSizes.length > 0 || text.includes('"size"') || text.includes('"raw_size"') || text.includes('"rawSize"'),
      count_present: text.includes('"count"'),
      from_present: metadata.timestamps.length > 0 || text.includes('"from"'),
      to_present: text.includes('"to"')
    };
  }

  function innerEventName(value) {
    const msg = value && typeof value === 'object' && !Array.isArray(value) ? value.msg : null;
    const body = msg && typeof msg === 'object' && !Array.isArray(msg) ? msg.body : null;
    for (const source of [msg, body]) {
      if (!source || typeof source !== 'object' || Array.isArray(source)) continue;
      for (const key of ['name', 'event', 'type', 'command', 'method']) {
        if (typeof source[key] === 'string') return source[key];
      }
    }
    return null;
  }

  function collectFieldTypes(value, output = { numeric: new Set(), string: new Set() }, depth = 0) {
    if (depth > 6 || !value || typeof value !== 'object') return output;
    if (Array.isArray(value)) {
      value.slice(0, 20).forEach((item) => collectFieldTypes(item, output, depth + 1));
      return output;
    }
    for (const [key, child] of Object.entries(value)) {
      const lowered = String(key).toLowerCase();
      if (hasSensitiveMarkerText(lowered)) continue;
      if (['active_id', 'activeId', 'size', 'raw_size', 'rawSize', 'count', 'from', 'to', 'limit', 'offset', 'chunk_size', 'chunkSize'].includes(key)) {
        if (typeof child === 'number') output.numeric.add(key);
        if (typeof child === 'string') output.string.add(key);
      }
      collectFieldTypes(child, output, depth + 1);
    }
    return output;
  }

  function outboundRequestDiagnostic(value, event_name) {
    const msg = value && typeof value === 'object' && !Array.isArray(value) ? value.msg : null;
    const body = msg && typeof msg === 'object' && !Array.isArray(msg) ? msg.body : null;
    const paths = collectStructurePaths(value);
    const presence = fieldPresence(value);
    const fieldTypes = collectFieldTypes(value);
    return {
      seen_main: 1,
      relayed: 0,
      event_name,
      inner_event_name: innerEventName(value),
      direction: 'client_to_server',
      top_level_type: valueType(value),
      top_level_keys: safeKeys(value),
      msg_type: valueType(msg),
      msg_keys: safeKeys(msg),
      body_type: valueType(body),
      body_keys: safeKeys(body),
      has_active_id: presence.active_id_present,
      has_size: presence.size_present,
      has_count: presence.count_present,
      has_from: presence.from_present,
      has_to: presence.to_present,
      has_limit: JSON.stringify(value || {}).includes('"limit"'),
      has_offset: JSON.stringify(value || {}).includes('"offset"'),
      has_chunk_size: JSON.stringify(value || {}).includes('"chunk_size"') || JSON.stringify(value || {}).includes('"chunkSize"'),
      numeric_field_names: Array.from(fieldTypes.numeric).sort(),
      string_field_names: Array.from(fieldTypes.string).sort(),
      array_paths: paths.arrays,
      object_paths: paths.objects,
      request_ref: requestRef(value),
      correlation_status: requestRef(value) ? 'CONFIRMED_BY_REQUEST_ID' : 'TEMPORAL_CANDIDATE',
      received_at: Date.now(),
      last_error_code: null
    };
  }

  function shapeFingerprint(diagnostic) {
    return [
      diagnostic.event_name,
      diagnostic.inner_event_name,
      diagnostic.top_level_keys.join(','),
      diagnostic.msg_keys.join(','),
      diagnostic.body_keys.join(','),
      diagnostic.has_active_id,
      diagnostic.has_size,
      diagnostic.has_count,
      diagnostic.has_from,
      diagnostic.has_to,
      diagnostic.has_limit,
      diagnostic.has_offset
    ].join('|');
  }

  function updateOutboundStatus(diagnostic) {
    status.outbound_candle_request_diagnostic = {
      ...status.outbound_candle_request_diagnostic,
      ...diagnostic,
      seen_main: status.outbound_candle_request_diagnostic.seen_main + 1
    };
    const fingerprint = shapeFingerprint(diagnostic);
    let shape = requestShapes.get(fingerprint);
    if (!shape && requestShapes.size < 8) {
      shape = {
        shape_ref: `request_shape_${requestShapes.size + 1}`,
        occurrences: 0,
        inner_event_name: diagnostic.inner_event_name,
        top_level_keys: diagnostic.top_level_keys,
        msg_keys: diagnostic.msg_keys,
        body_keys: diagnostic.body_keys,
        has_active_id: diagnostic.has_active_id,
        has_size: diagnostic.has_size,
        has_count: diagnostic.has_count,
        has_from: diagnostic.has_from,
        has_to: diagnostic.has_to,
        has_limit: diagnostic.has_limit,
        has_offset: diagnostic.has_offset,
        correlated_response_event_names: []
      };
      requestShapes.set(fingerprint, shape);
    }
    if (shape) {
      shape.occurrences += 1;
      status.outbound_request_shapes = Array.from(requestShapes.values());
    }
  }

  function historicalQuality(count) {
    if (count >= 100) return 'BROAD';
    if (count >= 20) return 'USEFUL';
    if (count >= 2) return 'SHORT';
    return null;
  }

  function transportDiagnostic({ transport, method, url, statusCode = null, contentType = null, parsedBody = null }) {
    const urlParts = sanitizeUrlParts(url || window.location.href);
    const paths = parsedBody ? collectStructurePaths(parsedBody) : { arrays: [], objects: [] };
    const candidate = parsedBody ? structuralCollectionCandidate(parsedBody) : null;
    const metadata = parsedBody ? collectCandleMetadata(parsedBody) : { timestamps: [], rawSizes: [], activeIds: [] };
    const distinct_timestamps = uniqueCount(metadata.timestamps);
    const distinct_raw_sizes = uniqueCount(metadata.rawSizes);
    const distinct_active_ids = uniqueCount(metadata.activeIds);
    const historical_candidate_found = distinct_active_ids === 1 && distinct_raw_sizes === 1 && distinct_timestamps >= 2;
    return {
      fetch_requests_seen: transport === 'fetch_request' ? 1 : 0,
      fetch_responses_seen: transport === 'fetch_response' ? 1 : 0,
      xhr_requests_seen: transport === 'xhr_request' ? 1 : 0,
      xhr_responses_seen: transport === 'xhr_response' ? 1 : 0,
      websocket_candidates_seen: transport === 'websocket' ? 1 : 0,
      last_transport: transport,
      last_method: (method || 'GET').toUpperCase(),
      last_url_host: urlParts.host,
      last_url_path_sanitized: urlParts.path,
      last_status_code: statusCode,
      last_content_type: contentType ? String(contentType).split(';')[0].toLowerCase() : null,
      candidate_collection_path: candidate ? candidate.path : null,
      candidate_collection_type: candidate ? candidate.type : null,
      candidate_collection_length: candidate ? candidate.length : null,
      distinct_timestamps,
      distinct_raw_sizes,
      distinct_active_ids,
      historical_candidate_found,
      historical_quality: historicalQuality(distinct_timestamps),
      historical_transport: historical_candidate_found ? transport : null,
      historical_request_ref: null,
      page_bridge_installed_at: status.page_bridge_installed_at,
      fetch_interceptor_installed_at: fetchInterceptorInstalledAt,
      xhr_interceptor_installed_at: xhrInterceptorInstalledAt,
      websocket_created_at: status.websocket_created_at,
      first_historical_candidate_at: historical_candidate_found ? Date.now() : null,
      last_error_code: null,
      top_level_type: parsedBody ? valueType(parsedBody) : null,
      top_level_keys: parsedBody ? safeKeys(parsedBody) : [],
      nested_array_paths: paths.arrays,
      nested_object_paths: paths.objects
    };
  }

  function transportShapeFingerprint(diagnostic) {
    return [
      diagnostic.last_transport,
      diagnostic.last_method,
      diagnostic.last_url_host,
      diagnostic.last_url_path_sanitized,
      diagnostic.last_content_type,
      diagnostic.candidate_collection_path,
      diagnostic.distinct_timestamps,
      diagnostic.distinct_raw_sizes,
      diagnostic.distinct_active_ids
    ].join('|');
  }

  function updateTransportStatus(diagnostic) {
    status.historical_transport_discovery.fetch_requests_seen += diagnostic.fetch_requests_seen;
    status.historical_transport_discovery.fetch_responses_seen += diagnostic.fetch_responses_seen;
    status.historical_transport_discovery.xhr_requests_seen += diagnostic.xhr_requests_seen;
    status.historical_transport_discovery.xhr_responses_seen += diagnostic.xhr_responses_seen;
    status.historical_transport_discovery.websocket_candidates_seen += diagnostic.websocket_candidates_seen;
    status.historical_transport_discovery.last_transport = diagnostic.last_transport;
    status.historical_transport_discovery.last_method = diagnostic.last_method;
    status.historical_transport_discovery.last_url_host = diagnostic.last_url_host;
    status.historical_transport_discovery.last_url_path_sanitized = diagnostic.last_url_path_sanitized;
    status.historical_transport_discovery.last_status_code = diagnostic.last_status_code;
    status.historical_transport_discovery.last_content_type = diagnostic.last_content_type;
    status.historical_transport_discovery.candidate_collection_path = diagnostic.candidate_collection_path;
    status.historical_transport_discovery.candidate_collection_type = diagnostic.candidate_collection_type;
    status.historical_transport_discovery.candidate_collection_length = diagnostic.candidate_collection_length;
    status.historical_transport_discovery.distinct_timestamps = diagnostic.distinct_timestamps;
    status.historical_transport_discovery.distinct_raw_sizes = diagnostic.distinct_raw_sizes;
    status.historical_transport_discovery.distinct_active_ids = diagnostic.distinct_active_ids;
    status.historical_transport_discovery.page_bridge_installed_at = diagnostic.page_bridge_installed_at;
    status.historical_transport_discovery.fetch_interceptor_installed_at = diagnostic.fetch_interceptor_installed_at;
    status.historical_transport_discovery.xhr_interceptor_installed_at = diagnostic.xhr_interceptor_installed_at;
    status.historical_transport_discovery.websocket_created_at = diagnostic.websocket_created_at;
    status.historical_transport_discovery.last_error_code = diagnostic.last_error_code;
    if (diagnostic.historical_candidate_found) {
      status.historical_transport_discovery.historical_candidate_found = true;
      status.historical_transport_discovery.historical_quality = diagnostic.historical_quality;
      status.historical_transport_discovery.historical_transport = diagnostic.historical_transport;
      status.historical_transport_discovery.first_historical_candidate_at = status.historical_transport_discovery.first_historical_candidate_at || diagnostic.first_historical_candidate_at;
    }
    const fingerprint = transportShapeFingerprint(diagnostic);
    let shape = transportShapes.get(fingerprint);
    if (!shape && transportShapes.size < 8) {
      shape = {
        shape_ref: `transport_shape_${transportShapes.size + 1}`,
        transport: diagnostic.last_transport,
        method: diagnostic.last_method,
        host: diagnostic.last_url_host,
        path_shape: diagnostic.last_url_path_sanitized,
        content_type: diagnostic.last_content_type,
        top_level_type: diagnostic.top_level_type,
        top_level_keys: diagnostic.top_level_keys,
        nested_array_paths: diagnostic.nested_array_paths,
        nested_object_paths: diagnostic.nested_object_paths,
        candidate_collection_path: diagnostic.candidate_collection_path,
        candidate_collection_length: diagnostic.candidate_collection_length,
        distinct_timestamps: diagnostic.distinct_timestamps,
        distinct_raw_sizes: diagnostic.distinct_raw_sizes,
        distinct_active_ids: diagnostic.distinct_active_ids,
        occurrences: 0
      };
      transportShapes.set(fingerprint, shape);
    }
    if (shape) {
      shape.occurrences += 1;
      status.historical_transport_shapes = Array.from(transportShapes.values());
    }
  }

  function publishTransportDiagnostic(diagnostic) {
    updateTransportStatus(diagnostic);
    publishMarketEvent({
      event_name: 'historical-transport-discovery',
      source: 'POLARIUM_AUTHORIZED_BROWSER',
      payload: { name: 'historical-transport-discovery' },
      historical_transport_discovery: diagnostic
    });
  }

  function runtimeSafeName(value) {
    const text = String(value || '').slice(0, 120);
    const lowered = text.toLowerCase();
    if (!text || hasSensitiveMarkerText(lowered)) return null;
    return text.replace(/[^a-zA-Z0-9._\-$[\]]/g, '_');
  }

  function runtimePath(parent, key) {
    const name = runtimeSafeName(key);
    if (!name) return parent || null;
    return parent ? `${parent}.${name}` : name;
  }

  function runtimeCandidateSource(name, value, keys, methods) {
    const text = `${name || ''} ${keys.join(' ')} ${methods.join(' ')}`.toLowerCase();
    if (text.includes('redux') || (methods.includes('getState') && methods.includes('dispatch'))) return 'redux';
    if (text.includes('zustand') || (methods.includes('getState') && methods.includes('subscribe'))) return 'zustand';
    if (text.includes('mobx') || text.includes('observable') || methods.includes('toJS')) return 'mobx';
    if (text.includes('datafeed') || methods.includes('getBars') || methods.includes('subscribeBars')) return 'datafeed';
    if (text.includes('tradingview') || text.includes('lightweight') || methods.includes('setData') || methods.includes('update')) return 'chart_engine';
    if (text.includes('worker')) return 'worker';
    if (value === window.localStorage) return 'localstorage';
    if (value === window.sessionStorage) return 'sessionstorage';
    return 'window_global';
  }

  function runtimeObjectType(value) {
    if (Array.isArray(value)) return 'array';
    if (value instanceof Map) return 'map';
    if (value instanceof Set) return 'set';
    if (value === null) return 'null';
    return typeof value;
  }

  function runtimeTopLevelKeys(value) {
    if (!value || typeof value !== 'object') return [];
    let keys = [];
    try {
      keys = Object.keys(value);
    } catch (_) {
      return [];
    }
    return keys
      .map(runtimeSafeName)
      .filter(Boolean)
      .filter((key) => !MARKET_VALUE_KEYS.has(String(key).toLowerCase()))
      .slice(0, 40);
  }

  function runtimeMethodNames(value, keys) {
    if (!value || typeof value !== 'object') return [];
    return keys
      .filter((key) => {
        try {
          return typeof value[key] === 'function';
        } catch (_) {
          return false;
        }
      })
      .map(runtimeSafeName)
      .filter(Boolean)
      .slice(0, 40);
  }

  function runtimeCollectionType(value) {
    if (Array.isArray(value)) return 'array';
    if (value instanceof Map) return 'map';
    if (value instanceof Set) return 'set';
    if (value && typeof value === 'object') return 'object';
    return 'unknown';
  }

  function runtimeCollectionLength(value) {
    if (Array.isArray(value)) return value.length;
    if (value instanceof Map || value instanceof Set) return value.size;
    if (value && typeof value === 'object') {
      try {
        return Object.keys(value).length;
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  function scanRuntimeShape(root, rootPath, context) {
    const started = performance.now();
    const visited = new WeakSet();
    const arrays = [];
    const objects = [];
    let scannedObjects = 0;
    const metadata = { timestamps: [], rawSizes: [], activeIds: [] };
    let candidateCollection = null;

    function inspect(value, path, depth, inherited = {}) {
      if (performance.now() - started > RUNTIME_SCAN_LIMITS.milliseconds) {
        context.last_error_code = context.last_error_code || 'RUNTIME_SCAN_TIMEOUT';
        return;
      }
      if (scannedObjects >= RUNTIME_SCAN_LIMITS.objects || depth > RUNTIME_SCAN_LIMITS.depth || !value || typeof value !== 'object') return;
      if (visited.has(value)) return;
      visited.add(value);
      scannedObjects += 1;

      if (Array.isArray(value)) {
        if (path) arrays.push(path);
        if (!candidateCollection && value.length >= 2 && value.slice(0, 20).some(looksLikeCandleShape)) {
          candidateCollection = { path, type: 'array', length: value.length };
        }
        value.slice(0, 20).forEach((item, index) => inspect(item, runtimePath(path, index), depth + 1, inherited));
        return;
      }

      if (path) objects.push(path);
      const active_id = value.active_id ?? value.activeId ?? value.active ?? inherited.active_id;
      const raw_size = value.size ?? value.raw_size ?? value.rawSize ?? inherited.raw_size;
      const timestamp = value.from ?? value.timestamp ?? value.start_timestamp ?? value.startTimestamp ?? value.time;
      if (active_id !== undefined) metadata.activeIds.push(active_id);
      if (raw_size !== undefined) metadata.rawSizes.push(raw_size);
      if (timestamp !== undefined) metadata.timestamps.push(timestamp);

      const keys = runtimeTopLevelKeys(value);
      if (!candidateCollection && keys.some((key) => ['candles', 'bars', 'series', 'history', 'data'].includes(String(key).toLowerCase()))) {
        candidateCollection = { path, type: runtimeCollectionType(value), length: runtimeCollectionLength(value) };
      }
      for (const key of keys.slice(0, 40)) {
        const lowered = String(key).toLowerCase();
        if (hasSensitiveMarkerText(lowered)) continue;
        try {
          const child = value[key];
          if (typeof child === 'function') continue;
          inspect(child, runtimePath(path, key), depth + 1, { active_id, raw_size });
        } catch (_) {
          context.last_error_code = context.last_error_code || 'RUNTIME_CANDIDATE_READ_FAILED';
        }
      }
    }

    inspect(root, rootPath, 0);
    return {
      array_paths: arrays.slice(0, 40),
      object_paths: objects.slice(0, 40),
      collection_path: candidateCollection ? candidateCollection.path : null,
      collection_type: candidateCollection ? candidateCollection.type : null,
      collection_length: candidateCollection ? candidateCollection.length : null,
      distinct_timestamps: uniqueCount(metadata.timestamps),
      distinct_raw_sizes: uniqueCount(metadata.rawSizes),
      distinct_active_ids: uniqueCount(metadata.activeIds),
      scanned_objects: scannedObjects
    };
  }

  function runtimeQuality(count) {
    if (count >= 100) return 'BROAD';
    if (count >= 20) return 'USEFUL';
    if (count >= 2) return 'SHORT';
    return null;
  }

  function runtimeCandidateFingerprint(candidate) {
    return [
      candidate.source_type,
      candidate.name_sanitized,
      candidate.path_sanitized,
      candidate.object_type,
      candidate.collection_length,
      candidate.distinct_timestamps,
      candidate.distinct_raw_sizes,
      candidate.distinct_active_ids
    ].join('|');
  }

  function addRuntimeCandidate(candidate) {
    const fingerprint = runtimeCandidateFingerprint(candidate);
    let existing = runtimeStoreCandidates.get(fingerprint);
    if (!existing && runtimeStoreCandidates.size < RUNTIME_SCAN_LIMITS.candidates) {
      existing = { ...candidate, occurrences: 0 };
      runtimeStoreCandidates.set(fingerprint, existing);
    }
    if (existing) {
      existing.occurrences += 1;
      status.runtime_store_candidates = Array.from(runtimeStoreCandidates.values());
    }
  }

  function inspectRuntimeCandidate(name, value, path, discovery, forcedSourceType = null) {
    if (!value || typeof value !== 'object') return null;
    const topLevelKeys = runtimeTopLevelKeys(value);
    const methodNames = runtimeMethodNames(value, topLevelKeys);
    const sourceType = forcedSourceType || runtimeCandidateSource(name, value, topLevelKeys, methodNames);
    const shape = scanRuntimeShape(value, path, discovery);
    const candidateRef = `runtime_candidate_${runtimeStoreCandidates.size + 1}`;
    const candidate = {
      candidate_ref: candidateRef,
      source_type: sourceType,
      name_sanitized: runtimeSafeName(name),
      path_sanitized: path,
      object_type: runtimeObjectType(value),
      top_level_keys: topLevelKeys,
      method_names: methodNames,
      array_paths: shape.array_paths,
      object_paths: shape.object_paths,
      collection_length: shape.collection_length,
      distinct_timestamps: shape.distinct_timestamps,
      distinct_raw_sizes: shape.distinct_raw_sizes,
      distinct_active_ids: shape.distinct_active_ids,
      quality: runtimeQuality(shape.distinct_timestamps),
      readable_passively: true,
      occurrences: 1,
      candidate_collection_type: shape.collection_type,
      candidate_path: shape.collection_path || path
    };
    addRuntimeCandidate(candidate);
    if (sourceType === 'redux') discovery.redux_candidates += 1;
    if (sourceType === 'mobx') discovery.mobx_candidates += 1;
    if (sourceType === 'zustand') discovery.zustand_candidates += 1;
    if (sourceType === 'chart_engine') discovery.chart_engine_candidates += 1;
    if (sourceType === 'datafeed') discovery.datafeed_candidates += 1;
    if (sourceType === 'localstorage' || sourceType === 'sessionstorage' || sourceType === 'indexeddb') discovery.storage_candidates += 1;
    if (sourceType === 'worker') discovery.worker_candidates += 1;
    return candidate;
  }

  function candidateMatchesHistory(candidate) {
    const hasReadableCounts = candidate.distinct_active_ids > 0 || candidate.distinct_raw_sizes > 0 || candidate.distinct_timestamps > 0;
    return (
      candidate.distinct_active_ids === 1 &&
      candidate.distinct_raw_sizes === 1 &&
      candidate.distinct_timestamps >= 2
    ) || (
      !hasReadableCounts &&
      candidate.collection_length >= 2 &&
      candidate.candidate_path &&
      (candidate.array_paths.length > 0 || candidate.object_paths.length > 0)
    );
  }

  function scanReactCandidates(discovery) {
    let nodes = [];
    try {
      nodes = Array.from(document.querySelectorAll('[class], [id], canvas, iframe')).slice(0, RUNTIME_SCAN_LIMITS.nodes);
    } catch (_) {
      return [];
    }
    const candidates = [];
    for (const node of nodes) {
      discovery.react_nodes_scanned += 1;
      const reactKeys = Object.keys(node).filter((key) => key.startsWith('__reactFiber') || key.startsWith('__reactProps') || key.startsWith('__reactContainer')).slice(0, 4);
      for (const key of reactKeys) {
        try {
          const value = node[key];
          const candidate = inspectRuntimeCandidate(key, value, `react.${runtimeSafeName(key)}`, discovery, 'react');
          if (candidate) {
            candidates.push(candidate);
          }
        } catch (_) {
          discovery.last_error_code = discovery.last_error_code || 'RUNTIME_REACT_SCAN_FAILED';
        }
      }
    }
    return candidates;
  }

  function scanStorageCandidates(discovery) {
    for (const [name, storage] of [['localStorage', window.localStorage], ['sessionStorage', window.sessionStorage]]) {
      try {
        const keys = [];
        for (let index = 0; index < Math.min(storage.length, 40); index += 1) {
          const key = runtimeSafeName(storage.key(index));
          if (key) keys.push(key);
        }
        const candidate = {
          candidate_ref: `runtime_candidate_${runtimeStoreCandidates.size + 1}`,
          source_type: name === 'localStorage' ? 'localstorage' : 'sessionstorage',
          name_sanitized: name,
          path_sanitized: name,
          object_type: 'storage',
          top_level_keys: keys,
          method_names: ['getItem', 'key'],
          array_paths: [],
          object_paths: [],
          collection_length: storage.length,
          distinct_timestamps: 0,
          distinct_raw_sizes: 0,
          distinct_active_ids: 0,
          quality: null,
          readable_passively: true,
          occurrences: 1,
          candidate_collection_type: 'unknown',
          candidate_path: name
        };
        addRuntimeCandidate(candidate);
        discovery.storage_candidates += 1;
      } catch (_) {
        discovery.last_error_code = discovery.last_error_code || 'RUNTIME_STORAGE_SCAN_FAILED';
      }
    }
    if (window.indexedDB) {
      discovery.storage_candidates += 1;
      addRuntimeCandidate({
        candidate_ref: `runtime_candidate_${runtimeStoreCandidates.size + 1}`,
        source_type: 'indexeddb',
        name_sanitized: 'indexedDB',
        path_sanitized: 'indexedDB',
        object_type: 'object',
        top_level_keys: ['databases'],
        method_names: ['open'],
        array_paths: [],
        object_paths: [],
        collection_length: null,
        distinct_timestamps: 0,
        distinct_raw_sizes: 0,
        distinct_active_ids: 0,
        quality: null,
        readable_passively: false,
        occurrences: 1,
        candidate_collection_type: 'unknown',
        candidate_path: 'indexedDB'
      });
    }
  }

  function scanRuntimeStores() {
    const scanStarted = Date.now();
    runtimeStoreCandidates.clear();
    status.runtime_store_candidates = [];
    const discovery = {
      scan_started_at: scanStarted,
      scan_completed_at: null,
      scan_duration_ms: null,
      window_globals_scanned: 0,
      react_nodes_scanned: 0,
      redux_candidates: 0,
      mobx_candidates: 0,
      zustand_candidates: 0,
      chart_engine_candidates: 0,
      datafeed_candidates: 0,
      storage_candidates: 0,
      worker_candidates: 0,
      candidate_found: false,
      candidate_type: null,
      candidate_ref: null,
      candidate_path: null,
      candidate_collection_type: null,
      candidate_collection_length: null,
      candidate_distinct_timestamps: 0,
      candidate_distinct_raw_sizes: 0,
      candidate_distinct_active_ids: 0,
      candidate_quality: null,
      candidate_readable_passively: false,
      last_error_code: null
    };

    const candidates = [];
    try {
      const names = Object.getOwnPropertyNames(window)
        .filter((name) => RUNTIME_SCAN_KEYWORDS.some((keyword) => name.toLowerCase().includes(keyword)))
        .slice(0, RUNTIME_SCAN_LIMITS.objects);
      for (const name of names) {
        discovery.window_globals_scanned += 1;
        try {
          const value = window[name];
          const candidate = inspectRuntimeCandidate(name, value, `window.${runtimeSafeName(name)}`, discovery);
          if (candidate) candidates.push(candidate);
        } catch (_) {
          discovery.last_error_code = discovery.last_error_code || 'RUNTIME_WINDOW_GLOBAL_READ_FAILED';
        }
      }
      candidates.push(...scanReactCandidates(discovery));
      scanStorageCandidates(discovery);
      if (typeof Worker !== 'undefined') discovery.worker_candidates += 1;
      if (typeof SharedWorker !== 'undefined') discovery.worker_candidates += 1;
    } catch (_) {
      discovery.last_error_code = discovery.last_error_code || 'RUNTIME_SCAN_FAILED';
    }

    const best = Array.from(runtimeStoreCandidates.values()).find(candidateMatchesHistory);
    if (best) {
      discovery.candidate_found = true;
      discovery.candidate_type = best.source_type;
      discovery.candidate_ref = best.candidate_ref;
      discovery.candidate_path = best.candidate_path || best.path_sanitized;
      discovery.candidate_collection_type = best.candidate_collection_type || 'unknown';
      discovery.candidate_collection_length = best.collection_length;
      discovery.candidate_distinct_timestamps = best.distinct_timestamps;
      discovery.candidate_distinct_raw_sizes = best.distinct_raw_sizes;
      discovery.candidate_distinct_active_ids = best.distinct_active_ids;
      discovery.candidate_quality = best.quality;
      discovery.candidate_readable_passively = best.readable_passively;
    }
    discovery.scan_completed_at = Date.now();
    discovery.scan_duration_ms = discovery.scan_completed_at - scanStarted;
    status.runtime_store_discovery = discovery;
    publishMarketEvent({
      event_name: 'runtime-store-discovery',
      source: 'POLARIUM_AUTHORIZED_BROWSER',
      payload: { name: 'runtime-store-discovery' },
      runtime_store_discovery: discovery,
      runtime_store_candidates: status.runtime_store_candidates
    });
    return {
      runtime_store_discovery: { ...status.runtime_store_discovery },
      runtime_store_candidates: status.runtime_store_candidates.slice()
    };
  }

  function discoveryDiagnostic(value, event_name, direction) {
    const msg = value && typeof value === 'object' && !Array.isArray(value) ? value.msg : null;
    const body = msg && typeof msg === 'object' && !Array.isArray(msg) ? msg.body : null;
    const candidate = collectionCandidate(value);
    const metadata = collectCandleMetadata(value);
    const presence = fieldPresence(value);
    const distinct_timestamps = uniqueCount(metadata.timestamps);
    const distinct_raw_sizes = uniqueCount(metadata.rawSizes);
    const distinct_active_ids = uniqueCount(metadata.activeIds);
    const historical_series_confirmed = distinct_active_ids === 1 && distinct_raw_sizes === 1 && distinct_timestamps >= 20;
    return {
      direction,
      event_name,
      request_ref: requestRef(value),
      request_id_present: Boolean(requestRef(value)),
      top_level_keys: safeKeys(value),
      msg_keys: safeKeys(msg),
      body_keys: safeKeys(body),
      active_id_present: presence.active_id_present,
      size_present: presence.size_present,
      count_present: presence.count_present,
      from_present: presence.from_present,
      to_present: presence.to_present,
      collection_path: candidate ? candidate.path : null,
      collection_length: candidate ? candidate.length : null,
      distinct_timestamps,
      distinct_raw_sizes,
      distinct_active_ids,
      historical_series_confirmed
    };
  }

  function candlesGeneratedDiagnostic(value, event_name, direction) {
    const msg = value && typeof value === 'object' && !Array.isArray(value) ? value.msg : null;
    const body = msg && typeof msg === 'object' && !Array.isArray(msg) ? msg.body : null;
    const paths = collectStructurePaths(value);
    const candidate = structuralCollectionCandidate(value);
    const metadata = collectCandleMetadata(value);
    const distinct_timestamps = uniqueCount(metadata.timestamps);
    const distinct_raw_sizes = uniqueCount(metadata.rawSizes);
    const distinct_active_ids = uniqueCount(metadata.activeIds);
    const historical_series_confirmed = distinct_active_ids === 1 && distinct_raw_sizes === 1 && distinct_timestamps >= 20;
    return {
      seen_main: 1,
      relayed: 0,
      received_backend: 0,
      top_level_type: valueType(value),
      top_level_keys: safeKeys(value),
      msg_type: valueType(msg),
      msg_keys: safeKeys(msg),
      body_type: valueType(body),
      body_keys: safeKeys(body),
      nested_array_paths: paths.arrays,
      nested_object_paths: paths.objects,
      candidate_collection_path: candidate ? candidate.path : null,
      candidate_collection_type: candidate ? candidate.type : null,
      candidate_collection_length: candidate ? candidate.length : null,
      distinct_timestamps,
      distinct_raw_sizes,
      distinct_active_ids,
      request_ref: requestRef(value),
      direction,
      received_at: Date.now(),
      last_error_code: null,
      historical_series_confirmed
    };
  }

  function updateCandlesGeneratedStatus(diagnostic) {
    status.candles_generated_diagnostic.seen_main += 1;
    status.candles_generated_diagnostic.top_level_type = diagnostic.top_level_type;
    status.candles_generated_diagnostic.top_level_keys = diagnostic.top_level_keys;
    status.candles_generated_diagnostic.msg_type = diagnostic.msg_type;
    status.candles_generated_diagnostic.msg_keys = diagnostic.msg_keys;
    status.candles_generated_diagnostic.body_type = diagnostic.body_type;
    status.candles_generated_diagnostic.body_keys = diagnostic.body_keys;
    status.candles_generated_diagnostic.nested_array_paths = diagnostic.nested_array_paths;
    status.candles_generated_diagnostic.nested_object_paths = diagnostic.nested_object_paths;
    status.candles_generated_diagnostic.candidate_collection_path = diagnostic.candidate_collection_path;
    status.candles_generated_diagnostic.candidate_collection_type = diagnostic.candidate_collection_type;
    status.candles_generated_diagnostic.candidate_collection_length = diagnostic.candidate_collection_length;
    status.candles_generated_diagnostic.distinct_timestamps = diagnostic.distinct_timestamps;
    status.candles_generated_diagnostic.distinct_raw_sizes = diagnostic.distinct_raw_sizes;
    status.candles_generated_diagnostic.distinct_active_ids = diagnostic.distinct_active_ids;
    status.candles_generated_diagnostic.request_ref = diagnostic.request_ref;
    status.candles_generated_diagnostic.direction = diagnostic.direction;
    status.candles_generated_diagnostic.received_at = diagnostic.received_at;
    status.candles_generated_diagnostic.last_error_code = null;
    status.candles_generated_diagnostic.historical_series_confirmed = diagnostic.historical_series_confirmed;
  }

  function updateDiscoveryStatus(diagnostic) {
    status.historical_series_discovery.candidate_events_seen += 1;
    if (diagnostic.direction === 'client_to_server') {
      status.historical_series_discovery.candidate_requests_seen += 1;
      status.historical_series_discovery.last_request_event_name = diagnostic.event_name;
    } else {
      status.historical_series_discovery.candidate_responses_seen += 1;
      status.historical_series_discovery.last_response_event_name = diagnostic.event_name;
    }
    status.historical_series_discovery.last_collection_path = diagnostic.collection_path;
    status.historical_series_discovery.last_collection_length = diagnostic.collection_length;
    status.historical_series_discovery.last_distinct_timestamps = diagnostic.distinct_timestamps;
    status.historical_series_discovery.last_distinct_raw_sizes = diagnostic.distinct_raw_sizes;
    status.historical_series_discovery.last_distinct_active_ids = diagnostic.distinct_active_ids;
    status.historical_series_discovery.historical_series_confirmed = diagnostic.historical_series_confirmed;
    status.historical_series_discovery.historical_series_event_name = diagnostic.historical_series_confirmed ? diagnostic.event_name : null;
    status.historical_series_discovery.historical_series_request_ref = diagnostic.historical_series_confirmed ? diagnostic.request_ref : null;
    status.historical_series_discovery.last_error_code = null;
  }

  function firstCandlesDiagnostic(value, event_name, direction) {
    const msg = value && typeof value === 'object' && !Array.isArray(value) ? value.msg : null;
    const body = msg && typeof msg === 'object' && !Array.isArray(msg) ? msg.body : null;
    const candidate = collectionCandidate(value);
    return {
      event_name,
      direction,
      top_level_type: valueType(value),
      top_level_keys: safeKeys(value),
      msg_type: valueType(msg),
      msg_keys: safeKeys(msg),
      body_type: valueType(body),
      body_keys: safeKeys(body),
      candidate_collection_path: candidate ? candidate.path : null,
      candidate_collection_length: candidate ? candidate.length : null,
      received_at: Date.now(),
      relay_ready_at: null,
      websocket_created_at: status.websocket_created_at
    };
  }

  function updateFirstCandlesMainDiagnostic(diagnostic) {
    status.historical_diagnostic.first_candles_seen_main += 1;
    status.historical_diagnostic.first_candles_collection_count = diagnostic.candidate_collection_length || 0;
    status.historical_diagnostic.first_candles_last_error_code = null;
    status.historical_diagnostic.event_name = diagnostic.event_name;
    status.historical_diagnostic.direction = diagnostic.direction;
    status.historical_diagnostic.top_level_type = diagnostic.top_level_type;
    status.historical_diagnostic.top_level_keys = diagnostic.top_level_keys;
    status.historical_diagnostic.msg_type = diagnostic.msg_type;
    status.historical_diagnostic.msg_keys = diagnostic.msg_keys;
    status.historical_diagnostic.body_type = diagnostic.body_type;
    status.historical_diagnostic.body_keys = diagnostic.body_keys;
    status.historical_diagnostic.candidate_collection_path = diagnostic.candidate_collection_path;
    status.historical_diagnostic.candidate_collection_length = diagnostic.candidate_collection_length;
    status.historical_diagnostic.received_at = diagnostic.received_at;
    status.historical_diagnostic.relay_ready_at = diagnostic.relay_ready_at;
    status.historical_diagnostic.websocket_created_at = diagnostic.websocket_created_at;
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
      const event_name = String(name);
      const payload = {
        event_name: String(name),
        source: 'POLARIUM_AUTHORIZED_BROWSER',
        payload: sanitizeAllowedPayload(value)
      };
      const observedSymbol = observedSymbolSnapshot(value);
      if (observedSymbol) {
        payload.observed_symbol = observedSymbol.symbol;
        payload.observed_symbol_source = observedSymbol.source;
      }
      if (event_name === 'first-candles') {
        payload.diagnostic = firstCandlesDiagnostic(value, event_name, 'server_to_client');
        updateFirstCandlesMainDiagnostic(payload.diagnostic);
      }
      if (DISCOVERY_EVENTS.has(event_name)) {
        payload.discovery = discoveryDiagnostic(value, event_name, 'server_to_client');
        updateDiscoveryStatus(payload.discovery);
      }
      if (event_name === 'candles-generated') {
        payload.candles_generated_diagnostic = candlesGeneratedDiagnostic(value, event_name, 'server_to_client');
        updateCandlesGeneratedStatus(payload.candles_generated_diagnostic);
      }
      return payload;
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

  const NativeFetch = window.fetch ? window.fetch.bind(window) : null;
  if (NativeFetch && !window.fetch.__fridayTradeBridgePatched) {
    const FridayTradeFetch = (...args) => {
      const requestUrl = args[0] && typeof args[0] === 'object' && 'url' in args[0] ? args[0].url : args[0];
      const method = (args[1] && args[1].method) || (args[0] && typeof args[0] === 'object' && args[0].method) || 'GET';
      publishTransportDiagnostic(transportDiagnostic({
        transport: 'fetch_request',
        method,
        url: requestUrl
      }));
      return NativeFetch(...args).then((response) => {
        try {
          const contentType = response.headers && typeof response.headers.get === 'function' ? response.headers.get('content-type') : null;
          response.clone().text()
            .then((text) => {
              publishTransportDiagnostic(transportDiagnostic({
                transport: 'fetch_response',
                method,
                url: response.url || requestUrl,
                statusCode: response.status,
                contentType,
                parsedBody: parseTransportBody(text)
              }));
            })
            .catch(() => {
              publishTransportDiagnostic({
                ...transportDiagnostic({
                  transport: 'fetch_response',
                  method,
                  url: response.url || requestUrl,
                  statusCode: response.status,
                  contentType
                }),
                last_error_code: 'TRANSPORT_PARSE_FAILED'
              });
            });
        } catch (_) {
          // Never interfere with the page transport.
        }
        return response;
      });
    };
    FridayTradeFetch.__fridayTradeBridgePatched = true;
    FridayTradeFetch.__originalFetch = NativeFetch;
    Object.defineProperty(window, 'fetch', {
      configurable: true,
      writable: true,
      value: FridayTradeFetch
    });
  }

  const NativeXMLHttpRequest = window.XMLHttpRequest;
  if (NativeXMLHttpRequest && !NativeXMLHttpRequest.prototype.__fridayTradeBridgePatched) {
    const nativeOpen = NativeXMLHttpRequest.prototype.open;
    const nativeSend = NativeXMLHttpRequest.prototype.send;

    NativeXMLHttpRequest.prototype.open = function fridayTradeOpen(method, url, ...rest) {
      this.__fridayTradeBridgeRequest = { method: method || 'GET', url };
      return nativeOpen.call(this, method, url, ...rest);
    };

    NativeXMLHttpRequest.prototype.send = function fridayTradeSend(body) {
      const request = this.__fridayTradeBridgeRequest || { method: 'GET', url: window.location.href };
      publishTransportDiagnostic(transportDiagnostic({
        transport: 'xhr_request',
        method: request.method,
        url: request.url
      }));
      const onDone = () => {
        if (this.readyState !== 4) return;
        try {
          const contentType = typeof this.getResponseHeader === 'function' ? this.getResponseHeader('content-type') : null;
          const responseText = typeof this.responseText === 'string' ? this.responseText : '';
          publishTransportDiagnostic(transportDiagnostic({
            transport: 'xhr_response',
            method: request.method,
            url: this.responseURL || request.url,
            statusCode: this.status,
            contentType,
            parsedBody: parseTransportBody(responseText)
          }));
        } catch (_) {
          publishTransportDiagnostic({
            ...transportDiagnostic({
              transport: 'xhr_response',
              method: request.method,
              url: request.url,
              statusCode: this.status
            }),
            last_error_code: 'TRANSPORT_PARSE_FAILED'
          });
        }
      };
      try {
        this.addEventListener('loadend', onDone, { once: true });
      } catch (_) {
        // Never interfere with the page transport.
      }
      return nativeSend.call(this, body);
    };

    NativeXMLHttpRequest.prototype.__fridayTradeBridgePatched = true;
    NativeXMLHttpRequest.__originalOpen = nativeOpen;
    NativeXMLHttpRequest.__originalSend = nativeSend;
  }

  const NativeWebSocket = window.WebSocket;
  if (!NativeWebSocket || NativeWebSocket.__fridayTradeBridgePatched) return;

  function FridayTradeWebSocket(url, protocols) {
    const socket = protocols ? new NativeWebSocket(url, protocols) : new NativeWebSocket(url);
    status.websocket_created_at = Date.now();
    status.historical_diagnostic.websocket_created_at = status.websocket_created_at;

    socket.addEventListener('open', () => {
      status.websocket_opened_at = Date.now();
    });

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
      if (parsed && name && DISCOVERY_EVENTS.has(String(name)) && !containsSensitiveMarker(parsed)) {
        const event_name = String(name);
        const payload = {
          event_name,
          source: 'POLARIUM_AUTHORIZED_BROWSER',
          payload: sanitizeAllowedPayload(parsed),
          discovery: discoveryDiagnostic(parsed, event_name, 'client_to_server')
        };
        const observedSymbol = observedSymbolSnapshot(parsed);
        if (observedSymbol) {
          payload.observed_symbol = observedSymbol.symbol;
          payload.observed_symbol_source = observedSymbol.source;
        }
        if (event_name === 'sendMessage' || event_name === 'get-first-candles' || event_name === 'subscribeMessage') {
          payload.outbound_candle_request_diagnostic = outboundRequestDiagnostic(parsed, event_name);
          updateOutboundStatus(payload.outbound_candle_request_diagnostic);
        }
        updateDiscoveryStatus(payload.discovery);
        publishMarketEvent(payload);
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
    },
    scanRuntimeStores() {
      return scanRuntimeStores();
    }
  };

  window.postMessage({ source: PAGE_EVENT_SOURCE, type: 'INSTALLED' }, window.location.origin);
})();
