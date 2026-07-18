from core.engine import EngineDescriptor


class AuditEngine:
    descriptor = EngineDescriptor(name="audit", responsibility="Logs, traceability, and audit contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility
