from __future__ import annotations

from typing import Protocol

from core.identity.models import IdentityProfile, IdentityRequest, IdentityResult


class IdentityResolverContract(Protocol):
    def resolve(self, request: IdentityRequest) -> IdentityProfile:
        ...


class IdentityBuilderContract(Protocol):
    def build(self, request: IdentityRequest, profile: IdentityProfile) -> IdentityResult:
        ...
