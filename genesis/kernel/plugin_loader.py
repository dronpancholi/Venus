"""
Universal Kernel: PluginLoader — Dynamic plugin discovery and loading.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


class PluginLoader:
    """Discovers and loads plugins from modules and directories."""

    def __init__(self):
        self._plugins: dict[str, dict[str, Any]] = {}
        self._hooks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._load_history: list[dict[str, Any]] = []

    def load_module(self, module_name: str) -> dict[str, Any] | None:
        try:
            module = importlib.import_module(module_name)
            plugin_info = {
                "id": generate_id("plug", 10),
                "name": module_name,
                "module": module,
                "loaded_at": time.time(),
                "functions": [],
                "classes": [],
            }
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj):
                    plugin_info["functions"].append(name)
                elif inspect.isclass(obj):
                    plugin_info["classes"].append(name)
            self._plugins[module_name] = plugin_info
            self._load_history.append({
                "action": "load_module",
                "module": module_name,
                "timestamp": time.time(),
            })
            return plugin_info
        except Exception as e:
            self._load_history.append({
                "action": "load_module_failed",
                "module": module_name,
                "error": str(e),
                "timestamp": time.time(),
            })
            return None

    def load_directory(self, directory: str) -> list[dict[str, Any]]:
        loaded = []
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return loaded
        for importer, module_name, is_pkg in pkgutil.iter_modules([str(path)]):
            info = self.load_module(module_name)
            if info:
                loaded.append(info)
        return loaded

    def register_hook(self, hook_name: str, handler: Callable,
                       plugin_id: str = "") -> str:
        hook_id = generate_id("hook", 10)
        self._hooks[hook_name].append({
            "id": hook_id,
            "plugin_id": plugin_id,
            "handler": handler,
            "registered_at": time.time(),
        })
        return hook_id

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        results = []
        for hook in self._hooks.get(hook_name, []):
            try:
                result = hook["handler"](*args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(e)
        return results

    def get_plugin(self, name: str) -> dict[str, Any] | None:
        return self._plugins.get(name)

    def loaded_plugins(self) -> list[dict[str, Any]]:
        return list(self._plugins.values())

    def unload(self, module_name: str) -> bool:
        return self._plugins.pop(module_name, None) is not None

    def summary(self) -> dict[str, Any]:
        return {
            "loaded": len(self._plugins),
            "hooks": sum(len(h) for h in self._hooks.values()),
            "hook_types": len(self._hooks),
            "total_operations": len(self._load_history),
        }
