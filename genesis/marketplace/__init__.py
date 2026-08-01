"""
Marketplace Foundation (Mission 183) — application distribution architecture.

Not an online store. Defines the architecture for:
  - Application manifests
  - Dependencies
  - Capabilities
  - Permissions
  - Versioning
  - Digital signatures
  - Updates
  - Installation
  - Removal
  - Validation

Future-ready. Every app ships with a manifest.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class AppManifest:
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = ""
    entry_point: str = ""
    dependencies: list[dict[str, str]] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    min_platform_version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    signature: str = ""
    manifest_version: str = "1.0"

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)

    @classmethod
    def from_json(cls, raw: str) -> AppManifest:
        return cls(**json.loads(raw))

    @property
    def hash(self) -> str:
        raw = self.to_json()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name:
            errors.append("name is required")
        if not self.version:
            errors.append("version is required")
        if not self.entry_point:
            errors.append("entry_point is required")
        for dep in self.dependencies:
            if "name" not in dep:
                errors.append("dependency missing 'name'")
        return errors


@dataclass
class MarketplacePackage:
    manifest: AppManifest
    package_hash: str = ""
    size_bytes: int = 0
    published_at: float = 0.0
    downloads: int = 0

    def __post_init__(self):
        if not self.published_at:
            self.published_at = time.time()


class MarketplaceRegistry:
    """Registry of installable packages (local catalog, not an online store)."""

    def __init__(self):
        self._packages: dict[str, MarketplacePackage] = {}

    def register(self, pkg: MarketplacePackage):
        errors = pkg.manifest.validate()
        if errors:
            raise ValueError(f"Invalid manifest: {errors}")
        self._packages[pkg.manifest.name] = pkg

    def get(self, name: str) -> MarketplacePackage | None:
        return self._packages.get(name)

    def search(self, query: str) -> list[MarketplacePackage]:
        q = query.lower()
        return [p for p in self._packages.values()
                if q in p.manifest.name.lower() or q in p.manifest.description.lower()]

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": p.manifest.name, "version": p.manifest.version,
             "description": p.manifest.description[:60],
             "capabilities": len(p.manifest.capabilities)}
            for p in self._packages.values()
        ]

    def check_dependencies(self, name: str) -> list[str]:
        pkg = self._packages.get(name)
        if not pkg:
            return ["Package not found"]
        missing: list[str] = []
        for dep in pkg.manifest.dependencies:
            dep_name = dep.get("name")
            if dep_name and dep_name not in self._packages:
                missing.append(dep_name)
        return missing

    def find_updates(self, name: str, current_version: str) -> MarketplacePackage | None:
        pkg = self._packages.get(name)
        if not pkg:
            return None
        if pkg.manifest.version != current_version:
            return pkg
        return None
