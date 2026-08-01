"""
Multi-Agent Orchestration — coordinate multiple agents for complex tasks.

Manages agent lifecycle: registration, task assignment, execution monitoring,
result collection, and failure recovery. Supports hierarchical agent teams,
recursive task decomposition, and inter-agent communication.

Integrates with: GoalHierarchy (agent goals), StrategyEngine (tool selection),
WorkingMemory (agent status), EpisodicMemory (agent actions),
EngineeringBrain (agent entities).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    BLOCKED = "blocked"
    ERROR = "error"
    TERMINATED = "terminated"


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CognitiveAgent:
    """An agent in the cognitive architecture."""
    id: str = ""
    name: str = ""
    agent_type: str = ""          # researcher, planner, implementer, reviewer, etc.
    capabilities: list[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: str = ""
    task_history: list[str] = field(default_factory=list)
    parent_agent_id: str = ""
    child_agent_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("agent", 10)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def is_available(self) -> bool:
        return self.status == AgentStatus.IDLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "current_task_id": self.current_task_id,
            "parent_agent_id": self.parent_agent_id,
            "child_agent_ids": self.child_agent_ids,
        }


@dataclass
class AgentTask:
    """A task assigned to an agent."""
    id: str = ""
    description: str = ""
    agent_id: str = ""
    parent_task_id: str = ""
    sub_task_ids: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5              # 1 (highest) to 10 (lowest)
    required_capabilities: list[str] = field(default_factory=list)
    result: Any = None
    error: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    max_retries: int = 3
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("task", 12)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def duration(self) -> float:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0.0


class Orchestrator:
    """Multi-agent orchestration for complex task decomposition and execution.

    Supports:
    - Agent registration and capability-based assignment
    - Recursive task decomposition (parent tasks → sub-tasks)
    - Priority-based scheduling
    - Failure detection and retry
    - Hierarchical agent teams
    """

    def __init__(self):
        self._agents: dict[str, CognitiveAgent] = {}
        self._tasks: dict[str, AgentTask] = {}
        self._pending_queue: list[str] = []  # Task IDs sorted by priority
        self._completion_handlers: dict[str, list[Callable]] = {}

    @property
    def agent_count(self) -> int:
        return len(self._agents)

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    def register_agent(self, name: str, agent_type: str = "",
                        capabilities: list[str] | None = None,
                        parent_id: str = "") -> CognitiveAgent:
        agent = CognitiveAgent(
            name=name,
            agent_type=agent_type,
            capabilities=capabilities or [],
            parent_agent_id=parent_id,
        )
        self._agents[agent.id] = agent

        if parent_id and parent_id in self._agents:
            parent = self._agents[parent_id]
            if agent.id not in parent.child_agent_ids:
                parent.child_agent_ids.append(agent.id)

        return agent

    def find_agents(self, capability: str = "",
                    status: AgentStatus | None = None) -> list[CognitiveAgent]:
        results = list(self._agents.values())
        if capability:
            results = [a for a in results if capability in a.capabilities]
        if status:
            results = [a for a in results if a.status == status]
        return results

    def assign_task(self, description: str,
                    required_capabilities: list[str] | None = None,
                    priority: int = 5,
                    parent_task_id: str = "") -> AgentTask | None:
        """Find the best agent for a task and assign it."""
        capabilities = required_capabilities or []

        # Find available agent with matching capabilities
        available = self.find_agents(status=AgentStatus.IDLE)
        if not capabilities:
            candidates = available
        else:
            candidates = [a for a in available
                         if any(c in a.capabilities for c in capabilities)]

        if not candidates:
            return None

        # Select least recently used agent
        agent = min(candidates, key=lambda a: len(a.task_history))

        task = AgentTask(
            description=description,
            agent_id=agent.id,
            parent_task_id=parent_task_id,
            required_capabilities=capabilities,
            priority=priority,
        )
        self._tasks[task.id] = task

        agent.status = AgentStatus.BUSY
        agent.current_task_id = task.id
        agent.task_history.append(task.id)
        task.status = TaskStatus.ASSIGNED
        task.started_at = time.time()

        return task

    def decompose_task(self, task_id: str,
                        subtasks: list[dict[str, Any]]) -> list[AgentTask]:
        """Decompose a task into sub-tasks and assign them."""
        parent = self._tasks.get(task_id)
        if not parent:
            return []

        children: list[AgentTask] = []
        for st in subtasks:
            child = self.assign_task(
                description=st.get("description", ""),
                required_capabilities=st.get("capabilities"),
                priority=st.get("priority", parent.priority),
                parent_task_id=task_id,
            )
            if child:
                children.append(child)
                parent.sub_task_ids.append(child.id)

        if children:
            parent.status = TaskStatus.IN_PROGRESS

        return children

    def complete_task(self, task_id: str, result: Any = None):
        """Mark a task as completed."""
        task = self._tasks.get(task_id)
        if not task:
            return
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = time.time()

        agent = self._agents.get(task.agent_id)
        if agent:
            agent.status = AgentStatus.IDLE
            agent.current_task_id = ""

        # Notify completion handlers
        for handler in self._completion_handlers.get(task_id, []):
            handler(task)

        # Check parent task
        if task.parent_task_id:
            self._check_parent_completion(task.parent_task_id)

    def fail_task(self, task_id: str, error: str = ""):
        """Mark a task as failed, with optional retry."""
        task = self._tasks.get(task_id)
        if not task:
            return

        task.error = error
        task.retry_count += 1

        if task.retry_count < task.max_retries:
            # Reassign to different agent
            agent = self._agents.get(task.agent_id)
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = ""

            task.status = TaskStatus.PENDING
            self._pending_queue.append(task.id)
        else:
            task.status = TaskStatus.FAILED
            agent = self._agents.get(task.agent_id)
            if agent:
                agent.status = AgentStatus.ERROR
                agent.current_task_id = ""

    def _check_parent_completion(self, parent_id: str):
        """Check if all sub-tasks of a parent are complete."""
        parent = self._tasks.get(parent_id)
        if not parent:
            return

        all_complete = all(
            self._tasks.get(sid) and self._tasks[sid].status == TaskStatus.COMPLETED
            for sid in parent.sub_task_ids
        ) if parent.sub_task_ids else False

        if all_complete:
            parent.status = TaskStatus.COMPLETED
            parent.completed_at = time.time()

    def on_complete(self, task_id: str, handler: Callable):
        """Register a handler for task completion."""
        self._completion_handlers.setdefault(task_id, []).append(handler)

    def get_agent_tree(self, agent_id: str) -> dict[str, Any]:
        """Get hierarchical agent tree rooted at the given agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return {}
        return {
            "id": agent.id,
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status.value,
            "children": [self.get_agent_tree(cid) for cid in agent.child_agent_ids],
        }

    def summary(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        for a in self._agents.values():
            status_counts[a.status.value] = status_counts.get(a.status.value, 0) + 1
        task_status: dict[str, int] = {}
        for t in self._tasks.values():
            task_status[t.status.value] = task_status.get(t.status.value, 0) + 1
        return {
            "agents": {
                "total": len(self._agents),
                "by_status": status_counts,
            },
            "tasks": {
                "total": len(self._tasks),
                "by_status": task_status,
                "pending_queue": len(self._pending_queue),
            },
            "agent_types": {t: len([a for a in self._agents.values() if a.agent_type == t])
                           for t in set(a.agent_type for a in self._agents.values())},
        }
