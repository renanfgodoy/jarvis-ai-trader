from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Mapping

from core.identity.models import IdentityProfile


def normalize_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    json.dumps(metadata, ensure_ascii=False, sort_keys=True, default=str)
    return dict(metadata)


def build_identity_profile_fingerprint(profile: IdentityProfile) -> str:
    payload = {
        "identity_id": profile.identity_id,
        "version": profile.version,
        "language": profile.language,
        "tone": profile.tone,
        "style": profile.style,
        "principles": profile.principles,
        "capabilities": profile.capabilities,
        "limitations": profile.limitations,
        "metadata": normalize_metadata(profile.metadata),
    }
    return _sha256(payload)


def with_profile_fingerprint(profile: IdentityProfile) -> IdentityProfile:
    return replace(profile, fingerprint=build_identity_profile_fingerprint(profile))


def build_identity_result_fingerprint(profile: IdentityProfile, metadata: Mapping[str, Any]) -> str:
    payload = {
        "identity_id": profile.identity_id,
        "version": profile.version,
        "language": profile.language,
        "tone": profile.tone,
        "style": profile.style,
        "principles": profile.principles,
        "capabilities": profile.capabilities,
        "limitations": profile.limitations,
        "metadata": normalize_metadata(metadata),
    }
    return _sha256(payload)


def _sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
