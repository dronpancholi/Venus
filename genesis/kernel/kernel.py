"""
Universal Kernel: UniversalKernel — Facade for the entire kernel subsystem.
"""

from __future__ import annotations

from typing import Any

from genesis.kernel.process_manager import ProcessManager
from genesis.kernel.task_scheduler import TaskScheduler
from genesis.kernel.memory_manager import MemoryManager
from genesis.kernel.storage_manager import StorageManager
from genesis.kernel.checkpoint_manager import CheckpointManager
from genesis.kernel.recovery_manager import RecoveryManager
from genesis.kernel.event_router import EventRouter
from genesis.kernel.ipc import IPC
from genesis.kernel.plugin_loader import PluginLoader
from genesis.kernel.capability_loader import CapabilityLoader
from genesis.kernel.di_kernel import DIKernel
from genesis.kernel.resource_manager import ResourceManager
from genesis.kernel.execution_manager import ExecutionManager
from genesis.kernel.health_manager import HealthManager
from genesis.kernel.security_manager import SecurityManager
from genesis.kernel.types import (
    ProcessInfo, ProcessState, TaskInfo, TaskPriority, TaskState,
    MemoryBlock, MemoryScope, StorageVolume, StorageClass,
    Checkpoint, RecoveryPlan, KernelEvent, IPCMessage,
    ResourceReservation, HealthProbe,
)


class UniversalKernel:
    """Unified kernel facade — the foundational execution layer of GENESIS X."""

    def __init__(self, name: str = "UniversalKernel"):
        self.name = name
        self.process = ProcessManager()
        self.task = TaskScheduler()
        self.memory = MemoryManager()
        self.storage = StorageManager()
        self.checkpoint = CheckpointManager()
        self.recovery = RecoveryManager()
        self.events = EventRouter()
        self.ipc = IPC()
        self.plugins = PluginLoader()
        self.di = DIKernel()
        self.resources = ResourceManager()
        self.execution = ExecutionManager()
        self.health = HealthManager()
        self.security = SecurityManager()
        self.capabilities = CapabilityLoader(self.di)

    def boot(self) -> UniversalKernel:
        """Initialize all kernel subsystems."""
        self.events.publish("kernel.boot", {"name": self.name})
        return self

    def shutdown(self):
        """Graceful shutdown of all kernel subsystems."""
        self.events.publish("kernel.shutdown", {"name": self.name})

    def overview(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "process": self.process.summary(),
            "task": self.task.summary(),
            "memory": self.memory.summary(),
            "storage": self.storage.summary(),
            "checkpoint": self.checkpoint.summary(),
            "recovery": self.recovery.summary(),
            "events": self.events.summary(),
            "ipc": self.ipc.summary(),
            "plugins": self.plugins.summary(),
            "di": self.di.summary(),
            "resources": self.resources.summary(),
            "execution": self.execution.summary(),
            "health": self.health.summary(),
            "security": self.security.summary(),
            "capabilities": self.capabilities.summary(),
        }
