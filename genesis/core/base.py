"""
CORE-05: Universal Object Model

Every entity in Venus inherits from BaseEntity.
Provides UUID, type hierarchy, metadata, validation, serialization.
"""

import json
from datetime import datetime, timezone
from typing import Any

from genesis.utils.identity import generate_id


class BaseEntity:
    """Foundation for all Venus entities. Every object inherits from this."""

    def __init__(
        self,
        entity_id: str | None = None,
        name: str = "",
        semantic_type: str = "base_entity",
        version: str = "0.1.0",
        description: str = "",
    ):
        self.entity_id = entity_id or generate_id(semantic_type, 12)
        self.name = name
        self.semantic_type = semantic_type
        self.version = version
        self.description = description
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.tags: list[str] = []
        self.owner: str = "genesis"
        self.lifecycle: str = "active"
        self.security_level: str = "internal"
        self.source: str = ""
        self.generated_by: str = ""
        self._metadata: dict[str, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "semantic_type": self.semantic_type,
            "version": self.version,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": list(self.tags),
            "owner": self.owner,
            "lifecycle": self.lifecycle,
            "security_level": self.security_level,
            "source": self.source,
            "generated_by": self.generated_by,
            "_metadata": dict(self._metadata),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseEntity":
        entity = cls(
            entity_id=data.get("entity_id"),
            name=data.get("name", ""),
            semantic_type=data.get("semantic_type", cls.__name__.lower()),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
        )
        entity.created_at = data.get("created_at", entity.created_at)
        entity.updated_at = data.get("updated_at", entity.updated_at)
        entity.tags = list(data.get("tags", []))
        entity.owner = data.get("owner", "genesis")
        entity.lifecycle = data.get("lifecycle", "active")
        entity.security_level = data.get("security_level", "internal")
        entity.source = data.get("source", "")
        entity.generated_by = data.get("generated_by", "")
        entity._metadata = dict(data.get("_metadata", {}))
        return entity

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def validate(self) -> list[str]:
        errors = []
        if not self.entity_id:
            errors.append("entity_id is required")
        if not self.semantic_type:
            errors.append("semantic_type is required")
        return errors

    def __repr__(self) -> str:
        return f"<{self.semantic_type}:{self.name or self.entity_id}>"


class BaseCapability(BaseEntity):
    """A capability that the platform provides."""

    def __init__(
        self,
        capability_id: str | None = None,
        name: str = "",
        version: str = "0.1.0",
        description: str = "",
    ):
        super().__init__(
            entity_id=capability_id,
            name=name,
            semantic_type="capability",
            version=version,
            description=description,
        )
        self.dependencies: list[str] = []
        self.interfaces: list[dict[str, Any]] = []
        self.inputs: list[dict[str, Any]] = []
        self.outputs: list[dict[str, Any]] = []
        self.contracts: list[dict[str, Any]] = []
        self.policies: list[str] = []
        self.permissions: list[str] = []
        self.validation_rules: list[str] = []
        self.certification_state: str = "uncertified"

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update({
            "dependencies": list(self.dependencies),
            "interfaces": list(self.interfaces),
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "contracts": list(self.contracts),
            "policies": list(self.policies),
            "permissions": list(self.permissions),
            "validation_rules": list(self.validation_rules),
            "certification_state": self.certification_state,
        })
        return base

    def validate(self) -> list[str]:
        errors = super().validate()
        if not self.interfaces:
            errors.append("capability must define at least one interface")
        return errors


class BaseArtifact(BaseEntity):
    """An artifact produced or consumed by the platform."""

    def __init__(
        self,
        artifact_id: str | None = None,
        name: str = "",
        artifact_type: str = "document",
        version: str = "0.1.0",
        description: str = "",
    ):
        super().__init__(
            entity_id=artifact_id,
            name=name,
            semantic_type=f"artifact.{artifact_type}",
            version=version,
            description=description,
        )
        self.artifact_type = artifact_type
        self.format: str = "markdown"
        self.content_hash: str = ""
        self.compiler_version: str = ""
        self.validation_state: str = "unvalidated"
        self.certification: str = "uncertified"

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update({
            "artifact_type": self.artifact_type,
            "format": self.format,
            "content_hash": self.content_hash,
            "compiler_version": self.compiler_version,
            "validation_state": self.validation_state,
            "certification": self.certification,
        })
        return base
