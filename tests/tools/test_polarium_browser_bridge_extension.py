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
    assert "fetch(" not in page


def test_background_forwards_to_local_backend_with_bridge_header() -> None:
    background = (BRIDGE_ROOT / "background.js").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8000/api/v1/polarium/browser-bridge/message" in background
    assert "X-Friday-Trade-Bridge" in background
    assert "POLARIUM_AUTHORIZED_BROWSER" in background
    assert "chrome.runtime.onMessage.addListener" in background
