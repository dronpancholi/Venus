"""Plugin manifest schema and validation."""

import json
from pathlib import Path
from typing import Any


class PluginManifest:
    """Plugin manifest defining metadata, dependencies, capabilities, and hooks."""

    REQUIRED_FIELDS = ["name", "version", "entry_point"]

    def __init__(
        self,
        name: str,
        version: str,
        entry_point: str,
        description: str = "",
        author: str = "",
    ):
        self.name = name
        self.version = version
        self.entry_point = entry_point
        self.description = description
        self.author = author
        self.dependencies: list[dict[str, str]] = []
        self.capabilities: list[str] = []
        self.schemas: list[str] = []
        self.commands: list[dict[str, Any]] = []
        self.hooks: dict[str, list[str]] = {
            "runtime": [],
            "validation": [],
            "memory": [],
            "compiler": [],
        }
        self.permissions: list[str] = []
        self.metadata: dict[str, Any] = {}

    def add_dependency(self, name: str, version: str = "*", optional: bool = False):
        self.dependencies.append({"name": name, "version": version, "optional": optional})

    def add_hook(self, hook_type: str, handler: str):
        if hook_type in self.hooks:
            self.hooks[hook_type].append(handler)

    def add_command(self, name: str, handler: str, description: str = ""):
        self.commands.append({"name": name, "handler": handler, "description": description})

    def validate(self) -> list[str]:
        errors = []
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field, None):
                errors.append(f"missing required field: {field}")
        if self.dependencies:
            for dep in self.dependencies:
                if "name" not in dep:
                    errors.append(f"dependency missing name: {dep}")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "entry_point": self.entry_point,
            "description": self.description,
            "author": self.author,
            "dependencies": list(self.dependencies),
            "capabilities": list(self.capabilities),
            "schemas": list(self.schemas),
            "commands": list(self.commands),
            "hooks": dict(self.hooks),
            "permissions": list(self.permissions),
            "metadata": dict(self.metadata),
        }

    def to_yaml(self) -> str:
        lines = [
            f"name: {self.name}",
            f"version: {self.version}",
            f"entry_point: {self.entry_point}",
            f"description: {self.description or ''}",
            f"author: {self.author or ''}",
        ]
        if self.dependencies:
            lines.append("dependencies:")
            for dep in self.dependencies:
                opt = ", optional: true" if dep.get("optional") else ""
                lines.append(f"  - name: {dep['name']}, version: {dep.get('version', '*')}{opt}")
        if self.capabilities:
            lines.append(f"capabilities: [{', '.join(self.capabilities)}]")
        if self.commands:
            lines.append("commands:")
            for cmd in self.commands:
                lines.append(f"  - name: {cmd['name']}, handler: {cmd['handler']}")
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginManifest":
        manifest = cls(
            name=data.get("name", ""),
            version=data.get("version", "0.1.0"),
            entry_point=data.get("entry_point", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
        )
        manifest.dependencies = list(data.get("dependencies", []))
        manifest.capabilities = list(data.get("capabilities", []))
        manifest.schemas = list(data.get("schemas", []))
        manifest.commands = list(data.get("commands", []))
        manifest.hooks.update(data.get("hooks", {}))
        manifest.permissions = list(data.get("permissions", []))
        manifest.metadata = dict(data.get("metadata", {}))
        return manifest

    @classmethod
    def load(cls, path: str | Path) -> "PluginManifest":
        raw = Path(path).read_text()
        if path.endswith(".json"):
            data = json.loads(raw)
        else:
            import yaml
            data = yaml.safe_load(raw)
        return cls.from_dict(data)
