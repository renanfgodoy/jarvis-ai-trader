from __future__ import annotations

import json
from pathlib import Path

BRIDGE_ROOT = Path("tools/polarium-browser-bridge")


def test_manifest_runs_page_bridge_in_main_world() -> None:
    manifest = json.loads((BRIDGE_ROOT / "manifest.json").read_text(encoding="utf-8"))

    main_script = manifest["content_scripts"][0]
    relay_script = manifest["content_scripts"][1]

    assert main_script["js"] == ["page-bridge-main.js"]
    assert main_script["run_at"] == "document_start"
    assert main_script["world"] == "MAIN"
    assert "https://trade.polariumbroker.com/*" in main_script["matches"]
    assert "https://*.polariumbroker.com/*" in main_script["matches"]
    assert relay_script["js"] == ["content-script.js"]
    assert "background" in manifest
    assert manifest["background"]["service_worker"] == "background.js"
    assert manifest["action"]["default_title"] == "Friday Trade Polarium Bridge"


def test_content_script_relays_page_messages_and_does_not_patch_websocket_directly() -> None:
    content = (BRIDGE_ROOT / "content-script.js").read_text(encoding="utf-8")

    assert "window.addEventListener('message'" in content
    assert "chrome.runtime.sendMessage" in content
    assert "window.WebSocket =" not in content
    assert "new NativeWebSocket" not in content
    assert "document.createElement('script')" not in content


def test_content_script_defends_against_invalidated_extension_context() -> None:
    content = (BRIDGE_ROOT / "content-script.js").read_text(encoding="utf-8")

    assert "runtimeMessagingAvailable()" in content
    assert "typeof chrome !== 'undefined'" in content
    assert "chrome.runtime.id" in content
    assert "typeof chrome.runtime.sendMessage === 'function'" in content
    assert "try {" in content
    assert "catch (error)" in content
    assert "EXTENSION_CONTEXT_INVALIDATED" in content
    assert "status.relay_active = false" in content


def test_main_world_script_patches_websocket_once_and_preserves_original() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "window.__FRIDAY_TRADE_POLARIUM_BRIDGE_MAIN_INSTALLED__" in page
    assert "const NativeWebSocket = window.WebSocket" in page
    assert "new NativeWebSocket" in page
    assert "__originalWebSocket = NativeWebSocket" in page
    assert "Object.defineProperty(window, 'WebSocket'" in page


def test_main_world_script_sanitizes_before_postmessage() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "ALLOWED_EVENTS" in page
    assert "BLOCKED_EVENTS" in page
    assert "SENSITIVE_MARKERS" in page
    assert "containsSensitiveMarker(value)" in page
    assert "sanitizeAllowedPayload(value)" in page
    assert "window.postMessage({ source: PAGE_EVENT_SOURCE, type: 'MARKET_EVENT', payload }" in page
    assert "http://127.0.0.1:8000/api/v1/polarium/browser-bridge/message" not in page


def test_main_world_script_observes_symbol_passively_without_manual_active_id_map() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "sanitizeObservedSymbol" in page
    assert "findSymbolInDom" in page
    assert "observed_symbol" in page
    assert "observed_symbol_source" in page
    assert "polarium_dom" in page
    assert "manual" not in page.lower()
    assert "activeIdTo" not in page
    assert "active_id_map" not in page


def test_main_world_script_keeps_latest_items_from_large_historical_collections() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "value.slice(-200)" in page


def test_main_world_script_records_sanitized_first_candles_diagnostic() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "first_candles_seen_main" in page
    assert "firstCandlesDiagnostic" in page
    assert "candidate_collection_path" in page
    assert "candidate_collection_length" in page
    assert "direction: null" in page
    assert "'server_to_client'" in page
    assert "websocket_created_at" in page
    assert "safeKeys(value)" in page


def test_content_script_records_relay_timestamp_and_first_candles_relay_counter() -> None:
    content = (BRIDGE_ROOT / "content-script.js").read_text(encoding="utf-8")

    assert "relay_ready_at: Date.now()" in content
    assert "first_candles_relayed" in content
    assert "mergeHistoricalDiagnostic(payload)" in content
    assert "relayPayload" in content


def test_bridge_diagnostic_never_forwards_raw_historical_collection_metadata_keys_as_values() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "collectionCandidate(value" in page
    assert "value.candles.length" in page
    assert "Object.keys(value.candles_by_size).length" in page
    assert "candidate_collection_length" in page


def test_main_world_script_observes_historical_request_and_response_candidates_without_modifying_send() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "DISCOVERY_EVENTS" in page
    assert "'get-first-candles'" in page
    assert "'subscribeMessage'" in page
    assert "'sendMessage'" in page
    assert "discoveryDiagnostic(parsed, event_name, 'client_to_server')" in page
    assert "return originalSend(data)" in page


def test_main_world_script_uses_sanitized_request_refs_and_never_exposes_raw_request_id() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "requestRefs = new Map()" in page
    assert "`request-${requestRefCounter}`" in page
    assert "lowered === 'request_id'" in page
    assert "request_id_present" in page


def test_main_world_script_classifies_historical_series_by_single_series_and_timestamp_count() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "distinct_active_ids === 1 && distinct_raw_sizes === 1 && distinct_timestamps >= 20" in page
    assert "distinct_timestamps" in page
    assert "distinct_raw_sizes" in page
    assert "distinct_active_ids" in page


