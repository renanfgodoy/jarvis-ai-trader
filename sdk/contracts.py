from __future__ import annotations

from typing import Protocol

from sdk.manifest import ModuleManifest
from sdk.metadata import ModuleMetadata
from sdk.models import ModuleRequest, ModuleResponse


class ModuleContract(Protocol):
    def initialize(self) -> None: ...

    def execute(self, request: ModuleRequest) -> ModuleResponse: ...

    def validate(self, request: ModuleRequest) -> None: ...

    def shutdown(self) -> None: ...

    def metadata(self) -> ModuleMetadata: ...

    def manifest(self) -> ModuleManifest: ...
