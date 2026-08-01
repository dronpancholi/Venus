"""
GENESIS-X Program B: Universal Kernel.

The kernel provides process/task scheduling, memory/storage/checkpoint/recovery
management, event routing, IPC, plugin/capability loading, DI, and
resource/execution/health/security management.
"""

from genesis.kernel.kernel import UniversalKernel
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
    ResourceReservation, HealthProbe, DiServiceRegistration,
)

__all__ = [
    "UniversalKernel",
    "ProcessManager", "TaskScheduler",
    "MemoryManager", "StorageManager",
    "CheckpointManager", "RecoveryManager",
    "EventRouter", "IPC",
    "PluginLoader", "CapabilityLoader",
    "DIKernel", "ResourceManager",
    "ExecutionManager", "HealthManager", "SecurityManager",
    "ProcessInfo", "ProcessState", "TaskInfo", "TaskPriority", "TaskState",
    "MemoryBlock", "MemoryScope", "StorageVolume", "StorageClass",
    "Checkpoint", "RecoveryPlan", "KernelEvent", "IPCMessage",
    "ResourceReservation", "HealthProbe", "DiServiceRegistration",
]
