from __future__ import annotations


class ExecutionHooks:
    def before_validation(self, context) -> None:
        return None

    def after_validation(self, context) -> None:
        return None

    def before_identity(self, context) -> None:
        return None

    def after_identity(self, context) -> None:
        return None

    def before_prompt(self, context) -> None:
        return None

    def after_prompt(self, context) -> None:
        return None

    def before_provider(self, context) -> None:
        return None

    def after_provider(self, context) -> None:
        return None

    def before_finish(self, context) -> None:
        return None

    def after_finish(self, context) -> None:
        return None
