"""
VENUS-II-DI-CON-01: ServiceProvider — Dependency Injection Container

Normative References:
  - VPS Part V §5.1: Runtime Structure
  - GENESIS_II_ARCHITECTURE §3.2: ServiceProvider
  - ADR-003: Protocol-based DI instead of ABCs

Purpose:
  Single source of truth for all Venus platform services.
  Provides lazy initialization, singleton scoping, lifecycle hooks,
  and testability via mock injection.

Design Decisions:
  - Services are registered by interface type, resolved by interface type
  - Default scope is singleton (one instance per service per provider)
  - Default initialization is lazy (created on first get())
  - register_instance() enables test mock injection
  - shutdown() provides graceful lifecycle termination
"""

from __future__ import annotations

import threading
from typing import Any, Callable


class ServiceDefinition:
    """Metadata about a registered service."""

    def __init__(
        self,
        interface: type,
        implementation: type,
        singleton: bool = True,
        lazy: bool = True,
    ):
        self.interface = interface
        self.implementation = implementation
        self.singleton = singleton
        self.lazy = lazy
        self.initialized = False
        self._lock = threading.Lock()


class ServiceProvider:
    """
    Dependency injection container for Venus platform services.

    Usage:
        provider = ServiceProvider()
        provider.register(GraphService, UnifiedGraphEngine)
        provider.register(CompilerService, Compiler)

        # Later:
        graph = provider.get(GraphService)
        compiler = provider.get(CompilerService)

    Thread Safety:
        get() is thread-safe for singleton services. Non-singleton services
        create a new instance on every call and require external synchronization.
    """

    _default_instance: ServiceProvider | None = None
    _default_lock = threading.Lock()

    def __init__(self):
        self._registry: dict[type, ServiceDefinition] = {}
        self._instances: dict[type, Any] = {}
        self._lock = threading.Lock()
        self._shutdown_hooks: list[Callable[[], None]] = []

    # ── Registration ────────────────────────────────────────────

    def register(
        self,
        interface: type,
        implementation: type,
        singleton: bool = True,
        lazy: bool = True,
    ):
        """
        Register a service implementation for an interface.

        NORMATIVE: All services must be registered before first use.
        Registration declares name, interface, and lifecycle scope.
        """
        if interface in self._registry:
            raise ValueError(f"Service already registered for interface: {interface.__name__}")
        self._registry[interface] = ServiceDefinition(
            interface=interface,
            implementation=implementation,
            singleton=singleton,
            lazy=lazy,
        )

    def register_instance(self, interface: type, instance: Any):
        """
        Register a pre-created instance (for testing — inject mocks directly).

        NORMATIVE: register_instance bypasses lazy initialization.
        The instance is stored immediately and returned on get().
        """
        with self._lock:
            if interface not in self._registry:
                self._registry[interface] = ServiceDefinition(
                    interface=interface,
                    implementation=type(instance),
                    singleton=True,
                    lazy=False,
                )
            self._instances[interface] = instance
            self._registry[interface].initialized = True

    # ── Resolution ──────────────────────────────────────────────

    def get(self, interface: type) -> Any:
        """
        Resolve a service by interface type.

        Returns the singleton instance (if registered as singleton)
        or creates a new instance (if registered as non-singleton).
        """
        definition = self._registry.get(interface)
        if definition is None:
            raise KeyError(f"No service registered for interface: {interface.__name__}")

        if definition.singleton:
            return self._get_singleton(interface, definition)
        return self._create_instance(interface, definition)

    def _get_singleton(self, interface: type, definition: ServiceDefinition) -> Any:
        """Thread-safe singleton access with lazy initialization."""
        if not definition.initialized:
            with definition._lock:
                if not definition.initialized:
                    instance = self._create_instance(interface, definition)
                    self._instances[interface] = instance
                    definition.initialized = True
        return self._instances[interface]

    def _create_instance(self, interface: type, definition: ServiceDefinition) -> Any:
        """Create a new service instance, injecting the provider if the constructor accepts it."""
        impl = definition.implementation
        try:
            # Try constructor with provider injection
            return impl(provider=self)
        except TypeError:
            # Fall back to no-argument constructor
            return impl()

    # ── Lifecycle ───────────────────────────────────────────────

    def register_shutdown_hook(self, hook: Callable[[], None]):
        """Register a function to call during shutdown."""
        self._shutdown_hooks.append(hook)

    def initialize_all(self):
        """
        Eager initialization of all registered services.
        Forces creation of all singleton services.
        """
        for interface, definition in self._registry.items():
            if definition.singleton and definition.lazy:
                self.get(interface)

    def shutdown(self):
        """
        Graceful shutdown. Calls all registered shutdown hooks.
        Services are responsible for registering their own cleanup.
        """
        for hook in reversed(self._shutdown_hooks):
            try:
                hook()
            except Exception:
                pass  # Log and continue during shutdown

    # ── Default Instance ────────────────────────────────────────

    @classmethod
    def get_default(cls) -> "ServiceProvider":
        """Return the default ServiceProvider instance (create if needed)."""
        if cls._default_instance is None:
            with cls._default_lock:
                if cls._default_instance is None:
                    cls._default_instance = cls()
        return cls._default_instance

    @classmethod
    def set_default(cls, provider: "ServiceProvider"):
        """Set the default ServiceProvider (for testing)."""
        cls._default_instance = provider

    # ── Inspection ──────────────────────────────────────────────

    def is_registered(self, interface: type) -> bool:
        """Check if a service is registered."""
        return interface in self._registry

    def is_initialized(self, interface: type) -> bool:
        """Check if a service has been initialized."""
        definition = self._registry.get(interface)
        return definition is not None and definition.initialized

    def registered_interfaces(self) -> list[str]:
        """List all registered interface names."""
        return sorted(i.__name__ for i in self._registry)
