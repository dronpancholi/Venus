"""
Strategy Engine — tool selection, cost optimization, and strategy planning.

Selects the best tools and strategies for achieving goals based on:
- Capability matching (what tools can do)
- Cost-benefit analysis (resource efficiency)
- Success history (what has worked before)
- Constraint satisfaction (tool requirements)

Integrates with: CapabilityRegistry (available tools), GoalHierarchy (what to achieve),
Marketplace (resource costs), BeliefSystem (tool effectiveness beliefs),
EpisodicMemory (past tool usage).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class Tool:
    """A tool available to the cognitive system."""
    id: str = ""
    name: str = ""
    description: str = ""
    capabilities: list[str] = field(default_factory=list)   # What it can do
    requirements: list[str] = field(default_factory=list)   # What it needs
    cost_per_use: float = 1.0
    estimated_duration: float = 0.0                         # Estimated time per use
    success_rate: float = 0.5                               # Historical success rate
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("tool", 10)

    @property
    def expected_value(self) -> float:
        """Expected value = success_rate / (cost * duration)."""
        denom = max(0.01, self.cost_per_use * max(0.1, self.estimated_duration))
        return self.success_rate / denom


@dataclass
class Strategy:
    """A strategy — plan of action to achieve a goal."""
    id: str = ""
    goal_id: str = ""
    name: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_duration: float = 0.0
    expected_success: float = 0.5
    risk: float = 0.0
    alternatives: list[str] = field(default_factory=list)
    selected: bool = False
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("strategy", 12)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def score(self) -> float:
        """Overall strategy score (higher is better)."""
        return self.expected_success / max(0.01, self.estimated_cost * (1.0 + self.risk))


class StrategyEngine:
    """Strategic planning: tool selection, cost-benefit analysis, strategy generation.

    Supports:
    - Tool capability matching
    - Cost-benefit analysis across strategies
    - Strategy generation from available tools
    - Success probability estimation
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._strategies: list[Strategy] = []
        self._tool_usage: dict[str, dict[str, Any]] = {}    # Tool usage history

    def register_tool(self, name: str, description: str = "",
                      capabilities: list[str] | None = None,
                      requirements: list[str] | None = None,
                      cost_per_use: float = 1.0,
                      estimated_duration: float = 0.0,
                      success_rate: float = 0.5) -> Tool:
        tool = Tool(
            name=name,
            description=description,
            capabilities=capabilities or [],
            requirements=requirements or [],
            cost_per_use=cost_per_use,
            estimated_duration=estimated_duration,
            success_rate=success_rate,
        )
        self._tools[tool.id] = tool
        return tool

    def find_tools(self, capability: str = "",
                   max_cost: float = float('inf'),
                   min_success_rate: float = 0.0) -> list[Tool]:
        results = list(self._tools.values())
        if capability:
            results = [t for t in results if capability in t.capabilities]
        results = [t for t in results if t.cost_per_use <= max_cost]
        results = [t for t in results if t.success_rate >= min_success_rate]
        return sorted(results, key=lambda t: t.expected_value, reverse=True)

    def select_tool(self, capability: str, goal_id: str = "",
                    max_cost: float = float('inf')) -> Tool | None:
        """Select the best tool for a capability."""
        tools = self.find_tools(capability, max_cost)
        if not tools:
            return None
        selected = tools[0]
        self._record_usage(selected.id, goal_id)
        return selected

    def _record_usage(self, tool_id: str, goal_id: str):
        if tool_id not in self._tool_usage:
            self._tool_usage[tool_id] = {"count": 0, "goals": []}
        self._tool_usage[tool_id]["count"] += 1
        if goal_id:
            self._tool_usage[tool_id]["goals"].append(goal_id)

    def generate_strategies(self, goal_id: str, goal_capabilities: list[str],
                             max_strategies: int = 3) -> list[Strategy]:
        """Generate strategies for achieving a goal given required capabilities."""
        strategies: list[Strategy] = []

        for cap in goal_capabilities:
            tools = self.find_tools(capability=cap)
            if not tools:
                continue

            for tool in tools[:3]:  # Top 3 tools per capability
                strategy = Strategy(
                    goal_id=goal_id,
                    name=f"Use {tool.name} for {cap}",
                    steps=[{
                        "tool_id": tool.id,
                        "tool_name": tool.name,
                        "capability": cap,
                        "cost": tool.cost_per_use,
                        "duration": tool.estimated_duration,
                    }],
                    estimated_cost=tool.cost_per_use,
                    estimated_duration=tool.estimated_duration,
                    expected_success=tool.success_rate,
                    risk=1.0 - tool.success_rate,
                )
                strategies.append(strategy)

        # Combine tools into multi-step strategies
        if len(goal_capabilities) > 1:
            combined = self._combine_strategies(goal_id, goal_capabilities, 
                                                  strategies[:6], max_strategies)
            strategies.extend(combined)

        strategies.sort(key=lambda s: s.score, reverse=True)
        self._strategies.extend(strategies[:max_strategies])
        return strategies[:max_strategies]

    def _combine_strategies(self, goal_id: str, capabilities: list[str],
                             base_strategies: list[Strategy],
                             max_combined: int) -> list[Strategy]:
        """Combine individual tool strategies into multi-step strategies."""
        combined: list[Strategy] = []
        used_tools = set()

        for s in base_strategies:
            for step in s.steps:
                used_tools.add(step["tool_name"])

        if len(used_tools) >= 2:
            strategy = Strategy(
                goal_id=goal_id,
                name="Combined: " + " + ".join(list(used_tools)[:3]),
                steps=[s.steps[0] for s in base_strategies[:len(capabilities)] 
                       if s.steps],
                estimated_cost=sum(s.estimated_cost for s in base_strategies[:3]),
                estimated_duration=max(s.estimated_duration for s in base_strategies[:3]),
                expected_success=min(s.expected_success for s in base_strategies[:3]),
                risk=1.0 - min(s.expected_success for s in base_strategies[:3]),
            )
            combined.append(strategy)

        return combined[:max_combined]

    def best_strategy(self, goal_id: str) -> Strategy | None:
        """Get the highest-scored strategy for a goal."""
        strategies = [s for s in self._strategies if s.goal_id == goal_id]
        return max(strategies, key=lambda s: s.score) if strategies else None

    def update_success_rate(self, tool_id: str, succeeded: bool):
        """Update a tool's success rate after use."""
        tool = self._tools.get(tool_id)
        if tool:
            usage = self._tool_usage.get(tool_id, {"count": 0})
            total = usage["count"]
            tool.success_rate = ((tool.success_rate * total) + (1.0 if succeeded else 0.0)) / (total + 1)

    def summary(self) -> dict[str, Any]:
        return {
            "tools": len(self._tools),
            "strategies": len(self._strategies),
            "by_capability": {cap: len([t for t in self._tools.values() if cap in t.capabilities])
                              for cap in set(c for t in self._tools.values() for c in t.capabilities)},
            "total_usage": sum(u["count"] for u in self._tool_usage.values()),
        }
