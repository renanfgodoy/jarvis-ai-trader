from __future__ import annotations

from sdk.config import ModuleConfig
from sdk.exceptions import ModuleManifestException, ModuleValidationException
from sdk.manifest import ModuleManifest
from sdk.metadata import ModuleMetadata
from sdk.models import ModuleRequest, ModuleResponse


class ModuleValidator:
    def validate_config(self, config: ModuleConfig) -> None:
        if not isinstance(config.enabled, bool):
            raise ModuleValidationException("config.enabled must be boolean")
        if not isinstance(config.strict_validation, bool):
            raise ModuleValidationException("config.strict_validation must be boolean")

    def validate_manifest(self, manifest: ModuleManifest) -> None:
        if not manifest.name.strip():
            raise ModuleManifestException("manifest.name is required")
        if not manifest.display_name.strip():
            raise ModuleManifestException("manifest.display_name is required")
        if not manifest.description.strip():
            raise ModuleManifestException("manifest.description is required")
        if not manifest.version.strip():
            raise ModuleManifestException("manifest.version is required")
        if not manifest.identity.strip():
            raise ModuleManifestException("manifest.identity is required")
        if not manifest.provider.strip():
            raise ModuleManifestException("manifest.provider is required")
        if manifest.provider.strip().lower() != "mock":
            raise ModuleManifestException("Module SDK V1 allows only the mock provider")

    def validate_metadata(self, metadata: ModuleMetadata) -> None:
        if not metadata.module.strip():
            raise ModuleValidationException("metadata.module is required")
        if not metadata.version.strip():
            raise ModuleValidationException("metadata.version is required")
        if len(metadata.fingerprint) != 64:
            raise ModuleValidationException("metadata.fingerprint must be a sha256 hex digest")

    def validate_request(self, request: ModuleRequest) -> None:
        if not request.module.strip():
            raise ModuleValidationException("request.module is required")
        if not request.payload.strip():
            raise ModuleValidationException("request.payload is required")

    def validate_response(self, response: ModuleResponse) -> None:
        if not response.module.strip():
            raise ModuleValidationException("response.module is required")
        if response.execution.request_id != response.execution.metadata.request_id:
            raise ModuleValidationException("response execution request_id mismatch")
