from __future__ import annotations

from core.prompts.contracts import PromptTemplate
from core.prompts.exceptions import (
    DuplicatePromptTemplateError,
    PromptTemplateNotFoundError,
    PromptTemplateVersionNotFoundError,
)


class PromptTemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, PromptTemplate]] = {}
        self._defaults: dict[str, str] = {}

    def register(self, template: PromptTemplate, *, default: bool = False) -> None:
        template_id = template.template_id.strip()
        version = template.version.strip()
        versions = self._templates.setdefault(template_id, {})
        if version in versions:
            raise DuplicatePromptTemplateError(f"template already registered: {template_id}@{version}")
        versions[version] = template
        if default or template_id not in self._defaults:
            self._defaults[template_id] = version

    def get(self, template_id: str, version: str | None = None) -> PromptTemplate:
        normalized = template_id.strip()
        if normalized not in self._templates:
            raise PromptTemplateNotFoundError(f"template not found: {normalized}")
        selected_version = version or self._defaults[normalized]
        if selected_version not in self._templates[normalized]:
            raise PromptTemplateVersionNotFoundError(f"template version not found: {normalized}@{selected_version}")
        return self._templates[normalized][selected_version]

    def list_templates(self) -> tuple[str, ...]:
        return tuple(sorted(self._templates))

    def list_versions(self, template_id: str) -> tuple[str, ...]:
        normalized = template_id.strip()
        if normalized not in self._templates:
            raise PromptTemplateNotFoundError(f"template not found: {normalized}")
        return tuple(sorted(self._templates[normalized]))

    def default_version(self, template_id: str) -> str:
        normalized = template_id.strip()
        if normalized not in self._defaults:
            raise PromptTemplateNotFoundError(f"template not found: {normalized}")
        return self._defaults[normalized]
