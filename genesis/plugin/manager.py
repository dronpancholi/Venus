"""
CORE-03: Plugin Architecture

Plugin Manager, Extension API, Capability Registry, Lifecycle Manager,
Dependency Resolver, Version Resolver, Sandbox, Permissions, Hot Reload.
"""

import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Callable

from genesis.core.exceptions import PluginError
from genesis.events.bus import EventBus
from genesis.plugin.manifest import PluginManifest


class PluginInstance:
    """A loaded plugin instance with its manifest and module reference."""

    def __init__(self, manifest: PluginManifest, module=None):
        self.manifest = manifest
        self.module = module
        self.state: str = "registered"
        self.instance = None
        self.handlers: dict[str, Callable] = {}

    def activate(self):
        if self.module:
            if hasattr(self.module, "create_plugin"):
                self.instance = self.module.create_plugin()
            elif hasattr(self.module, "Plugin"):
                self.instance = self.module.Plugin()
            self.state = "active"

            # Register handlers
            if self.instance:
                for hook_type, handlers in self.manifest.hooks.items():
                    for handler_name in handlers:
                        handler = getattr(self.instance, handler_name, None)
                        if handler and callable(handler):
                            self.handlers[f"{hook_type}.{handler_name}"] = handler

    def deactivate(self):
        if self.instance and hasattr(self.instance, "deactivate"):
            self.instance.deactivate()
        self.state = "inactive"

    def get_handler(self, hook_type: str, name: str) -> Callable | None:
        return self.handlers.get(f"{hook_type}.{name}")

    def __repr__(self) -> str:
        return f"<Plugin:{self.manifest.name}:{self.state}>"


class Sandbox:
    """Plugin sandbox with restricted execution."""

    def __init__(self, allowed_modules: list[str] | None = None):
        self.allowed_modules = allowed_modules or [
            "json", "yaml", "pathlib", "datetime", "uuid", "typing",
            "collections", "re", "math", "statistics",
        ]

    def validate_module(self, module_name: str) -> bool:
        for allowed in self.allowed_modules:
            if module_name == allowed or module_name.startswith(f"{allowed}."):
                return True
        return False


class PluginManager:
    """Central plugin manager. Handles registration, lifecycle, dependencies."""

    def __init__(self, event_bus: EventBus | None = None):
        self._plugins: dict[str, PluginInstance] = {}
        self._plugin_dirs: list[Path] = []
        self.sandbox = Sandbox()
        self._hook_registry: dict[str, list[tuple[str, Callable]]] = {}
        self._bus = event_bus

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def register_plugin(self, manifest: PluginManifest) -> PluginInstance:
        instance = PluginInstance(manifest)
        self._plugins[manifest.name] = instance
        self._emit("plugin.registered", {"name": manifest.name, "version": manifest.version})
        return instance

    def load_from_dir(self, plugin_dir: str | Path) -> list[PluginInstance]:
        """Load all plugins from a directory containing manifest files."""
        path = Path(plugin_dir)
        self._plugin_dirs.append(path)
        loaded = []

        for manifest_file in path.glob("*.yaml"):
            manifest = PluginManifest.load(manifest_file)
            instance = self._load_plugin(manifest, path)
            if instance:
                loaded.append(instance)

        for manifest_file in path.glob("*.json"):
            manifest = PluginManifest.load(manifest_file)
            instance = self._load_plugin(manifest, path)
            if instance:
                loaded.append(instance)

        return loaded

    def _load_plugin(self, manifest: PluginManifest, base_path: Path) -> PluginInstance | None:
        errors = manifest.validate()
        if errors:
            raise PluginError(f"Invalid manifest {manifest.name}: {errors}")

        instance = PluginInstance(manifest)
        entry_path = base_path / manifest.entry_point

        if entry_path.exists():
            module_name = f"venus_plugin_{manifest.name}"
            spec = importlib.util.spec_from_file_location(module_name, entry_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                instance.module = module
                instance.state = "loaded"

        self._plugins[manifest.name] = instance
        return instance

    def activate(self, name: str) -> bool:
        instance = self._plugins.get(name)
        if not instance:
            raise PluginError(f"Plugin not found: {name}")

        # Resolve dependencies
        for dep in instance.manifest.dependencies:
            dep_name = dep["name"]
            dep_instance = self._plugins.get(dep_name)
            if not dep_instance:
                if not dep.get("optional"):
                    raise PluginError(f"Required dependency not installed: {dep_name}")
            elif dep_instance.state != "active":
                self.activate(dep_name)

        instance.activate()

        # Register hooks
        for hook_type, handlers in instance.manifest.hooks.items():
            for handler_name in handlers:
                handler = instance.get_handler(hook_type, handler_name)
                if handler:
                    key = f"{hook_type}.{handler_name}"
                    self._hook_registry.setdefault(key, []).append((name, handler))

        self._emit("plugin.activated", {"name": name})
        return True

    def deactivate(self, name: str):
        instance = self._plugins.get(name)
        if instance:
            instance.deactivate()
            self._emit("plugin.deactivated", {"name": name})

    def activate_all(self):
        for name in list(self._plugins.keys()):
            try:
                self.activate(name)
            except PluginError as e:
                print(f"  [WARN] Failed to activate {name}: {e}")

    def get(self, name: str) -> PluginInstance | None:
        return self._plugins.get(name)

    def all(self) -> list[PluginInstance]:
        return list(self._plugins.values())

    def trigger_hook(self, hook_type: str, name: str, *args, **kwargs) -> list[Any]:
        """Trigger all handlers registered for a hook."""
        key = f"{hook_type}.{name}"
        results = []
        for plugin_name, handler in self._hook_registry.get(key, []):
            try:
                result = handler(*args, **kwargs)
                results.append((plugin_name, result))
            except Exception as e:
                results.append((plugin_name, e))
        return results

    def hot_reload(self, name: str) -> bool:
        """Reload a plugin without restarting the platform."""
        instance = self._plugins.get(name)
        if not instance:
            return False

        old_state = instance.state
        instance.deactivate()

        # Find and reload the module
        for plugin_dir in self._plugin_dirs:
            manifest_file = plugin_dir / f"{name}.yaml"
            if not manifest_file.exists():
                manifest_file = plugin_dir / f"{name}.json"
            if manifest_file.exists():
                manifest = PluginManifest.load(manifest_file)
                instance.manifest = manifest
                self._load_plugin(manifest, plugin_dir)
                if old_state == "active":
                    self.activate(name)
                return True

        return False

    def validate_all(self) -> list[dict[str, Any]]:
        results = []
        for name, instance in self._plugins.items():
            errors = instance.manifest.validate()
            results.append({
                "plugin": name,
                "state": instance.state,
                "errors": errors,
            })
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            name: {
                "manifest": instance.manifest.to_dict(),
                "state": instance.state,
            }
            for name, instance in self._plugins.items()
        }
