"""
Universal Kernel: DIKernel — Lightweight dependency injection container.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import DiServiceRegistration


class DIKernel:
    """Dependency injection container for capability services."""

    def __init__(self):
        self._services: dict[str, DiServiceRegistration] = {}
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}

    def register(self, interface: str, implementation: Any = None,
                 factory: Callable | None = None,
                 singleton: bool = True, tags: list[str] | None = None) -> DiServiceRegistration:
        if implementation is None and factory is None:
            raise ValueError("Either implementation or factory must be provided")
        reg = DiServiceRegistration(
            interface=interface,
            implementation=implementation.__class__.__name__ if implementation else factory.__name__,
            singleton=singleton,
            tags=tags or [],
        )
        self._services[interface] = reg
        if implementation is not None and singleton:
            self._instances[interface] = implementation
        if factory is not None:
            self._factories[interface] = factory
        return reg

    def resolve(self, interface: str) -> Any:
        if interface in self._instances:
            return self._instances[interface]
        reg = self._services.get(interface)
        if not reg:
            return None
        if reg.singleton:
            if interface in self._factories:
                self._instances[interface] = self._factories[interface]()
                return self._instances[interface]
            return self._instances.get(interface)
        if interface in self._factories:
            return self._factories[interface]()
        return None

    def register_instance(self, interface: str, instance: Any):
        self._instances[interface] = instance
        if interface not in self._services:
            self._services[interface] = DiServiceRegistration(
                interface=interface,
                implementation=instance.__class__.__name__,
                singleton=True,
            )

    def register_factory(self, interface: str, factory: Callable, singleton: bool = True):
        reg = DiServiceRegistration(
            interface=interface,
            implementation=factory.__name__,
            singleton=singleton,
            tags=[],
        )
        self._services[interface] = reg
        self._factories[interface] = factory

    def has(self, interface: str) -> bool:
        return interface in self._services or interface in self._instances

    def unregister(self, interface: str) -> bool:
        self._instances.pop(interface, None)
        self._factories.pop(interface, None)
        return self._services.pop(interface, None) is not None

    def find_by_tag(self, tag: str) -> list[DiServiceRegistration]:
        return [r for r in self._services.values() if tag in r.tags]

    def clear(self):
        self._services.clear()
        self._instances.clear()
        self._factories.clear()

    def summary(self) -> dict[str, Any]:
        return {
            "services": len(self._services),
            "instances": len(self._instances),
            "factories": len(self._factories),
            "interfaces": list(self._services.keys()),
        }
