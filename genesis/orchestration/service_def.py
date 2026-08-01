from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ServiceStatus(Enum):
    PENDING = "pending"
    BOOTING = "booting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    SKIPPED = "skipped"


class BootPhase(Enum):
    CONFIG_LOAD = "config_load"
    CONTAINER_BOOT = "container_boot"
    SERVICE_INIT = "service_init"
    HEALTH_VALIDATION = "health_validation"
    RUNTIME_START = "runtime_start"
    SHUTDOWN = "shutdown"


@dataclass
class ServiceDef:
    id: str = ""
    version: str = "1.0.0"
    owner: str = "genesis"
    description: str = ""

    dependencies: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    optional_capabilities: list[str] = field(default_factory=list)

    configuration: dict[str, Any] = field(default_factory=dict)

    factory: Callable[[], Any] | None = None
    instance: Any = None

    health_check: Callable[[Any], bool] | None = None
    startup_hook: Callable[[Any], None] | None = None
    shutdown_hook: Callable[[Any], None] | None = None
    verification_hook: Callable[[Any], bool] | None = None
    rollback_hook: Callable[[Any], None] | None = None

    resource_requirements: dict[str, float] = field(default_factory=lambda: {"memory_mb": 0, "cpu_percent": 0})
    estimated_startup_ms: float = 100.0
    priority: int = 100
    critical: bool = False
    tags: list[str] = field(default_factory=list)
