from __future__ import annotations

import ast
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any


@dataclass
class AnalysisFinding:
    category: str = ""
    severity: str = "info"
    file: str = ""
    line: int = 0
    message: str = ""
    suggestion: str = ""
    metric: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisReport:
    timestamp: float = 0.0
    total_files: int = 0
    total_lines: int = 0
    findings: list[AnalysisFinding] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)


class SelfAnalyzer:
    def __init__(self, repo_root: str | None = None):
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._lock = RLock()

    def analyze(self, path: str | None = None) -> AnalysisReport:
        target = Path(path) if path else self._repo_root
        if not target.exists():
            return AnalysisReport(timestamp=time.time())
        report = AnalysisReport(timestamp=time.time())
        findings: list[AnalysisFinding] = []
        total_lines = 0
        total_files = 0

        for pyfile in sorted(target.rglob("*.py")):
            if "__pycache__" in str(pyfile):
                continue
            if not pyfile.is_file():
                continue
            total_files += 1
            lines = self._read_file(pyfile)
            total_lines += len(lines)
            total_chars = sum(len(l) for l in lines)
            findings.extend(self._analyze_file(pyfile, lines))

        report.total_files = total_files
        report.total_lines = total_lines
        report.findings = findings

        by_severity: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)
        for f in findings:
            by_severity[f.severity] += 1
            by_category[f.category] += 1

        report.summary = {
            "total_findings": len(findings),
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
        }
        report.metrics = {
            "files_per_second": total_files / max(0.001, time.time() - report.timestamp),
            "findings_per_file": len(findings) / max(1, total_files),
            "avg_line_length": total_chars / max(1, total_lines) if total_lines else 0,
        }
        return report

    def _read_file(self, path: Path) -> list[str]:
        try:
            return path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return []

    def _analyze_file(self, path: Path, lines: list[str]) -> list[AnalysisFinding]:
        findings: list[AnalysisFinding] = []
        rel = str(path.relative_to(self._repo_root)) if path.is_relative_to(self._repo_root) else str(path)
        source = "\n".join(lines)

        findings.extend(self._check_todo(rel, lines))
        findings.extend(self._check_long_lines(rel, lines))
        findings.extend(self._check_imports(rel, source))
        findings.extend(self._check_complex_functions(rel, source))
        findings.extend(self._check_duplicate_strings(rel, lines))
        findings.extend(self._check_mutable_defaults(rel, source))
        findings.extend(self._check_bare_excepts(rel, source))

        return findings

    @staticmethod
    def _check_todo(file: str, lines: list[str]) -> list[AnalysisFinding]:
        results = []
        for i, line in enumerate(lines, 1):
            lower = line.strip().lower()
            if "todo" in lower or "fixme" in lower or "hack" in lower:
                results.append(AnalysisFinding(
                    category="todo", severity="info",
                    file=file, line=i,
                    message=f"TODO/FIXME/HACK marker at line {i}",
                    suggestion="Resolve the pending work item",
                ))
        return results

    @staticmethod
    def _check_long_lines(file: str, lines: list[str]) -> list[AnalysisFinding]:
        results = []
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                results.append(AnalysisFinding(
                    category="style", severity="warning",
                    file=file, line=i,
                    message=f"Line too long ({len(line)} > 120)",
                    suggestion="Break into multiple lines",
                    metric=float(len(line)),
                ))
        return results

    @staticmethod
    def _check_imports(file: str, source: str) -> list[AnalysisFinding]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results
        imports: dict[str, int] = defaultdict(int)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.name] += 1
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports[node.module] += 1
        for mod, count in imports.items():
            if count > 1:
                results.append(AnalysisFinding(
                    category="imports", severity="warning",
                    file=file, line=0,
                    message=f"Duplicate import: '{mod}' imported {count} times",
                    suggestion="Consolidate to a single import",
                    metric=float(count),
                ))
        return results

    @staticmethod
    def _check_complex_functions(file: str, source: str) -> list[AnalysisFinding]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.While, ast.For, ast.Try)))
                if branches > 10:
                    results.append(AnalysisFinding(
                        category="complexity", severity="warning",
                        file=file, line=node.lineno,
                        message=f"High cyclomatic complexity ({branches} branches) in '{node.name}'",
                        suggestion="Consider refactoring into smaller functions",
                        metric=float(branches),
                    ))
        return results

    @staticmethod
    def _check_duplicate_strings(file: str, lines: list[str]) -> list[AnalysisFinding]:
        results = []
        strings: dict[str, list[int]] = defaultdict(list)
        import re
        for i, line in enumerate(lines, 1):
            for m in re.finditer(r"'([^']+)'|\"([^\"]+)\"", line):
                s = m.group(1) or m.group(2)
                if len(s) > 20:
                    strings[s].append(i)
        for s, linenos in strings.items():
            if len(linenos) >= 3:
                results.append(AnalysisFinding(
                    category="duplication", severity="warning",
                    file=file, line=linenos[0],
                    message=f"Duplicate literal '{s[:40]}...' appears {len(linenos)} times",
                    suggestion="Extract to a constant or shared variable",
                    metric=float(len(linenos)),
                    metadata={"lines": linenos},
                ))
        return results

    @staticmethod
    def _check_mutable_defaults(file: str, source: str) -> list[AnalysisFinding]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        results.append(AnalysisFinding(
                            category="bug_prone", severity="warning",
                            file=file, line=node.lineno,
                            message=f"Mutable default argument in '{node.name}'",
                            suggestion="Use None and initialize inside function body",
                        ))
        return results

    @staticmethod
    def _check_bare_excepts(file: str, source: str) -> list[AnalysisFinding]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                results.append(AnalysisFinding(
                    category="bug_prone", severity="warning",
                    file=file, line=node.lineno,
                    message="Bare 'except:' clause",
                    suggestion="Catch specific exception types",
                ))
        return results
