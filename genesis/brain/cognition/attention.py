"""
Attention Mechanism — salience-based focus for the cognitive architecture.

Determines which entities, beliefs, goals, and working memory items
receive processing focus. Supports multiple attention modes:
bottom-up (salience-driven), top-down (goal-driven), and mixed.

Integrates with: WorkingMemory (attention focus), GoalHierarchy (top-down),
BeliefSystem (salient beliefs), ReasoningEngine (focus on relevant premises).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class AttentionFocus:
    """What the cognitive system is currently focused on."""
    id: str = ""
    target_type: str = ""         # entity, belief, goal, observation
    target_id: str = ""
    description: str = ""
    salience: float = 0.0
    source: str = ""              # bottom_up, top_down, mixed
    created_at: float = 0.0
    duration: float = 0.0         # How long to maintain focus (seconds)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("focus", 10)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def is_expired(self) -> bool:
        return self.duration > 0 and (time.time() - self.created_at) > self.duration


class AttentionMechanism:
    """Attention mechanism that determines processing focus.

    Supports:
    - Bottom-up attention: salience-driven (novelty, surprise, importance)
    - Top-down attention: goal-driven (relevant to current goal)
    - Mixed attention: combination of both
    - Focus switching when salience thresholds are exceeded
    """

    def __init__(self, focus_capacity: int = 3, 
                 surprise_threshold: float = 0.3,
                 salience_decay: float = 0.05):
        self._foci: list[AttentionFocus] = []
        self._focus_capacity = focus_capacity
        self._surprise_threshold = surprise_threshold
        self._salience_decay = salience_decay
        self._history: list[AttentionFocus] = []

    @property
    def current_focus(self) -> list[AttentionFocus]:
        """Current active foci (not expired)."""
        self._foci = [f for f in self._foci if not f.is_expired]
        return list(self._foci)

    @property
    def primary_focus(self) -> AttentionFocus | None:
        """Highest-salience current focus."""
        foci = self.current_focus
        return max(foci, key=lambda f: f.salience) if foci else None

    def bottom_up(self, target_type: str, target_id: str,
                  description: str = "", salience: float = 0.5,
                  duration: float = 0.0) -> AttentionFocus:
        """Bottom-up attention driven by salience."""
        focus = AttentionFocus(
            target_type=target_type,
            target_id=target_id,
            description=description,
            salience=salience,
            source="bottom_up",
            duration=duration,
        )
        return self._add_focus(focus)

    def top_down(self, target_type: str, target_id: str,
                 description: str = "", priority: float = 0.5,
                 duration: float = 0.0) -> AttentionFocus:
        """Top-down attention driven by goals."""
        focus = AttentionFocus(
            target_type=target_type,
            target_id=target_id,
            description=description,
            salience=priority,
            source="top_down",
            duration=duration,
        )
        return self._add_focus(focus)

    def _add_focus(self, focus: AttentionFocus) -> AttentionFocus:
        # Check if already focused on this target
        existing = next((f for f in self._foci if f.target_id == focus.target_id), None)
        if existing:
            existing.salience = max(existing.salience, focus.salience)
            existing.duration = max(existing.duration, focus.duration)
            self._history.append(focus)
            return existing

        self._foci.append(focus)
        self._history.append(focus)

        # Evict lowest salience if over capacity
        while len(self._foci) > self._focus_capacity:
            lowest = min(self._foci, key=lambda f: f.salience)
            self._foci.remove(lowest)

        return focus

    def surprise(self, expected: float, observed: float) -> float:
        """Compute surprise (salience trigger) from prediction error."""
        error = abs(observed - expected)
        return min(1.0, error / max(self._surprise_threshold, 0.01))

    def orient(self, target_type: str, target_id: str,
               description: str, expected_salience: float,
               actual_salience: float) -> AttentionFocus | None:
        """Orient attention based on surprise (mismatch between expected and actual)."""
        s = self.surprise(expected_salience, actual_salience)
        if s >= self._surprise_threshold:
            return self.bottom_up(
                target_type=target_type,
                target_id=target_id,
                description=description,
                salience=s,
            )
        return None

    def decay(self):
        """Decay salience of all foci over time."""
        for focus in self._foci:
            focus.salience = max(0.0, focus.salience - self._salience_decay)
        self._foci = [f for f in self._foci if f.salience > 0]

    def summary(self) -> dict[str, Any]:
        foci = self.current_focus
        return {
            "active_foci": len(foci),
            "capacity": self._focus_capacity,
            "primary": self.primary_focus.description if self.primary_focus else None,
            "sources": {f.source for f in foci},
            "total_switches": len(self._history),
        }
