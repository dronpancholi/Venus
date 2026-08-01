"""Genesis-II Dependency Injection Container — service wiring and lifecycle."""

from .bootstrap import bootstrap
from .container import ServiceProvider
from .interfaces import (
    CapabilityService,
    CheckpointService,
    CompilerService,
    ConfigService,
    DiagnosticsService,
    EventBus,
    ExecutionService,
    GraphService,
    MetadataService,
    PluginService,
    ValidationService,
)

__all__ = [
    "bootstrap",
    "wire_domain_services",
    "ServiceProvider",
    "CheckpointService",
    "CompilerService",
    "ConfigService",
    "DiagnosticsService",
    "EventBus",
    "ExecutionService",
    "GraphService",
    "MetadataService",
    "PluginService",
    "CapabilityService",
    "ValidationService",
]
