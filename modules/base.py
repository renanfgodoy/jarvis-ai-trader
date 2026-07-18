from __future__ import annotations

from sdk import BaseModule as SDKBaseModule, ModuleManifest, ModuleMetadata
from shared.contracts import PlatformRequest, PlatformResponse


class BaseModule(SDKBaseModule):
    name = "base"

    def __init__(self) -> None:
        super().__init__(
            manifest=ModuleManifest(
                name=self.name,
                display_name=self.name.title(),
                description=f"{self.name.title()} module placeholder.",
            ),
            metadata=ModuleMetadata(module=self.name, tags=("placeholder",)),
        )

    def handle(self, request: PlatformRequest) -> PlatformResponse:
        return PlatformResponse(request_id=request.request_id, module=self.name, status="placeholder")
