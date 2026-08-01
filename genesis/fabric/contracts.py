from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContractSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class ContractSchema:
    """Schema definition for an event contract."""

    topic: str = ""
    version: str = "1.0.0"
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)
    field_validators: dict[str, str] = field(default_factory=dict)
    max_size_bytes: int = 1024 * 1024
    timeout_secs: float = 30.0
    retry_allowed: bool = True
    max_retries: int = 3
    description: str = ""

    def validate_body(self, body: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for field_name in self.required_fields:
            if field_name not in body:
                errors.append(f"Missing required field: {field_name}")
        for field_name, expected_type in self.field_types.items():
            if field_name in body:
                val = body[field_name]
                if expected_type == "string" and not isinstance(val, str):
                    errors.append(f"Field '{field_name}' must be string, got {type(val).__name__}")
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    errors.append(f"Field '{field_name}' must be number, got {type(val).__name__}")
                elif expected_type == "list" and not isinstance(val, list):
                    errors.append(f"Field '{field_name}' must be list, got {type(val).__name__}")
                elif expected_type == "dict" and not isinstance(val, dict):
                    errors.append(f"Field '{field_name}' must be dict, got {type(val).__name__}")
        for field_name, pattern in self.field_validators.items():
            if field_name in body:
                val = str(body[field_name])
                if not re.match(pattern, val):
                    errors.append(f"Field '{field_name}' does not match pattern: {pattern}")
        return errors


class ContractViolation(Exception):
    def __init__(self, message: str, contract: str = "",
                 errors: list[str] | None = None,
                 severity: ContractSeverity = ContractSeverity.ERROR):
        super().__init__(message)
        self.contract = contract
        self.errors = errors or []
        self.severity = severity


@dataclass
class EventContract:
    """A typed event contract connecting producers and consumers."""

    topic: str = ""
    schema: ContractSchema | None = None
    producer: str = ""
    consumers: list[str] = field(default_factory=list)
    required: bool = False

    def validate(self, body: dict[str, Any]) -> list[str]:
        if self.schema:
            return self.schema.validate_body(body)
        return []

    def assert_valid(self, body: dict[str, Any]):
        errors = self.validate(body)
        if errors:
            raise ContractViolation(
                f"Contract violation for topic '{self.topic}'",
                contract=self.topic,
                errors=errors,
            )


class ContractRegistry:
    """Registry of typed event contracts."""

    def __init__(self):
        self._contracts: dict[str, EventContract] = {}

    def register(self, contract: EventContract):
        self._contracts[contract.topic] = contract

    def get(self, topic: str) -> EventContract | None:
        return self._contracts.get(topic)

    def validate_message(self, topic: str, body: dict[str, Any]) -> list[str]:
        contract = self._contracts.get(topic)
        if contract:
            return contract.validate(body)
        return []

    def list_contracts(self) -> list[EventContract]:
        return list(self._contracts.values())

    def summary(self) -> dict[str, Any]:
        return {
            "contracts": len(self._contracts),
            "topics": [c.topic for c in self._contracts.values()],
        }
