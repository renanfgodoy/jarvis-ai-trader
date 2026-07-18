from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.identity.metadata import build_identity_result_fingerprint, normalize_metadata
from core.identity.models import IdentityProfile, IdentityRequest, IdentityResult
from core.identity.validators import IdentityValidator


class IdentityBuilder:
    def __init__(self, validator: IdentityValidator | None = None, resolver_version: str = "1.0") -> None:
        self.validator = validator or IdentityValidator()
        self.resolver_version = resolver_version

    def build(self, request: IdentityRequest, profile: IdentityProfile) -> IdentityResult:
        self.validator.validate_request(request)
        self.validator.validate_profile(profile)
        metadata = {
            **normalize_metadata(request.metadata),
            "module": request.module,
            "identity_id": profile.identity_id,
            "version": profile.version,
            "resolver_version": self.resolver_version,
        }
        return IdentityResult(
            request_id=request.request_id or str(uuid4()),
            identity_profile=profile,
            resolved_identity=profile.identity_id,
            metadata=metadata,
            fingerprint=build_identity_result_fingerprint(profile, metadata),
            timestamp=datetime.now(timezone.utc),
        )
