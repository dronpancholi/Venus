"""
UCOS Core: Capability Model.

Every entity in Genesis is a Capability with identity, semantics, contracts,
dependencies, consumers, providers, permissions, execution policies,
version history, maturity, health, ownership, verification, and metrics.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class CapabilityCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    STORAGE = "storage"
    MEMORY = "memory"
    COGNITIVE = "cognitive"
    KNOWLEDGE = "knowledge"
    COMPILER = "compiler"
    RUNTIME = "runtime"
    SIMULATION = "simulation"
    RESEARCH = "research"
    CIVILIZATION = "civilization"
    EVOLUTION = "evolution"
    INTELLIGENCE = "intelligence"
    ACQUISITION = "acquisition"
    SECURITY = "security"
    VALIDATION = "validation"
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    OBSERVATORY = "observatory"
    MARKETPLACE = "marketplace"
    AGENT = "agent"
    PLATFORM = "platform"
    GRAPH = "graph"
    KERNEL = "kernel"
    COMPILER_INFRA = "compiler_infrastructure"
    DNA = "dna"
    FOUNDATION_MODEL = "foundation_model"


class CapabilityState(Enum):
    DORMANT = "dormant"
    REGISTERED = "registered"
    VERIFIED = "verified"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPED = "stopped"
    OBSOLETE = "obsolete"


class MaturityLevel(Enum):
    PROPOSED = "proposed"
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"
    MATURE = "mature"
    CRITICAL = "critical"
    DEPRECATED = "deprecated"


@dataclass
class CapabilityContract:
    """Input/output contract for a capability."""
    inputs: list[dict[str, Any]] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    error_conditions: list[str] = field(default_factory=list)

    def validate_input(self, data: dict[str, Any]) -> list[str]:
        errors = []
        for inp in self.inputs:
            name = inp.get("name", "")
            required = inp.get("required", False)
            if required and name not in data:
                errors.append(f"Missing required input: {name}")
        return errors

    def validate_output(self, data: dict[str, Any]) -> list[str]:
        errors = []
        for out in self.outputs:
            name = out.get("name", "")
            required = out.get("required", False)
            if required and name not in data:
                errors.append(f"Missing required output: {name}")
        return errors


@dataclass
class CapabilityVersion:
    major: int = 1
    minor: int = 0
    patch: int = 0
    commit_hash: str = ""
    timestamp: float = 0.0
    changelog: str = ""

    @property
    def semver(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0

    def bump_minor(self):
        self.minor += 1
        self.patch = 0

    def bump_patch(self):
        self.patch += 1


@dataclass
class CapabilityHealth:
    healthy: bool = True
    score: float = 1.0
    uptime: float = 0.0
    failure_count: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0
    recovery_count: int = 0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    message: str = ""


@dataclass
class CapabilityPermission:
    capability_id: str = ""
    actions: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    granted_by: str = ""
    granted_at: float = 0.0
    expires_at: float = 0.0


@dataclass
class CapabilityDefinition:
    """Complete definition of a capability."""
    id: str = ""
    name: str = ""
    category: CapabilityCategory = CapabilityCategory.PLATFORM
    description: str = ""
    version: CapabilityVersion = field(default_factory=CapabilityVersion)
    state: CapabilityState = CapabilityState.DORMANT
    maturity: MaturityLevel = MaturityLevel.PROPOSED
    contract: CapabilityContract = field(default_factory=CapabilityContract)
    dependencies: list[str] = field(default_factory=list)
    providers: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)
    permissions: list[CapabilityPermission] = field(default_factory=list)
    execution_policy: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    owner: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0
    health: CapabilityHealth = field(default_factory=CapabilityHealth)
    metrics: dict[str, float] = field(default_factory=dict)
    implementation: Any = None

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("cap", 12)
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def touch(self):
        self.updated_at = time.time()

    def register_consumer(self, consumer_id: str):
        if consumer_id not in self.consumers:
            self.consumers.append(consumer_id)
            self.touch()

    def register_provider(self, provider_id: str):
        if provider_id not in self.providers:
            self.providers.append(provider_id)
            self.touch()

    def has_permission(self, action: str, role: str = "") -> bool:
        for p in self.permissions:
            if action in p.actions:
                if not role or role in p.roles:
                    if p.expires_at == 0 or time.time() < p.expires_at:
                        return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "version": self.version.semver,
            "state": self.state.value,
            "maturity": self.maturity.value,
            "dependencies": list(self.dependencies),
            "providers": list(self.providers),
            "consumers": list(self.consumers),
            "tags": list(self.tags),
            "owner": self.owner,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "health": {
                "healthy": self.health.healthy,
                "score": self.health.score,
                "uptime": self.health.uptime,
                "error_rate": self.health.error_rate,
            },
        }

    def clone(self, new_id: str | None = None) -> CapabilityDefinition:
        return CapabilityDefinition(
            id=new_id or generate_id("cap", 12),
            name=self.name,
            category=self.category,
            description=self.description,
            version=CapabilityVersion(
                major=self.version.major,
                minor=self.version.minor,
                patch=self.version.patch,
            ),
            maturity=self.maturity,
            contract=self.contract,
            dependencies=list(self.dependencies),
            tags=list(self.tags),
            owner=self.owner,
        )


class Capability:
    """Runtime wrapper around a CapabilityDefinition with execution context."""

    def __init__(self, *args, **kwargs):
        self._context: dict[str, Any] = {}
        self._started_at: float = 0.0
        self._execution_count: int = 0
        self._last_execution: float = 0.0
        self._total_execution_time: float = 0.0

        if args and isinstance(args[0], CapabilityDefinition):
            self._definition = args[0]
            self._implementation = args[1] if len(args) > 1 else kwargs.get("implementation")
            return

        id_val = args[0] if args else kwargs.get("id", "")
        name_val = args[1] if len(args) > 1 else kwargs.get("name", "")
        implementation = kwargs.get("implementation")

        definition_kwargs: dict[str, Any] = {"id": id_val, "name": name_val}
        for key, value in kwargs.items():
            if key.startswith("definition__"):
                attr_name = key.replace("definition__", "")
                definition_kwargs[attr_name] = value
            elif key == "implementation":
                implementation = value

        self._definition = CapabilityDefinition(**definition_kwargs)
        self._implementation = implementation

    @property
    def id(self) -> str:
        return self._definition.id

    @property
    def name(self) -> str:
        return self._definition.name

    @property
    def definition(self) -> CapabilityDefinition:
        return self._definition

    @property
    def state(self) -> CapabilityState:
        return self._definition.state

    @state.setter
    def state(self, value: CapabilityState):
        self._definition.state = value

    @property
    def is_running(self) -> bool:
        return self._definition.state == CapabilityState.RUNNING

    @property
    def is_ready(self) -> bool:
        return self._definition.state == CapabilityState.READY

    @property
    def execution_count(self) -> int:
        return self._execution_count

    @property
    def avg_execution_time(self) -> float:
        if self._execution_count == 0:
            return 0.0
        return self._total_execution_time / self._execution_count

    def start(self):
        self._definition.state = CapabilityState.RUNNING
        self._started_at = time.time()
        self._definition.health.uptime = 0.0

    def stop(self):
        self._definition.state = CapabilityState.STOPPED
        if self._started_at > 0:
            self._definition.health.uptime += time.time() - self._started_at
        self._started_at = 0.0

    def execute(self, **kwargs) -> Any:
        if not self._implementation:
            return None
        self._execution_count += 1
        start = time.time()
        try:
            result = self._implementation(**kwargs)
            elapsed = time.time() - start
            self._total_execution_time += elapsed
            self._last_execution = time.time()
            self._definition.health.last_success = time.time()
            self._definition.health.response_time_ms = elapsed * 1000
            self._definition.health.healthy = True
            return result
        except Exception as e:
            elapsed = time.time() - start
            self._total_execution_time += elapsed
            self._definition.health.failure_count += 1
            self._definition.health.last_failure = time.time()
            self._definition.health.healthy = False
            self._definition.health.message = str(e)
            raise

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "execution_count": self._execution_count,
            "avg_execution_time_ms": self.avg_execution_time * 1000,
            "health": {
                "healthy": self._definition.health.healthy,
                "score": self._definition.health.score,
                "error_rate": self._definition.health.error_rate,
            },
        }
