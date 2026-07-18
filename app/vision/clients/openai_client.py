from __future__ import annotations

import asyncio
import base64
import json
import time

import httpx

from app.core.config import settings
from app.vision.exceptions import VisionProviderError
from app.vision.models import VisionAnalysisRequest, VisionAnalysisResult
from app.vision.prompts import VISION_RESULT_JSON_SCHEMA, VISION_SYSTEM_PROMPT, build_vision_user_prompt
from app.vision.result_validator import VisionResultValidator


class OpenAIVisionClient:
    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        self.model = model or settings.friday_vision_model
        self.validator = VisionResultValidator()

    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        context: VisionAnalysisRequest,
    ) -> VisionAnalysisResult:
        if not self.api_key:
            raise VisionProviderError("OpenAI API key is not configured.", error_code="VISION_PROVIDER_NOT_CONFIGURED")
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        started = time.perf_counter()
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": VISION_SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": build_vision_user_prompt(context)},
                        {"type": "input_image", "image_url": f"data:{mime_type};base64,{encoded_image}"},
                    ],
                },
            ],
            "text": {"format": {"type": "json_schema", **VISION_RESULT_JSON_SCHEMA}},
        }
        try:
            async with httpx.AsyncClient(timeout=settings.friday_vision_analysis_timeout_seconds) as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
        except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
            raise VisionProviderError("Vision provider timeout.", error_code="VISION_PROVIDER_TIMEOUT") from exc
        except httpx.HTTPError as exc:
            raise VisionProviderError("Vision provider unavailable.", error_code="VISION_PROVIDER_UNAVAILABLE") from exc
        if response.status_code == 429:
            raise VisionProviderError("Vision provider rate limit.", error_code="VISION_PROVIDER_RATE_LIMIT")
        if response.status_code >= 400:
            raise VisionProviderError("Vision provider unavailable.", error_code="VISION_PROVIDER_UNAVAILABLE")

        processing_time_ms = int((time.perf_counter() - started) * 1000)
        return self.validator.validate(self._extract_json(response.json()), model=self.model, processing_time_ms=processing_time_ms)

    def _extract_json(self, response_payload: dict) -> dict:
        text = response_payload.get("output_text")
        if not text:
            chunks: list[str] = []
            for item in response_payload.get("output", []) or []:
                for content in item.get("content", []) or []:
                    if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                        chunks.append(content["text"])
            text = "".join(chunks)
        if not isinstance(text, str) or not text.strip():
            raise VisionProviderError("Missing provider structured output.", error_code="VISION_INVALID_PROVIDER_RESPONSE")
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError as exc:
            raise VisionProviderError("Provider output is not JSON.", error_code="VISION_INVALID_PROVIDER_RESPONSE") from exc
        if not isinstance(loaded, dict):
            raise VisionProviderError("Provider output is not an object.", error_code="VISION_INVALID_PROVIDER_RESPONSE")
        return loaded
