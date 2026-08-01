"""
CORE-10: Validation Framework

Universal validation engine for all artifact types.
Every validator is a plugin.

Validation Categories:
  Schema, Naming, Links, Metadata, Policies, Inheritance,
  Dependencies, Ontology, Security, Quality, Documentation,
  Prompt, Graph, Compilation
"""

from pathlib import Path
from typing import Any, Callable

from genesis.validation.base import BaseValidator, ValidationResult


class ValidationEngine:
    """Central validation engine. Runs all registered validators against targets."""

    def __init__(self):
        self._validators: dict[str, BaseValidator] = {}
        self._register_builtins()

    def _register_builtins(self):
        from genesis.validation.validators.schema import SchemaValidator
        from genesis.validation.validators.naming import NamingValidator
        from genesis.validation.validators.structural import StructuralValidator

        self.register(SchemaValidator())
        self.register(NamingValidator())
        self.register(StructuralValidator())

    def register(self, validator: BaseValidator):
        self._validators[validator.name] = validator

    def register_func(self, name: str, category: str, fn: Callable[[Any], ValidationResult]):
        """Register a function as a validator."""

        class FuncValidator(BaseValidator):
            def __init__(self):
                super().__init__(name, category)

            def validate(self, target: Any) -> ValidationResult:
                return fn(target)

        self.register(FuncValidator())

    def get(self, name: str) -> BaseValidator | None:
        return self._validators.get(name)

    def validate(self, target: Any, categories: list[str] | None = None) -> list[ValidationResult]:
        """Run all validators (optionally filtered by category)."""
        results = []
        for validator in self._validators.values():
            if categories and validator.category not in categories:
                continue
            try:
                result = validator.validate(target)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    validator.name, validator.category, False,
                    str(e), "error", str(getattr(target, "path", ""))
                ))
        return results

    def validate_path(self, path: str | Path, categories: list[str] | None = None) -> list[ValidationResult]:
        """Validate a file path using all applicable validators."""
        target = {"path": str(path), "name": Path(path).name, "suffix": Path(path).suffix}
        return self.validate(target, categories)

    def validate_all(self, targets: list[Any], categories: list[str] | None = None) -> dict[str, list[ValidationResult]]:
        """Validate multiple targets. Returns dict keyed by target."""
        return {str(t): self.validate(t, categories) for t in targets}

    def summary(self, results: list[ValidationResult]) -> dict[str, Any]:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        by_category: dict[str, dict[str, int]] = {}
        for r in results:
            by_category.setdefault(r.category, {"passed": 0, "failed": 0})
            by_category[r.category]["passed" if r.passed else "failed"] += 1
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 100.0,
            "by_category": by_category,
        }

    def all_validators(self) -> list[BaseValidator]:
        return list(self._validators.values())
