"""
Goal Hierarchy — hierarchical goal system with decomposition, priority, and dependency tracking.

Goals represent desired states. They decompose into subgoals, have dependencies,
priority levels, and track progress. The goal system integrates with the Planning
subsystem and the Marketplace for resource allocation.

Integrates with: EngineeringBrain (goals as entities), Planning (hierarchical plans),
Marketplace (resource allocation for goal achievement), BeliefSystem (goal justification).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class GoalStatus(Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    ACHIEVED = "achieved"
    FAILED = "failed"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class GoalPriority(Enum):
    CRITICAL = 0      # Must happen now
    HIGH = 1          # Should happen soon
    MEDIUM = 2        # Important but not urgent
    LOW = 3           # Nice to have
    DEFERRED = 4      # Postponed


@dataclass
class Goal:
    id: str = ""
    name: str = ""
    description: str = ""
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PROPOSED
    progress: float = 0.0               # 0.0 to 1.0
    parent_id: str = ""
    child_ids: list[str] = field(default_factory=list)
    dependency_ids: list[str] = field(default_factory=list)  # Goals that must complete first
    depends_on_me: list[str] = field(default_factory=list)   # Goals that depend on this
    estimated_effort: float = 0.0        # In some unit (e.g., agent-hours)
    actual_effort: float = 0.0
    deadline: float = 0.0
    owner: str = ""                      # Agent or subsystem responsible
    tags: list[str] = field(default_factory=list)
    justification: str = ""              # Why this goal exists
    success_criteria: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("goal", 12)
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = self.created_at

    @property
    def is_blocked(self) -> bool:
        return self.status == GoalStatus.BLOCKED

    @property
    def is_complete(self) -> bool:
        return self.status in (GoalStatus.ACHIEVED, GoalStatus.FAILED,
                               GoalStatus.SUPERSEDED, GoalStatus.CANCELLED)

    @property
    def remaining_effort(self) -> float:
        return max(0.0, self.estimated_effort - self.actual_effort)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.value,
            "progress": self.progress,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "dependency_ids": self.dependency_ids,
            "estimated_effort": self.estimated_effort,
            "actual_effort": self.actual_effort,
            "deadline": self.deadline,
            "owner": self.owner,
            "tags": self.tags,
            "justification": self.justification,
            "success_criteria": self.success_criteria,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class GoalHierarchy:
    """Manages a tree of goals with decomposition, priority, and dependency resolution.

    Supports:
    - Goal creation and hierarchical decomposition
    - Dependency tracking and blocking detection
    - Priority-based ordering
    - Progress computation (rolls up from children)
    - Integration with Planning subsystem for plan creation
    """

    def __init__(self):
        self._goals: dict[str, Goal] = {}
        self._index_by_owner: dict[str, list[str]] = {}
        self._index_by_status: dict[str, list[str]] = {}

    @property
    def goal_count(self) -> int:
        return len(self._goals)

    def create_goal(self, name: str, description: str = "",
                    priority: GoalPriority = GoalPriority.MEDIUM,
                    parent_id: str = "",
                    dependency_ids: list[str] | None = None,
                    estimated_effort: float = 0.0,
                    owner: str = "",
                    justification: str = "",
                    success_criteria: list[str] | None = None,
                    tags: list[str] | None = None) -> Goal:
        goal = Goal(
            name=name,
            description=description,
            priority=priority,
            parent_id=parent_id,
            dependency_ids=dependency_ids or [],
            estimated_effort=estimated_effort,
            owner=owner,
            justification=justification,
            success_criteria=success_criteria or [],
            tags=tags or [],
        )

        # Register with parent
        if parent_id and parent_id in self._goals:
            parent = self._goals[parent_id]
            if goal.id not in parent.child_ids:
                parent.child_ids.append(goal.id)
            parent.updated_at = time.time()

        # Register reverse dependencies
        for dep_id in goal.dependency_ids:
            dep = self._goals.get(dep_id)
            if dep and goal.id not in dep.depends_on_me:
                dep.depends_on_me.append(goal.id)

        self._goals[goal.id] = goal
        self._reindex(goal)

        # Check if blocked
        self._update_blocked_status(goal)
        return goal

    def get(self, goal_id: str) -> Goal | None:
        return self._goals.get(goal_id)

    def find(self, status: GoalStatus | None = None,
             priority: GoalPriority | None = None,
             owner: str = "",
             tag: str = "") -> list[Goal]:
        results: list[Goal] = []
        if owner:
            ids = self._index_by_owner.get(owner, [])
            results = [self._goals[gid] for gid in ids if gid in self._goals]
        else:
            results = list(self._goals.values())

        if status:
            results = [g for g in results if g.status == status]
        if priority:
            results = [g for g in results if g.priority == priority]
        if tag:
            results = [g for g in results if tag in g.tags]
        return results

    def update_progress(self, goal_id: str, progress: float):
        goal = self._goals.get(goal_id)
        if not goal:
            return
        goal.progress = min(1.0, max(0.0, progress))
        goal.updated_at = time.time()
        if progress >= 1.0:
            goal.status = GoalStatus.ACHIEVED
        elif progress > 0:
            goal.status = GoalStatus.IN_PROGRESS
        self._reindex(goal)
        # Roll up progress to parent
        self._rollup_progress(goal_id)

    def _rollup_progress(self, goal_id: str):
        goal = self._goals.get(goal_id)
        if not goal or not goal.parent_id:
            return
        parent = self._goals.get(goal.parent_id)
        if not parent:
            return
        children = [self._goals[cid] for cid in parent.child_ids if cid in self._goals]
        if children:
            parent.progress = sum(c.progress for c in children) / len(children)
            parent.updated_at = time.time()
        # Recursively roll up
        self._rollup_progress(goal.parent_id)

    def decompose(self, parent_id: str, subgoals: list[dict[str, Any]]) -> list[Goal]:
        """Decompose a goal into subgoals."""
        parent = self._goals.get(parent_id)
        if not parent:
            return []
        children = []
        for sg in subgoals:
            child = self.create_goal(
                name=sg.get("name", ""),
                description=sg.get("description", ""),
                priority=sg.get("priority", parent.priority),
                parent_id=parent_id,
                dependency_ids=sg.get("dependency_ids"),
                estimated_effort=sg.get("estimated_effort", 0.0),
                owner=sg.get("owner", parent.owner),
                justification=sg.get("justification", parent.justification),
                success_criteria=sg.get("success_criteria"),
                tags=sg.get("tags", parent.tags.copy()),
            )
            children.append(child)
        parent.status = GoalStatus.ACTIVE
        parent.updated_at = time.time()
        return children

    def _update_blocked_status(self, goal: Goal):
        """Check if a goal is blocked by unmet dependencies."""
        for dep_id in goal.dependency_ids:
            dep = self._goals.get(dep_id)
            if dep and dep.status != GoalStatus.ACHIEVED:
                goal.status = GoalStatus.BLOCKED
                goal.updated_at = time.time()
                return

    def priorities(self, status: GoalStatus | None = GoalStatus.ACTIVE) -> list[Goal]:
        """Get goals sorted by priority (most urgent first), optionally filtered by status."""
        candidates = self.find(status=status) if status else list(self._goals.values())
        return sorted(candidates, key=lambda g: (g.priority.value, g.deadline or float('inf')))

    def get_chain(self, goal_id: str) -> list[Goal]:
        """Get the full chain from root to this goal."""
        chain: list[Goal] = []
        current = self._goals.get(goal_id)
        while current:
            chain.append(current)
            current = self._goals.get(current.parent_id) if current.parent_id else None
        return list(reversed(chain))

    def _reindex(self, goal: Goal):
        self._index_by_owner.setdefault(goal.owner, [])
        if goal.id not in self._index_by_owner[goal.owner]:
            self._index_by_owner[goal.owner].append(goal.id)
        self._index_by_status.setdefault(goal.status.value, [])
        if goal.id not in self._index_by_status[goal.status.value]:
            self._index_by_status[goal.status.value].append(goal.id)

    def summary(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        priority_counts: dict[str, int] = {}
        for g in self._goals.values():
            status_counts[g.status.value] = status_counts.get(g.status.value, 0) + 1
            priority_counts[g.priority.name] = priority_counts.get(g.priority.name, 0) + 1
        return {
            "total_goals": len(self._goals),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "average_progress": sum(g.progress for g in self._goals.values()) / max(len(self._goals), 1),
            "blocked_goals": len([g for g in self._goals.values() if g.status == GoalStatus.BLOCKED]),
        }
