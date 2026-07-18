from core.engine import EngineDescriptor


class LearningEngine:
    descriptor = EngineDescriptor(name="learning", responsibility="Future feedback loops and learning contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility

