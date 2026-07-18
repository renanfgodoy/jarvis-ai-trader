from core.engine import EngineDescriptor


class AnalyticsEngine:
    descriptor = EngineDescriptor(name="analytics", responsibility="Metrics, dashboards, and product intelligence contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility

