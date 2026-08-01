"""
Universal Kernel: Shared types and data models.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class ProcessState(Enum):
    CREATED = "created"
    RUNNING = "running"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    FAILED = "failed"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskState(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MemoryScope(Enum):
    PROCESS = "process"
    CAPABILITY = "capability"
    SHARED = "shared"
    GLOBAL = "global"


class StorageClass(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class EventPriority(Enum):
    LOW = 0
    NORMAL = 5
    HIGH = 10


class IPCChannelType(Enum):
    REQUEST_REPLY = "request_reply"
    PUB_SUB = "pub_sub"
    PUSH_PULL = "push_pull"
    STREAM = "stream"


@dataclass
class ProcessInfo:
    id: str = ""
    name: str = ""
    capability_id: str = ""
    state: ProcessState = ProcessState.CREATED
    pid: int = 0
    memory_bytes: int = 0
    cpu_usage: float = 0.0
    created_at: float = 0.0
    started_at: float = 0.0
    stopped_at: float = 0.0
    exit_code: int = 0
    error: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("proc", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class TaskInfo:
    id: str = ""
    name: str = ""
    capability_id: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    state: TaskState = TaskState.PENDING
    schedule: str = ""
    max_retries: int = 3
    retry_count: int = 0
    timeout_ms: float = 30000.0
    depends_on: list[str] = field(default_factory=list)
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    result: Any = None
    error: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("task", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class MemoryBlock:
    id: str = ""
    capability_id: str = ""
    scope: MemoryScope = MemoryScope.CAPABILITY
    size_bytes: int = 0
    used_bytes: int = 0
    allocated_at: float = 0.0
    last_access: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("mem", 14)
        if not self.allocated_at:
            self.allocated_at = time.time()

    @property
    def utilization(self) -> float:
        return self.used_bytes / max(self.size_bytes, 1)


@dataclass
class StorageVolume:
    id: str = ""
    name: str = ""
    storage_class: StorageClass = StorageClass.HOT
    total_bytes: int = 0
    used_bytes: int = 0
    path: str = ""
    mount_point: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("vol", 14)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def available_bytes(self) -> int:
        return self.total_bytes - self.used_bytes

    @property
    def utilization(self) -> float:
        return self.used_bytes / max(self.total_bytes, 1)


@dataclass
class Checkpoint:
    id: str = ""
    capability_id: str = ""
    state_data: dict[str, Any] = field(default_factory=dict)
    memory_snapshot: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    size_bytes: int = 0
    version: int = 1
    checksum: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ckpt", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class RecoveryPlan:
    id: str = ""
    capability_id: str = ""
    strategy: str = "restart"
    checkpoint_id: str = ""
    max_attempts: int = 3
    attempt: int = 0
    created_at: float = 0.0
    executed_at: float = 0.0
    status: str = "pending"

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("rec", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class KernelEvent:
    id: str = ""
    type: str = ""
    source: str = ""
    target: str = ""
    priority: EventPriority = EventPriority.NORMAL
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    ttl_ms: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("evt", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class IPCMessage:
    id: str = ""
    channel: str = ""
    sender: str = ""
    recipient: str = ""
    channel_type: IPCChannelType = IPCChannelType.REQUEST_REPLY
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    created_at: float = 0.0
    ttl_ms: float = 5000.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ipc", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class ResourceReservation:
    id: str = ""
    capability_id: str = ""
    cpu_cores: float = 0.0
    memory_mb: int = 0
    storage_mb: int = 0
    network_mbps: float = 0.0
    gpu_cores: float = 0.0
    priority: int = 0
    created_at: float = 0.0
    expires_at: float = 0.0
    status: str = "active"

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("rsrc", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class DiServiceRegistration:
    id: str = ""
    interface: str = ""
    implementation: str = ""
    instance: Any = None
    singleton: bool = True
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("di", 14)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class HealthProbe:
    id: str = ""
    capability_id: str = ""
    probe_type: str = "http"
    endpoint: str = ""
    interval_ms: float = 30000.0
    timeout_ms: float = 5000.0
    healthy: bool = True
    last_check: float = 0.0
    last_response_ms: float = 0.0
    consecutive_failures: int = 0
    threshold: int = 3

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("probe", 14)
