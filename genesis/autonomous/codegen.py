from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

from genesis.autonomous.planner import ImprovementPlan, ImprovementStep, PlanStatus
from genesis.utils.identity import generate_id


@dataclass
class Patch:
    file: str = ""
    original: str = ""
    patched: str = ""
    description: str = ""
    applied: bool = False
    validated: bool = False


@dataclass
class GenerationResult:
    id: str = ""
    timestamp: float = 0.0
    patches: list[Patch] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("gen", 12)
        if not self.timestamp:
            self.timestamp = time.time()


class CodeGenerator:
    def __init__(self, repo_root: str | None = None):
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._history: list[GenerationResult] = []
        self._lock = RLock()

    def generate(self, plan: ImprovementPlan) -> GenerationResult:
        result = GenerationResult()
        for step in plan.steps:
            try:
                patch = self._generate_for_step(step)
                if patch:
                    result.patches.append(patch)
            except Exception as e:
                result.errors.append(f"{step.file}: {e}")
        result.metrics = {
            "patches": len(result.patches),
            "errors": len(result.errors),
            "files_modified": len(set(p.file for p in result.patches)),
        }
        with self._lock:
            self._history.append(result)
        return result

    def _generate_for_step(self, step: ImprovementStep) -> Patch | None:
        filepath = self._resolve(step.file)
        if not filepath or not filepath.exists():
            return None
        original = filepath.read_text(encoding="utf-8")
        patched = self._apply_step(original, step)
        if patched == original:
            return None
        return Patch(
            file=str(filepath),
            original=original,
            patched=patched,
            description=step.description,
        )

    def _resolve(self, path_str: str) -> Path:
        p = Path(path_str)
        if p.is_absolute():
            return p
        return self._repo_root / p

    def apply(self, result: GenerationResult, dry_run: bool = False) -> int:
        applied = 0
        for patch in result.patches:
            try:
                filepath = Path(patch.file)
                if not dry_run:
                    filepath.write_text(patch.patched, encoding="utf-8")
                patch.applied = True
                applied += 1
            except Exception:
                pass
        return applied

    def validate(self, result: GenerationResult) -> bool:
        all_ok = True
        for patch in result.patches:
            try:
                compile(patch.patched, patch.file, "exec")
                patch.validated = True
            except SyntaxError:
                patch.validated = False
                all_ok = False
        return all_ok

    def rollback(self, result: GenerationResult) -> int:
        restored = 0
        for patch in result.patches:
            try:
                if patch.applied:
                    filepath = Path(patch.file)
                    filepath.write_text(patch.original, encoding="utf-8")
                    patch.applied = False
                    restored += 1
            except Exception:
                pass
        return restored

    @staticmethod
    def _apply_step(source: str, step: ImprovementStep) -> str:
        action = step.action.lower()

        if action.startswith("extract to a constant"):
            import re
            matches = set(re.findall(r"'([^']+)'|\"([^\"]+)\"", source))
            return source

        if action.startswith("use none"):
            lines = source.splitlines()
            result: list[str] = []
            for line in lines:
                stripped = line.strip()
                if "= []" in stripped:
                    result.append(line.replace("= []", "= None"))
                elif "= {}" in stripped:
                    result.append(line.replace("= {}", "= None"))
                elif "= set()" in stripped:
                    result.append(line.replace("= set()", "= None"))
                else:
                    result.append(line)
            return "\n".join(result)

        if action.startswith("catch specific"):
            lines = source.splitlines()
            result = []
            for line in lines:
                stripped = line.strip()
                if stripped == "except:" or stripped == "except :":
                    indent = line[:len(line) - len(line.lstrip())]
                    result.append(f"{indent}except Exception:")
                else:
                    result.append(line)
            return "\n".join(result)

        return source

    def history(self, limit: int = 10) -> list[GenerationResult]:
        with self._lock:
            return list(self._history[-limit:])

    def summary(self) -> dict[str, Any]:
        with self._lock:
            total_patches = sum(len(r.patches) for r in self._history)
            total_applied = sum(sum(1 for p in r.patches if p.applied) for r in self._history)
            return {
                "generations": len(self._history),
                "total_patches": total_patches,
                "applied": total_applied,
                "errors": sum(len(r.errors) for r in self._history),
            }
