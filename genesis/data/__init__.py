"""
Engineering Data Platform (Mission 178) — standardized internal models.

Defines model descriptors, a model registry, and utilities for
serialization, validation, schema evolution, and versioning.

Not a new engine. Every existing model can declare a descriptor here.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class ModelCategory(Enum):
    EVENT = "event"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    OBJECT = "object"
    TIMELINE = "timeline"
    REPORT = "report"
    INSIGHT = "insight"
    WORKFLOW = "workflow"
    AGENT = "agent"
    APP = "app"
    METRIC = "metric"
    CONFIG = "config"
    PROVIDER = "provider"
    PROJECT = "project"
    GRAPH = "graph"


@dataclass
class ModelDescriptor:
    name: str
    category: ModelCategory
    version: str = "1.0.0"
    description: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    validation_rules: dict[str, str] = field(default_factory=dict)
    migrate_from: dict[str, str] = field(default_factory=dict)  # {prev_version: migration_fn_name}


@dataclass
class VersionedPayload:
    model: str
    version: str
    data: dict[str, Any]
    timestamp: str = ""
    schema_hash: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, raw: str) -> VersionedPayload:
        return cls(**json.loads(raw))


class ModelRegistry:
    """Central model registry.

    All subsystems declare their models here for discoverability,
    validation, and migration.
    """

    def __init__(self):
        self._models: dict[str, ModelDescriptor] = {}
        self._lock = threading.RLock()

    def register(self, descriptor: ModelDescriptor):
        with self._lock:
            self._models[descriptor.name] = descriptor

    def get(self, name: str) -> ModelDescriptor | None:
        return self._models.get(name)

    def by_category(self, category: ModelCategory) -> list[ModelDescriptor]:
        return [m for m in self._models.values() if m.category == category]

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": m.name, "category": m.category.value, "version": m.version}
            for m in self._models.values()
        ]

    def validate(self, model_name: str, data: dict[str, Any]) -> list[str]:
        desc = self._models.get(model_name)
        if not desc:
            return [f"Unknown model: {model_name}"]
        errors: list[str] = []
        for field_name in desc.required_fields:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")
        for field_name, rule in desc.validation_rules.items():
            val = data.get(field_name)
            if val is not None:
                if rule == "positive" and (not isinstance(val, (int, float)) or val <= 0):
                    errors.append(f"{field_name} must be positive")
                elif rule == "non_empty_string" and (not isinstance(val, str) or not val.strip()):
                    errors.append(f"{field_name} must be a non-empty string")
                elif rule == "list_of_strings" and (not isinstance(val, list) or not all(isinstance(v, str) for v in val)):
                    errors.append(f"{field_name} must be a list of strings")
        return errors

    def upgrade(self, payload: VersionedPayload) -> VersionedPayload | None:
        desc = self._models.get(payload.model)
        if not desc:
            return None
        if payload.version == desc.version:
            return payload
        current_version = payload.version
        data = dict(payload.data)
        visited = set()
        while current_version != desc.version:
            if current_version in visited:
                break
            visited.add(current_version)
            migration_info = desc.migrate_from.get(current_version)
            if not migration_info:
                break
            current_version = migration_info.get("target_version", current_version)
        return VersionedPayload(
            model=payload.model,
            version=desc.version,
            data=data,
            schema_hash=payload.schema_hash,
        )


# Global model registry
_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    return _registry