def test_main_world_script_records_candles_generated_structure_without_modifying_messages() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "candles_generated_diagnostic" in page
    assert "candlesGeneratedDiagnostic" in page
    assert "collectStructurePaths" in page
    assert "structuralCollectionCandidate" in page
    assert "nested_array_paths" in page
    assert "nested_object_paths" in page
    assert "return originalSend(data)" in page


def test_main_world_script_filters_market_value_keys_from_structural_keys() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "MARKET_VALUE_KEYS" in page
    assert "MARKET_VALUE_KEYS.has(lowered)" in page


def test_main_world_script_records_outbound_request_diagnostic_without_replaying_requests() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "outbound_candle_request_diagnostic" in page
    assert "outboundRequestDiagnostic" in page
    assert "updateOutboundStatus" in page
    assert "payload.outbound_candle_request_diagnostic" in page
    assert "return originalSend(data)" in page
    assert page.count("originalSend(data)") == 1


def test_main_world_script_observes_fetch_passively_without_replaying_requests() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "const NativeFetch = window.fetch ? window.fetch.bind(window) : null" in page
    assert "NativeFetch(...args)" in page
    assert "return response" in page
    assert "response.clone().text()" in page
    assert "transport: 'fetch_request'" in page
    assert "transport: 'fetch_response'" in page
    assert "publishTransportDiagnostic" in page
    assert "headers: " not in page
    assert "body: " not in page


def test_main_world_script_observes_xhr_passively_without_modifying_body() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "const NativeXMLHttpRequest = window.XMLHttpRequest" in page
    assert "const nativeOpen = NativeXMLHttpRequest.prototype.open" in page
    assert "const nativeSend = NativeXMLHttpRequest.prototype.send" in page
    assert "nativeOpen.call(this, method, url, ...rest)" in page
    assert "nativeSend.call(this, body)" in page
    assert "transport: 'xhr_request'" in page
    assert "transport: 'xhr_response'" in page


def test_main_world_script_sanitizes_transport_url_and_keeps_limited_shape_catalog() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "sanitizeUrlParts(input)" in page
    assert "url.pathname" in page
    assert "url.search" not in page
    assert "historical_transport_discovery" in page
    assert "historical_transport_shapes" in page
    assert "transportShapes = new Map()" in page
    assert "transportShapes.size < 8" in page
    assert "shape_ref: `transport_shape_${transportShapes.size + 1}`" in page


def test_main_world_script_exposes_runtime_store_scan_only_as_explicit_command() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "runtime_store_discovery" in page
    assert "runtime_store_candidates" in page
    assert "scanRuntimeStores()" in page
    assert "window.__FRIDAY_TRADE_POLARIUM_BRIDGE__" in page
    assert "return scanRuntimeStores();" in page
    assert "setInterval(scanRuntimeStores" not in page
    assert "addEventListener('load', scanRuntimeStores" not in page


def test_runtime_store_scan_has_depth_object_timeout_and_cycle_limits() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "RUNTIME_SCAN_LIMITS" in page
    assert "depth: 5" in page
    assert "objects: 350" in page
    assert "milliseconds: 180" in page
    assert "const visited = new WeakSet()" in page
    assert "visited.has(value)" in page
    assert "performance.now() - started > RUNTIME_SCAN_LIMITS.milliseconds" in page


def test_runtime_store_scan_inspects_required_sources_structurally() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    for marker in ["redux", "mobx", "zustand", "datafeed", "tradingview", "lightweight", "chart", "candles"]:
        assert marker in page
    assert "__reactFiber" in page
    assert "__reactProps" in page
    assert "__reactContainer" in page
    assert "localStorage" in page
    assert "sessionStorage" in page
    assert "indexedDB" in page
    assert "typeof Worker !== 'undefined'" in page
    assert "typeof SharedWorker !== 'undefined'" in page


def test_runtime_store_scan_does_not_call_write_or_chart_mutation_methods() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert ".dispatch(" not in page
    assert ".setData(" not in page
    assert ".update(" not in page
    assert ".subscribe(" not in page
    assert ".getBars(" not in page
    assert ".subscribeBars(" not in page
    assert ".getState(" not in page


def test_runtime_store_scan_sanitizes_catalog_and_avoids_ohlc_values() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "MARKET_VALUE_KEYS.has" in page
    assert "runtimeSafeName" in page
    assert "SENSITIVE_MARKERS.some" in page
    assert "collection_length" in page
    assert "distinct_timestamps" in page
    assert "distinct_raw_sizes" in page
    assert "distinct_active_ids" in page
    assert "runtimeStoreCandidates.size < RUNTIME_SCAN_LIMITS.candidates" in page


def test_main_world_script_catalogs_limited_outbound_request_shapes() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "requestShapes = new Map()" in page
    assert "request_shape_" in page
    assert "requestShapes.size < 8" in page
    assert "shapeFingerprint" in page


def test_main_world_script_detects_outbound_fields_by_presence_not_values() -> None:
    page = (BRIDGE_ROOT / "page-bridge-main.js").read_text(encoding="utf-8")

    assert "has_active_id" in page
    assert "has_size" in page
    assert "has_count" in page
    assert "has_from" in page
    assert "has_to" in page
    assert "numeric_field_names" in page
    assert "string_field_names" in page


def test_background_forwards_to_local_backend_with_bridge_header() -> None:
    background = (BRIDGE_ROOT / "background.js").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8000/api/v1/polarium/browser-bridge/message" in background
    assert "X-Friday-Trade-Bridge" in background
    assert "POLARIUM_AUTHORIZED_BROWSER" in background
    assert "chrome.runtime.onMessage.addListener" in background
