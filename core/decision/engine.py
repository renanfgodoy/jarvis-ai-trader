from core.engine import EngineDescriptor


class DecisionEngine:
    descriptor = EngineDescriptor(name="decision", responsibility="Validate AI output and produce final structured decisions.")

    def describe(self) -> str:
        return self.descriptor.responsibility

