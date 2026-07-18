from __future__ import annotations

import asyncio
import struct
import zlib

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.vision.clients.openai_client import OpenAIVisionClient
from app.vision.history import vision_history_repository
from app.vision.service import vision_rate_limiter


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_vision_state(monkeypatch: pytest.MonkeyPatch):
    vision_history_repository.clear()
    vision_rate_limiter.clear()
    monkeypatch.setattr(settings, "friday_vision_enabled", True)
    monkeypatch.setattr(settings, "friday_vision_provider", "fake")
    monkeypatch.setattr(settings, "friday_vision_save_history", True)
    monkeypatch.setattr(settings, "friday_vision_cooldown_seconds", 0)
    monkeypatch.setattr(settings, "friday_vision_max_analyses_per_hour", 30)
    monkeypatch.setattr(settings, "openai_api_key", None)
    yield
    vision_history_repository.clear()
    vision_rate_limiter.clear()


def test_vision_status_available() -> None:
    response = client.get("/api/v1/vision/status")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "VISION_FIRST"
    assert data["analysis_available"] is True
    assert "openai_api_key" not in data


def test_valid_analysis_with_fake_client_saves_history() -> None:
    response = post_image(request_id="valid-1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["decision"] == "WAIT"
    assert data["confidence"] == 42
    assert data["model"] == "fake-vision-client"

    history = client.get("/api/v1/vision/history").json()["items"]
    assert len(history) == 1
    assert history[0]["analysis_id"] == data["analysis_id"]
    assert "image" not in history[0]


def test_history_item_does_not_return_image() -> None:
    analysis = post_image(request_id="history-1").json()
    response = client.get(f"/api/v1/vision/history/{analysis['analysis_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == analysis["analysis_id"]
    assert "base64" not in str(data).lower()


def test_openai_provider_without_key_does_not_fallback_to_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "friday_vision_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", None)
    response = post_image(request_id="missing-key")
    assert response.status_code == 503
    assert response.json()["detail"]["error_code"] == "VISION_PROVIDER_NOT_CONFIGURED"


def test_vision_disabled_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "friday_vision_enabled", False)
    response = post_image(request_id="disabled")
    assert response.status_code == 503
    assert response.json()["detail"]["error_code"] == "VISION_DISABLED"


def test_empty_image_is_rejected() -> None:
    response = post_image(image=b"", request_id="empty")
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "VISION_IMAGE_EMPTY"


def test_corrupted_image_is_rejected() -> None:
    response = post_image(image=b"not an image", request_id="corrupted")
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "VISION_IMAGE_UNSUPPORTED"


def test_small_image_is_rejected() -> None:
    response = post_image(image=png_bytes(100, 100), request_id="small")
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "VISION_IMAGE_TOO_SMALL"


def test_mime_mismatch_is_rejected() -> None:
    response = post_image(content_type="image/jpeg", request_id="mime")
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "VISION_IMAGE_UNSUPPORTED"


def test_duplicate_request_id_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "friday_vision_cooldown_seconds", 3)
    first = post_image(request_id="same-id")
    second = post_image(request_id="same-id")
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"]["error_code"] == "VISION_DUPLICATE_REQUEST"


def test_rate_limit_is_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "friday_vision_max_analyses_per_hour", 1)
    first = post_image(request_id="rate-1")
    second = post_image(request_id="rate-2")
    assert first.status_code == 200
    assert second.status_code == 429


def test_openai_client_mocked_validates_structured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 200

        def json(self) -> dict:
            return {
                "output_text": (
                    '{"decision":"WAIT","asset_detected":null,"timeframe_detected":"M1",'
                    '"expiration_considered":"1 minuto","trend":"UNCLEAR","market_state":"UNCLEAR",'
                    '"risk":"HIGH","confidence":55,"image_quality":"ACCEPTABLE","chart_visible":true,'
                    '"candles_visible":true,"summary":"Resumo visual conservador.",'
                    '"market_reading":"Leitura sem confirmação suficiente.",'
                    '"entry_condition":"Aguardar confirmação clara.",'
                    '"invalidation_condition":"Ignorar se o contexto mudar.",'
                    '"support_zones":[],"resistance_zones":[],"warnings":["Sem garantia."],'
                    '"limitations":["Imagem limitada."]}'
                )
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, *args, **kwargs) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    result = asyncio.run(
        OpenAIVisionClient(api_key="test-key", model="test-model").analyze(
            image_bytes=png_bytes(320, 240),
            mime_type="image/png",
            context=vision_context(),
        )
    )
    assert result.model == "test-model"
    assert result.confidence == 55


def test_broker_routes_still_retired() -> None:
    assert client.get("/api/v1/market/chart").status_code == 410
    assert client.get("/api/v1/market/providers/iq-option/status").status_code == 410


def post_image(
    *,
    image: bytes | None = None,
    content_type: str = "image/png",
    request_id: str,
):
    return client.post(
        "/api/v1/vision/analyze",
        files={"image": ("chart.png", image if image is not None else png_bytes(320, 240), content_type)},
        data={
            "asset": "EUR/USD OTC",
            "timeframe": "M1",
            "expiration": "1 minuto",
            "strategy_mode": "COMPLETE",
            "user_notes": "Teste automatizado sanitizado.",
        },
        headers={"X-Request-ID": request_id},
    )


def vision_context():
    from app.vision.models import VisionAnalysisRequest

    return VisionAnalysisRequest(
        asset="EUR/USD OTC",
        timeframe="M1",
        expiration="1 minuto",
        strategy_mode="COMPLETE",
        user_notes=None,
        image_hash="abc",
        image_width=320,
        image_height=240,
        mime_type="image/png",
    )


def png_bytes(width: int, height: int) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * width for _ in range(height))
    idat = chunk(b"IDAT", zlib.compress(raw))
    return signature + ihdr + idat + chunk(b"IEND", b"")


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
