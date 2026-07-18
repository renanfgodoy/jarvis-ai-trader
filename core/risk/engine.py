from core.engine import EngineDescriptor


class RiskEngine:
    descriptor = EngineDescriptor(name="risk", responsibility="Risk, confidence, limits, and score contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility

