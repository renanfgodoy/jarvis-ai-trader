from __future__ import annotations

from typing import Protocol

from core.orchestrator.context import ExecutionContext


class PipelineStage(Protocol):
    def name(self) -> str:
        ...

    def version(self) -> str:
        ...

    def validate(self, context: ExecutionContext) -> None:
        ...

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        ...

    def rollback(self, context: ExecutionContext) -> None:
        ...
