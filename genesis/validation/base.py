"""
CORE-10a: Validation Foundation — Base types for the validation framework.

Extracted from engine.py to break circular import:
  engine.py → validators/*.py → engine.py

Now: engine.py → base.py ← validators/*.py

Normative References:
  - VPS Part VI §6.3: Validation Semantics
  - CONSTITUTION Article 4: No circular dependencies between layers
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


class ValidationResult:
    """Result of a single validation check."""

    def __init__(
        self,
        validator_name: str,
        category: str,
        passed: bool,
        message: str = "",
        severity: str = "error",
        location: str = "",
    ):
        self.validator_name = validator_name
        self.category = category
        self.passed = passed
        self.message = message
        self.severity = severity
        self.location = location
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator_name": self.validator_name,
            "category": self.category,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.validator_name}: {self.message}"


class BaseValidator(ABC):
    """Abstract base for all validators."""

    def __init__(self, name: str = "", category: str = "general"):
        self.name = name or self.__class__.__name__
        self.category = category

    @abstractmethod
    def validate(self, target: Any) -> ValidationResult:
        ...

    def result(
        self,
        passed: bool,
        message: str = "",
        severity: str = "error",
        location: str = "",
    ) -> ValidationResult:
        return ValidationResult(
            self.name, self.category, passed, message, severity, location
        )
