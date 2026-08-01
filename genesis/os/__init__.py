"""
Engineering Operating System — persistent runtime for the civilization.

Components:
  - PersistentScheduler: time-based + event-based scheduling
  - PersistentPlanner: goal decomposition into task plans
  - PersistentTaskGraph: DAG of tasks with dependencies
  - DistributedQueue: persistent priority queue
  - AgentRuntime: manages agent lifecycle and execution
  - ResourceAllocator: tracks and allocates compute resources
  - MemoryManager: multi-tier memory hierarchy
  - CheckpointManager: snapshots system state
  - RecoveryManager: restores from failures
  - ObservationManager: collects and stores observations
"""

from genesis.os.scheduler import PersistentScheduler
from genesis.os.planner import PersistentPlanner
from genesis.os.task_graph import PersistentTaskGraph
from genesis.os.queue import DistributedQueue
from genesis.os.agent_runtime import AgentRuntime
from genesis.os.resource_allocator import ResourceAllocator
from genesis.os.memory_manager import MemoryManager
from genesis.os.checkpoint import CheckpointManager
from genesis.os.recovery import RecoveryManager
from genesis.os.observation import ObservationManager
from genesis.os.runtime import AutonomousRuntime, RuntimeStatus, ComponentStatus
from genesis.os.watchers import (
    GitWatcher, FileWatcher, ProcessWatcher,
    WatcherRegistry, WatcherEvent, BaseWatcher,
)

__all__ = [
    "PersistentScheduler", "PersistentPlanner", "PersistentTaskGraph",
    "DistributedQueue", "AgentRuntime", "ResourceAllocator",
    "MemoryManager", "CheckpointManager", "RecoveryManager",
    "ObservationManager",
    "AutonomousRuntime", "RuntimeStatus", "ComponentStatus",
    "GitWatcher", "FileWatcher", "ProcessWatcher",
    "WatcherRegistry", "WatcherEvent", "BaseWatcher",
]
