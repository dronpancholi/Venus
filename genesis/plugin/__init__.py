"""Plugin Architecture — installable everything: manager, sandbox, lifecycle, manifest, registry."""

from .manager import PluginManager
from .manifest import PluginManifest
from .registry import ModulePluginRegistry, EnginePlugin

__all__ = ["PluginManager", "PluginManifest", "ModulePluginRegistry", "EnginePlugin"]
