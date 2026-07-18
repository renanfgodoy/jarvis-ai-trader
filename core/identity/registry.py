from __future__ import annotations

from core.identity.config import IdentityConfig
from core.identity.exceptions import DuplicateIdentityError, IdentityNotFoundError, IdentityVersionNotFoundError
from core.identity.models import IdentityProfile
from core.identity.validators import IdentityValidator


class IdentityRegistry:
    def __init__(self, config: IdentityConfig | None = None, validator: IdentityValidator | None = None) -> None:
        self.config = config or IdentityConfig()
        self.validator = validator or IdentityValidator(self.config)
        self._profiles: dict[str, dict[str, IdentityProfile]] = {}
        self._defaults: dict[str, str] = {}

    def register(self, profile: IdentityProfile, *, default: bool = False) -> None:
        self.validator.validate_profile(profile)
        versions = self._profiles.setdefault(profile.identity_id, {})
        if profile.version in versions:
            raise DuplicateIdentityError(f"identity already registered: {profile.identity_id}@{profile.version}")
        versions[profile.version] = profile
        if default or profile.identity_id not in self._defaults:
            self._defaults[profile.identity_id] = profile.version

    def get(self, identity_id: str, version: str | None = None) -> IdentityProfile:
        normalized = identity_id.strip()
        if normalized not in self._profiles:
            raise IdentityNotFoundError(f"identity not found: {normalized}")
        selected_version = version or self._defaults[normalized]
        if selected_version not in self._profiles[normalized]:
            raise IdentityVersionNotFoundError(f"identity version not found: {normalized}@{selected_version}")
        return self._profiles[normalized][selected_version]

    def list_identities(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))

    def list_versions(self, identity_id: str) -> tuple[str, ...]:
        normalized = identity_id.strip()
        if normalized not in self._profiles:
            raise IdentityNotFoundError(f"identity not found: {normalized}")
        return tuple(sorted(self._profiles[normalized]))

    def default_version(self, identity_id: str) -> str:
        normalized = identity_id.strip()
        if normalized not in self._defaults:
            raise IdentityNotFoundError(f"identity not found: {normalized}")
        return self._defaults[normalized]
