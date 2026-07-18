from core.engine import EngineDescriptor


class VisionEngine:
    descriptor = EngineDescriptor(name="vision", responsibility="Image and screenshot analysis contracts.")

    def describe(self) -> str:
        return self.descriptor.responsibility

