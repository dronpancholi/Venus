"""
Real Agent Runtime (Mission 43) — alive, observable, collaborative agents.

Agents execute through a runtime that manages lifecycle, scheduling, messaging,
state, and observability. Users can watch agents work in real time.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from genesis.engineering import EngineeringObject, EngineeringObjectType
from genesis.fabric.events import EngineeringEvent, EventPriority, EventSeverity
from genesis.fabric.kernel import FabricKernel
from genesis.utils.identity import generate_id


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    BLOCKED = "blocked"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentRole(Enum):
    CHIEF_ENGINEER = "chief_engineer"
    PRINCIPAL_ARCHITECT = "principal_architect"
    REPOSITORY_SCIENTIST = "repository_scientist"
    ENGINEERING_RESEARCHER = "engineering_researcher"
    PLANNER = "planner"
    PRODUCT_MANAGER = "product_manager"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    KNOWLEDGE_ENGINEER = "knowledge_engineer"
    DOCUMENTATION_ENGINEER = "documentation_engineer"
    SECURITY_ENGINEER = "security_engineer"
    PERFORMANCE_ENGINEER = "performance_engineer"
    QUALITY_ENGINEER = "quality_engineer"
    TESTING_ENGINEER = "testing_engineer"
    GOVERNANCE_AUDITOR = "governance_auditor"
    MIGRATION_SPECIALIST = "migration_specialist"
    SIMULATION_SCIENTIST = "simulation_scientist"
    ECONOMICS_ANALYST = "economics_analyst"
    REVIEWER = "reviewer"
    RELEASE_ENGINEER = "release_engineer"


@dataclass
class AgentSpec:
    agent_id: str = ""
    role: AgentRole = AgentRole.BACKEND_ENGINEER
    name: str = ""
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    system_prompt: str = ""


@dataclass
class AgentTask:
    task_id: str = ""
    agent_id: str = ""
    objective: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending → running → completed/failed
    started_at: float = 0.0
    completed_at: float = 0.0
    result: Any = None
    error: str = ""

    @property
    def duration_ms(self) -> float:
        if self.started_at == 0:
            return 0.0
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000


@dataclass
class AgentMessage:
    id: str = ""
    sender_id: str = ""
    recipient_id: str = ""
    content: str = ""
    message_type: str = "text"  # text, request, response, debate, vote, approval
    correlation_id: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("amsg", 12)
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class AgentDebugInfo:
    agent_id: str = ""
    status: str = ""
    current_task: str = ""
    task_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    uptime_seconds: float = 0.0
    inbox_count: int = 0
    memory_size: int = 0
    spawned_agents: list[str] = field(default_factory=list)


class AgentContext:
    """Private context for a single agent — memory, state, workspace."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._memory: dict[str, Any] = {}
        self._workspace: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._created_at = time.time()

    def remember(self, key: str, value: Any):
        with self._lock:
            self._memory[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._memory.get(key, default)

    def store_workspace(self, key: str, value: Any):
        with self._lock:
            self._workspace[key] = value

    def read_workspace(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._workspace.get(key, default)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._memory) + len(self._workspace)

    @property
    def age_seconds(self) -> float:
        return time.time() - self._created_at


class AgentRuntime:
    """Runtime that manages agent lifecycle, execution, and communication."""

    def __init__(self, kernel: FabricKernel | None = None):
        self._kernel = kernel or FabricKernel.instance()
        self._agents: dict[str, "AgentInstance"] = {}
        self._contexts: dict[str, AgentContext] = {}
        self._inboxes: dict[str, list[AgentMessage]] = defaultdict(list)
        self._outboxes: dict[str, list[AgentMessage]] = defaultdict(list)
        self._lock = threading.RLock()
        self._running = False

    def spawn(self, spec: AgentSpec) -> str:
        agent_id = spec.agent_id or generate_id("agent", 12)
        spec.agent_id = agent_id
        with self._lock:
            agent = AgentInstance(agent_id=agent_id, spec=spec, runtime=self)
            self._agents[agent_id] = agent
            self._contexts[agent_id] = AgentContext(agent_id)
        self._kernel.emit("agent.spawned", {
            "agent_id": agent_id, "role": spec.role.value, "name": spec.name,
        }, origin="agent_runtime", tags=["agent"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_agent({
                "agent_id": agent_id, "role": spec.role.value,
                "name": spec.name, "description": spec.description,
                "capabilities": spec.capabilities,
                "max_concurrent_tasks": spec.max_concurrent_tasks,
                "system_prompt": spec.system_prompt,
                "status": "idle", "task_count": 0,
                "completed_count": 0, "failed_count": 0,
                "created_at": agent._created_at, "metadata": {},
            })
        eng_obj = EngineeringObject(
            id=agent_id,
            object_type=EngineeringObjectType.AGENT,
            name=spec.name or spec.role.value,
            description=spec.description,
            tags=spec.capabilities + [spec.role.value],
            owner="system",
            metadata={"role": spec.role.value, "max_concurrent_tasks": spec.max_concurrent_tasks},
        )
        self._kernel.engineering.register(eng_obj)
        return agent_id

    def terminate(self, agent_id: str):
        with self._lock:
            agent = self._agents.get(agent_id)
            if agent:
                agent.status = AgentStatus.TERMINATED
                del self._agents[agent_id]
                self._contexts.pop(agent_id, None)
        self._kernel.emit("agent.terminated", {"agent_id": agent_id}, origin="agent_runtime", tags=["agent"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.delete_agent(agent_id)

    def get_agent(self, agent_id: str) -> "AgentInstance | None":
        return self._agents.get(agent_id)

    def get_context(self, agent_id: str) -> AgentContext | None:
        return self._contexts.get(agent_id)

    def send_message(self, sender_id: str, recipient_id: str, content: str,
                     message_type: str = "text", correlation_id: str = "",
                     metadata: dict[str, Any] | None = None) -> AgentMessage:
        msg = AgentMessage(
            sender_id=sender_id, recipient_id=recipient_id, content=content,
            message_type=message_type, correlation_id=correlation_id,
            metadata=metadata or {},
        )
        with self._lock:
            self._inboxes[recipient_id].append(msg)
            self._outboxes[sender_id].append(msg)
        self._kernel.emit("agent.message.sent", {
            "sender": sender_id, "recipient": recipient_id, "type": message_type,
        }, origin="agent_runtime", tags=["agent", "message"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_message({
                "id": msg.id, "sender_id": sender_id,
                "recipient_id": recipient_id, "content": content,
                "message_type": message_type,
                "correlation_id": correlation_id,
                "timestamp": msg.timestamp,
                "metadata": metadata or {},
            })
        return msg

    def read_inbox(self, agent_id: str) -> list[AgentMessage]:
        with self._lock:
            msgs = list(self._inboxes.get(agent_id, []))
            self._inboxes[agent_id] = []
        return msgs

    def read_outbox(self, agent_id: str) -> list[AgentMessage]:
        with self._lock:
            return list(self._outboxes.get(agent_id, []))

    def list_agents(self) -> list["AgentInstance"]:
        return list(self._agents.values())

    def get_debug_info(self, agent_id: str) -> AgentDebugInfo | None:
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return None
            ctx = self._contexts.get(agent_id)
            return AgentDebugInfo(
                agent_id=agent_id, status=agent.status.value,
                current_task=agent._current_task_id or "",
                task_count=agent._task_count,
                completed_count=agent._completed_count,
                failed_count=agent._failed_count,
                uptime_seconds=(time.time() - agent._created_at) if agent._created_at else 0,
                inbox_count=len(self._inboxes.get(agent_id, [])),
                memory_size=ctx.size if ctx else 0,
            )

    def summary(self) -> dict[str, Any]:
        agents = self.list_agents()
        by_status: dict[str, int] = defaultdict(int)
        for a in agents:
            by_status[a.status.value] += 1
        return {
            "total_agents": len(agents),
            "by_status": dict(by_status),
            "total_messages": sum(len(v) for v in self._outboxes.values()),
        }


class AgentInstance:
    """A living agent running in the runtime."""

    def __init__(self, agent_id: str, spec: AgentSpec, runtime: AgentRuntime):
        self.agent_id = agent_id
        self.spec = spec
        self._runtime = runtime
        self.status = AgentStatus.IDLE
        self._current_task_id: str = ""
        self._task_count = 0
        self._completed_count = 0
        self._failed_count = 0
        self._created_at = time.time()
        self._handler: Callable[[AgentTask], Any] | None = None

    def register_handler(self, handler: Callable[[AgentTask], Any]):
        self._handler = handler

    def assign_task(self, objective: str, context: dict[str, Any] | None = None) -> AgentTask:
        task = AgentTask(
            task_id=generate_id("atask", 12),
            agent_id=self.agent_id,
            objective=objective,
            context=context or {},
        )
        self._current_task_id = task.task_id
        self.status = AgentStatus.RUNNING
        task.started_at = time.time()
        self._task_count += 1
        self._runtime._kernel.emit("agent.task.assigned", {
            "agent_id": self.agent_id, "task_id": task.task_id, "objective": objective,
        }, origin=self.agent_id, tags=["agent", "task"])
        if self._runtime._kernel.storage and self._runtime._kernel.storage.connected:
            self._runtime._kernel.storage.store_agent_task({
                "task_id": task.task_id, "agent_id": self.agent_id,
                "objective": objective, "context": context or {},
                "status": "running", "started_at": task.started_at,
                "completed_at": 0, "result": None, "error": "",
                "created_at": time.time(),
            })
        return task

    def complete_task(self, task: AgentTask, result: Any = None):
        task.status = "completed"
        task.completed_at = time.time()
        task.result = result
        self._current_task_id = ""
        self._completed_count += 1
        self.status = AgentStatus.IDLE
        self._runtime._kernel.emit("agent.task.completed", {
            "agent_id": self.agent_id, "task_id": task.task_id,
            "duration_ms": task.duration_ms,
        }, origin=self.agent_id, tags=["agent", "task"])
        if self._runtime._kernel.storage and self._runtime._kernel.storage.connected:
            self._runtime._kernel.storage.store_agent_task({
                "task_id": task.task_id, "agent_id": self.agent_id,
                "objective": task.objective, "context": task.context,
                "status": "completed", "started_at": task.started_at,
                "completed_at": task.completed_at,
                "result": {"data": result} if result is not None else None,
                "error": "", "created_at": time.time(),
            })

    def fail_task(self, task: AgentTask, error: str = ""):
        task.status = "failed"
        task.completed_at = time.time()
        task.error = error
        self._current_task_id = ""
        self._failed_count += 1
        self.status = AgentStatus.ERROR
        self._runtime._kernel.emit("agent.task.failed", {
            "agent_id": self.agent_id, "task_id": task.task_id, "error": error,
        }, origin=self.agent_id, severity=EventSeverity.ERROR, tags=["agent", "task"])
        if self._runtime._kernel.storage and self._runtime._kernel.storage.connected:
            self._runtime._kernel.storage.store_agent_task({
                "task_id": task.task_id, "agent_id": self.agent_id,
                "objective": task.objective, "context": task.context,
                "status": "failed", "started_at": task.started_at,
                "completed_at": task.completed_at,
                "result": None, "error": error,
                "created_at": time.time(),
            })

    def send(self, recipient_id: str, content: str, message_type: str = "text") -> AgentMessage:
        return self._runtime.send_message(self.agent_id, recipient_id, content, message_type)

    def read_messages(self) -> list[AgentMessage]:
        return self._runtime.read_inbox(self.agent_id)

    def debug(self) -> AgentDebugInfo | None:
        return self._runtime.get_debug_info(self.agent_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.spec.role.value,
            "name": self.spec.name,
            "status": self.status.value,
            "task_count": self._task_count,
            "completed_count": self._completed_count,
            "failed_count": self._failed_count,
            "capabilities": self.spec.capabilities,
        }


class AgentScheduler:
    """Schedules periodic or delayed agent tasks."""

    def __init__(self, runtime: AgentRuntime):
        self._runtime = runtime
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def schedule_task(self, agent_id: str, objective: str,
                      delay_secs: float = 0, interval_secs: float = 0,
                      context: dict[str, Any] | None = None) -> str:
        tid = generate_id("sched", 12)
        with self._lock:
            self._tasks[tid] = {
                "agent_id": agent_id, "objective": objective,
                "delay_secs": delay_secs, "interval_secs": interval_secs,
                "context": context or {}, "next_run": time.time() + delay_secs,
                "active": True,
            }
        return tid

    def cancel_task(self, task_id: str):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["active"] = False

    def tick(self):
        now = time.time()
        with self._lock:
            for tid, t in list(self._tasks.items()):
                if not t["active"]:
                    continue
                if now >= t["next_run"]:
                    agent = self._runtime.get_agent(t["agent_id"])
                    if agent:
                        task = agent.assign_task(t["objective"], t["context"])
                        try:
                            result = (agent._handler or self._default_handler)(task)
                            agent.complete_task(task, result)
                        except Exception as e:
                            agent.fail_task(task, str(e))
                    if t["interval_secs"] > 0:
                        t["next_run"] = now + t["interval_secs"]
                    else:
                        t["active"] = False

    def _default_handler(self, task: AgentTask) -> str:
        return f"[simulated] completed: {task.objective[:60]}"
