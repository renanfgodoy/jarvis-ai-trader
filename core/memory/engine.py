from core.engine import EngineDescriptor


class MemoryEngine:
    descriptor = EngineDescriptor(name="memory", responsibility="History, preferences, context, and cache contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility

