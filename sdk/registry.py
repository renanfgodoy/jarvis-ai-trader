from __future__ import annotations

from sdk.base import BaseModule
from sdk.exceptions import ModuleRegistryException
from sdk.validators import ModuleValidator


class ModuleRegistry:
    def __init__(self, validator: ModuleValidator | None = None) -> None:
        self.validator = validator or ModuleValidator()
        self._modules: dict[str, BaseModule] = {}
        self._default_module: str | None = None

    def register(self, module: BaseModule, *, default: bool = False) -> None:
        manifest = module.manifest()
        self.validator.validate_manifest(manifest)
        name = manifest.name.strip().lower()
        if name in self._modules:
            raise ModuleRegistryException(f"module already registered: {name}")
        self._modules[name] = module
        if default or self._default_module is None:
            self._default_module = name

    def unregister(self, name: str) -> None:
        normalized = name.strip().lower()
        if normalized not in self._modules:
            raise ModuleRegistryException(f"module not registered: {normalized}")
        del self._modules[normalized]
        if self._default_module == normalized:
            self._default_module = next(iter(self._modules), None)

    def get(self, name: str) -> BaseModule:
        normalized = name.strip().lower()
        if normalized not in self._modules:
            raise ModuleRegistryException(f"module not registered: {normalized}")
        return self._modules[normalized]

    def list(self) -> tuple[str, ...]:
        return tuple(sorted(self._modules))

    def exists(self, name: str) -> bool:
        return name.strip().lower() in self._modules

    def default(self) -> BaseModule | None:
        if self._default_module is None:
            return None
        return self._modules[self._default_module]

    def clear(self) -> None:
        self._modules.clear()
        self._default_module = None
