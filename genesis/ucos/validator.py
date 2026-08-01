"""
UCOS: CapabilityValidator — Validates capability contracts, dependencies, and health.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import (
    Capability, CapabilityDefinition, CapabilityState, MaturityLevel,
)


@dataclass
class ValidationResult:
    capability_id: str = ""
    passed: bool = True
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 1.0
    validated_at: float = 0.0

    def __post_init__(self):
        if not self.validated_at:
            self.validated_at = time.time()


class CapabilityValidator:
    """Validates capability definitions, contracts, dependencies, and health."""

    def __init__(self, registry):
        self._registry = registry
        self._results: dict[str, ValidationResult] = {}
        self._validation_rules: list[callable] = []

    def add_rule(self, rule: callable):
        self._validation_rules.append(rule)

    def validate(self, capability_id: str) -> ValidationResult:
        cap = self._registry.get(capability_id)
        if not cap:
            return ValidationResult(
                capability_id=capability_id,
                passed=False,
                errors=["Capability not found"],
                score=0.0,
            )
        checks = []
        errors = []
        warnings = []
        score = 1.0

        # Identity check
        if not cap.definition.name:
            errors.append("Capability has no name")
            score -= 0.2
        checks.append({"check": "identity", "passed": len(errors) == 0})

        # Version check
        if cap.definition.version.semver == "0.0.0":
            warnings.append("Capability version is 0.0.0")
            score -= 0.05
        checks.append({"check": "version", "passed": True})

        # Contract checks
        contract = cap.definition.contract
        if contract.inputs:
            for inp in contract.inputs:
                if not inp.get("name"):
                    warnings.append("Contract input missing name")
                    score -= 0.05
        if contract.outputs:
            for out in contract.outputs:
                if not out.get("name"):
                    warnings.append("Contract output missing name")
                    score -= 0.05
        checks.append({"check": "contract", "passed": len([e for e in errors if "contract" in e]) == 0})

        # Dependency checks
        for dep_id in cap.definition.dependencies:
            dep = self._registry.get(dep_id)
            if not dep:
                errors.append(f"Dependency '{dep_id}' not registered")
                score -= 0.3
            elif dep.state == CapabilityState.DORMANT:
                warnings.append(f"Dependency '{dep_id}' is dormant")
                score -= 0.1
            elif dep.state == CapabilityState.FAILED:
                errors.append(f"Dependency '{dep_id}' is failed")
                score -= 0.3
        checks.append({"check": "dependencies", "passed": len([e for e in errors if "Dependency" in e]) == 0})

        # Health check
        if cap.definition.health.failure_count > 10:
            warnings.append(f"High failure count: {cap.definition.health.failure_count}")
            score -= 0.1
        if cap.definition.health.error_rate > 0.5:
            warnings.append(f"High error rate: {cap.definition.health.error_rate:.2f}")
            score -= 0.1
        checks.append({"check": "health", "passed": True})

        # Custom rules
        for rule in self._validation_rules:
            try:
                rule_result = rule(cap)
                if rule_result:
                    if isinstance(rule_result, str):
                        warnings.append(rule_result)
                        score -= 0.05
                    elif isinstance(rule_result, list):
                        errors.extend(rule_result)
                        score -= 0.2 * len(rule_result)
            except Exception as e:
                warnings.append(f"Custom rule error: {e}")

        score = max(0.0, min(1.0, score))
        result = ValidationResult(
            capability_id=capability_id,
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            warnings=warnings,
            score=score,
        )
        self._results[capability_id] = result
        return result

    def validate_all(self) -> dict[str, ValidationResult]:
        for cap in self._registry.all:
            self.validate(cap.id)
        return dict(self._results)

    def get_result(self, capability_id: str) -> ValidationResult | None:
        return self._results.get(capability_id)

    def healthy_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all
                if c.definition.health.healthy and c.definition.health.score > 0.7]

    def unhealthy_capabilities(self) -> list[Capability]:
        return [c for c in self._registry.all
                if not c.definition.health.healthy or c.definition.health.score <= 0.7]
