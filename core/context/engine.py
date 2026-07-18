from core.engine import EngineDescriptor


class ContextEngine:
    descriptor = EngineDescriptor(name="context", responsibility="Normalize user, module, and session context.")

    def describe(self) -> str:
        return self.descriptor.responsibility

