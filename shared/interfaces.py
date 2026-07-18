from __future__ import annotations

from typing import Protocol

from shared.contracts import PlatformRequest, PlatformResponse, ProviderRequest, ProviderResponse


class Engine(Protocol):
    name: str

    def describe(self) -> str:
        ...


class Module(Protocol):
    name: str

    def handle(self, request: PlatformRequest) -> PlatformResponse:
        ...


class Provider(Protocol):
    name: str

    def execute(self, request: ProviderRequest) -> ProviderResponse:
        ...

