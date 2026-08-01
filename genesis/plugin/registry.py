"""ModulePluginRegistry — lightweight internal engine registry for Genesis modules.

OmegaLoop discovers engines through this registry instead of direct imports.
Each engine registers a factory function; the registry handles lazy instantiation.
"""

from __future__ import annotations

from typing import Any, Callable


class EnginePlugin:
    """A registered engine plugin with its metadata and optional instance."""

    def __init__(
        self,
        name: str,
        plugin_type: str,
        factory: Callable[[], Any] | None = None,
        instance: Any = None,
        description: str = "",
        dependencies: list[str] | None = None,
    ):
        self.name = name
        self.plugin_type = plugin_type
        self.factory = factory
        self._instance = instance
        self.description = description
        self.dependencies = dependencies or []

    @property
    def instance(self) -> Any:
        if self._instance is None and self.factory is not None:
            self._instance = self.factory()
        return self._instance

    def __repr__(self) -> str:
        return f"<EnginePlugin:{self.name}:{self.plugin_type}>"


class ModulePluginRegistry:
    """Lightweight registry for Genesis engine plugins.

    Modules register their engine factories here. OmegaLoop discovers
    engines by type or name rather than importing directly.

    Usage:
        registry = ModulePluginRegistry()
        registry.register("reasoning", "engine", factory=make_reasoning)
        engine = registry.get("reasoning")        # by name
        engines = registry.get_by_type("engine")   # by type
    """

    def __init__(self):
        self._plugins: dict[str, EnginePlugin] = {}

    def register(
        self,
        name: str,
        plugin_type: str,
        *,
        factory: Callable[[], Any] | None = None,
        instance: Any = None,
        description: str = "",
        dependencies: list[str] | None = None,
    ) -> EnginePlugin:
        if name in self._plugins:
            raise KeyError(f"Plugin already registered: {name}")
        plugin = EnginePlugin(
            name=name,
            plugin_type=plugin_type,
            factory=factory,
            instance=instance,
            description=description,
            dependencies=dependencies,
        )
        self._plugins[name] = plugin
        return plugin

    def get(self, name: str) -> Any:
        plugin = self._plugins.get(name)
        if plugin is None:
            raise KeyError(f"No plugin registered: {name}")
        return plugin.instance

    def has(self, name: str) -> bool:
        return name in self._plugins

    def get_by_type(self, plugin_type: str) -> list[EnginePlugin]:
        return [p for p in self._plugins.values() if p.plugin_type == plugin_type]

    def all(self) -> list[EnginePlugin]:
        return list(self._plugins.values())

    def names(self) -> list[str]:
        return list(self._plugins.keys())

    def types(self) -> list[str]:
        return sorted({p.plugin_type for p in self._plugins.values()})

    def to_dict(self) -> dict[str, Any]:
        return {
            name: {
                "type": p.plugin_type,
                "description": p.description,
                "has_instance": p._instance is not None,
                "dependencies": list(p.dependencies),
            }
            for name, p in self._plugins.items()
        }
