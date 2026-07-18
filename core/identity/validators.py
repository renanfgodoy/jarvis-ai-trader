from __future__ import annotations

import json

from core.identity.config import IdentityConfig
from core.identity.exceptions import IdentityEngineError, InvalidIdentityProfileError, InvalidIdentityRequestError
from core.identity.models import IdentityProfile, IdentityRequest


class IdentityValidator:
    def __init__(self, config: IdentityConfig | None = None) -> None:
        self.config = config or IdentityConfig()

    def validate_request(self, request: IdentityRequest) -> None:
        if request.module not in self.config.supported_modules:
            raise InvalidIdentityRequestError(f"unsupported module: {request.module}")
        if request.language is not None and request.language not in self.config.supported_languages:
            raise InvalidIdentityRequestError(f"unsupported language: {request.language}")
        self._ensure_serializable(request.metadata, "metadata", InvalidIdentityRequestError)
        self._ensure_serializable(request.context, "context", InvalidIdentityRequestError)

    def validate_profile(self, profile: IdentityProfile) -> None:
        if not profile.identity_id.strip():
            raise InvalidIdentityProfileError("identity_id is required")
        if not profile.version.strip():
            raise InvalidIdentityProfileError("version is required")
        if profile.language not in self.config.supported_languages:
            raise InvalidIdentityProfileError(f"unsupported language: {profile.language}")
        if not profile.tone.strip():
            raise InvalidIdentityProfileError("tone is required")
        if not profile.style.strip():
            raise InvalidIdentityProfileError("style is required")
        if not profile.principles:
            raise InvalidIdentityProfileError("principles are required")
        self._ensure_serializable(profile.capabilities, "capabilities", InvalidIdentityProfileError)
        self._ensure_serializable(profile.limitations, "limitations", InvalidIdentityProfileError)
        self._ensure_serializable(profile.metadata, "metadata", InvalidIdentityProfileError)

    def _ensure_serializable(self, value: object, field_name: str, error_type: type[IdentityEngineError]) -> None:
        try:
            json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except (TypeError, ValueError) as exc:
            raise error_type(f"{field_name} must be serializable") from exc
