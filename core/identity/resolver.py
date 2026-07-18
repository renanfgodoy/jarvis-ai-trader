from __future__ import annotations

from dataclasses import replace

from core.identity.config import IdentityConfig
from core.identity.metadata import with_profile_fingerprint
from core.identity.models import IdentityProfile, IdentityRequest
from core.identity.registry import IdentityRegistry
from core.identity.validators import IdentityValidator


class IdentityResolver:
    resolver_version = "1.0"

    def __init__(
        self,
        registry: IdentityRegistry,
        config: IdentityConfig | None = None,
        validator: IdentityValidator | None = None,
    ) -> None:
        self.registry = registry
        self.config = config or IdentityConfig()
        self.validator = validator or IdentityValidator(self.config)

    def resolve(self, request: IdentityRequest) -> IdentityProfile:
        self.validator.validate_request(request)
        identity_id = request.requested_identity or self.config.default_identity
        profile = self.registry.get(identity_id, self.config.default_version)
        language = request.language or profile.language or self.config.default_language
        if language != profile.language:
            profile = with_profile_fingerprint(replace(profile, language=language))
            self.validator.validate_profile(profile)
        return profile
