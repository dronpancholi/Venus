"""
Genesis AgentOS — Andrej Karpathy Skills & Execution Engine.

Directly implements Andrej Karpathy's 4 core agent coding guidelines:
1. Think Before Coding (State assumptions, surface tradeoffs, don't hide confusion)
2. Simplicity First (Minimum code, no speculative abstractions, 200 lines to 50)
3. Surgical Changes (Touch only target code, match style, clean up own orphans)
4. Goal-Driven Execution (Define success criteria, loop until verified)
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class KarpathyPrinciple(str, Enum):
    THINK_BEFORE_CODING = "Think Before Coding"
    SIMPLICITY_FIRST = "Simplicity First"
    SURGICAL_CHANGES = "Surgical Changes"
    GOAL_DRIVEN_EXECUTION = "Goal-Driven Execution"


KARPATHY_GUIDELINES_TEXT = """
# Karpathy Coding Guidelines

## 1. Think Before Coding
- State assumptions explicitly. If uncertain, ask rather than guess.
- If multiple interpretations exist, surface them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop and name what's confusing.

## 2. Simplicity First
- Write the minimum code that solves the problem. Nothing speculative.
- Avoid abstractions for single-use code.
- Avoid unnecessary "flexibility" or "configurability".
- If 200 lines could be 50, rewrite it.

## 3. Surgical Changes
- Touch only what you must. Match existing code style.
- Don't refactor code or comments outside your task's scope.
- Remove imports/variables/functions that YOUR changes made unused.
- Do not delete pre-existing dead code unless explicitly asked.

## 4. Goal-Driven Execution
- Define explicit success criteria before making changes.
- Write or run verification tests/commands.
- Loop independently until verification passes.
"""


@dataclass
class PreCodingThought:
    request: str
    assumptions: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)
    simpler_alternatives: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    proceed_recommended: bool = True


@dataclass
class SurgicalDiffReport:
    modified_files: List[str] = field(default_factory=list)
    added_lines: int = 0
    deleted_lines: int = 0
    orphaned_imports: List[str] = field(default_factory=list)
    orphaned_vars: List[str] = field(default_factory=list)
    surgical_score: float = 1.0  # 1.0 = clean & surgical
    violations: List[str] = field(default_factory=list)


@dataclass
class GoalStep:
    step_number: int
    description: str
    verification_command: str
    status: str = "pending"  # pending, running, passed, failed
    output: str = ""
    duration_seconds: float = 0.0


@dataclass
class GoalExecutionResult:
    goal_description: str
    success: bool
    iterations: int
    steps: List[GoalStep] = field(default_factory=list)
    final_verification_output: str = ""
    thought: Optional[PreCodingThought] = None
    diff_report: Optional[SurgicalDiffReport] = None


class KarpathyDiffValidator:
    """Validates code diffs for surgical cleanliness and orphaned symbols."""

    @staticmethod
    def analyze_python_ast(source_code: str) -> Tuple[List[str], List[str]]:
        """Extract imported names and used names using AST."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return [], []

        imported_names = []
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.append(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.append(alias.asname or alias.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        orphans = [name for name in imported_names if name not in used_names]
        return imported_names, orphans

    @classmethod
    def audit_file_change(cls, file_path: str, old_content: str, new_content: str) -> SurgicalDiffReport:
        report = SurgicalDiffReport()
        report.modified_files = [file_path]

        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        # Simple diff line counts
        added = max(0, len(new_lines) - len(old_lines))
        report.added_lines = added
        report.deleted_lines = max(0, len(old_lines) - len(new_lines))

        # Check AST for Python files
        if file_path.endswith(".py"):
            _, orphans = cls.analyze_python_ast(new_content)
            report.orphaned_imports = orphans
            if orphans:
                report.violations.append(f"Unused imports detected: {', '.join(orphans)}")
                report.surgical_score -= 0.2 * len(orphans)

        # Check over-bloat (if line count grew > 3x unnecessarily)
        if len(old_lines) > 10 and len(new_lines) > 3 * len(old_lines):
            report.violations.append("Change increased line count significantly — check for overengineering.")
            report.surgical_score -= 0.3

        report.surgical_score = max(0.0, min(1.0, report.surgical_score))
        return report


class KarpathyExecutionEngine:
    """Core autonomous loop enforcing Karpathy guidelines."""

    def __init__(self, workspace_path: str | Path = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.diff_validator = KarpathyDiffValidator()

    def get_system_prompt(self, project_context: str = "") -> str:
        """Constructs system prompt embedding Karpathy guidelines."""
        prompt = KARPATHY_GUIDELINES_TEXT
        if project_context:
            prompt += f"\n\nProject Context:\n{project_context}"
        return prompt

    def think_before_coding(self, request: str, code_context: str = "") -> PreCodingThought:
        """Phase 1: Pre-coding explicit thinking & assumption analysis."""
        thought = PreCodingThought(request=request)

        # Heuristic analysis of request
        req_lower = request.lower()

        # Detect potential ambiguity
        if any(word in req_lower for word in ["better", "improve", "refactor", "clean"]):
            thought.assumptions.append("User requested qualitative improvement — scope focused to specified area.")
            thought.tradeoffs.append("Tradeoff: Deep structural refactor vs. minimal targeted fix.")

        if "add" in req_lower or "create" in req_lower:
            thought.assumptions.append("Adding new capability without altering public contract of existing modules.")

        # Check for potential simpler alternatives
        if "framework" in req_lower or "abstract" in req_lower or "class" in req_lower:
            thought.simpler_alternatives.append("Consider plain functions or dictionary configuration instead of a new class hierarchy.")

        thought.proceed_recommended = len(thought.open_questions) == 0
        return thought

    def execute_goal(
        self,
        goal_description: str,
        verification_cmd: str,
        action_fn: Optional[Callable[[], Any]] = None,
        max_iterations: int = 3,
    ) -> GoalExecutionResult:
        """Phase 4: Goal-driven verification loop."""
        result = GoalExecutionResult(
            goal_description=goal_description,
            success=False,
            iterations=0,
        )

        # 1. Think Before Coding
        result.thought = self.think_before_coding(goal_description)

        for iteration in range(1, max_iterations + 1):
            result.iterations = iteration
            step_start = time.time()
            step = GoalStep(
                step_number=iteration,
                description=f"Attempt {iteration} for: {goal_description}",
                verification_command=verification_cmd,
            )

            # Perform action if function provided
            if action_fn:
                try:
                    action_fn()
                except Exception as e:
                    step.status = "failed"
                    step.output = f"Action error: {e}"
                    step.duration_seconds = time.time() - step_start
                    result.steps.append(step)
                    continue

            # Run verification command
            cmd_res = self.run_verification_command(verification_cmd)
            step.output = cmd_res["output"]
            step.duration_seconds = time.time() - step_start

            if cmd_res["exit_code"] == 0:
                step.status = "passed"
                result.steps.append(step)
                result.success = True
                result.final_verification_output = cmd_res["output"]
                break
            else:
                step.status = "failed"
                result.steps.append(step)
                result.final_verification_output = cmd_res["output"]

        return result

    def run_verification_command(self, command: str) -> Dict[str, Any]:
        """Execute verification command and return stdout/stderr and exit code."""
        start = time.time()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "exit_code": proc.returncode,
                "output": proc.stdout + ("\n" + proc.stderr if proc.stderr else ""),
                "duration": time.time() - start,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "output": "Verification command timed out after 60s",
                "duration": time.time() - start,
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "output": f"Failed to execute command: {e}",
                "duration": time.time() - start,
            }
