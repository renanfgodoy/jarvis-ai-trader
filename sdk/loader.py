from __future__ import annotations

from collections.abc import Callable

from sdk.base import BaseModule
from sdk.config import ModuleConfig
from sdk.exceptions import ModuleLoaderException
from sdk.registry import ModuleRegistry
from sdk.validators import ModuleValidator


ModuleBuilder = Callable[[], BaseModule]


class ModuleLoader:
    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        validator: ModuleValidator | None = None,
        config: ModuleConfig | None = None,
    ) -> None:
        self.registry = registry or ModuleRegistry()
        self.validator = validator or ModuleValidator()
        self.config = config or ModuleConfig()
        self._builders: dict[str, ModuleBuilder] = {}
        self.validator.validate_config(self.config)

    def register_builder(self, name: str, builder: ModuleBuilder) -> None:
        normalized = name.strip().lower()
        if not normalized:
            raise ModuleLoaderException("module builder name is required")
        if normalized in self._builders:
            raise ModuleLoaderException(f"module builder already registered: {normalized}")
        self._builders[normalized] = builder

    def load(self, name: str, *, register: bool | None = None, initialize: bool | None = None) -> BaseModule:
        normalized = name.strip().lower()
        if normalized not in self._builders:
            raise ModuleLoaderException(f"module builder not registered: {normalized}")
        module = self._builders[normalized]()
        self.validator.validate_manifest(module.manifest())
        self.validator.validate_metadata(module.metadata())
        should_register = self.config.auto_register if register is None else register
        should_initialize = self.config.auto_initialize if initialize is None else initialize
        if should_register:
            self.registry.register(module)
        if should_initialize:
            module.initialize()
        return module

    def list_builders(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))

    def clear(self) -> None:
        self._builders.clear()


def create_default_module_loader() -> ModuleLoader:
    from modules.trading import TradingModule

    loader = ModuleLoader(config=ModuleConfig(auto_register=True, auto_initialize=True))
    loader.register_builder("trading", TradingModule)
    loader.load("trading")
    return loader
