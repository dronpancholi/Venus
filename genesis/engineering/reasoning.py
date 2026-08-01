from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering.object import EngineeringObject, EngineeringObjectType
from genesis.engineering.registry import get_registry


@dataclass
class Finding:
    id: str = ""
    category: str = ""
    severity: str = "info"
    title: str = ""
    description: str = ""
    evidence: list[str] = field(default_factory=list)
    object_ids: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ReasoningResult:
    question: str = ""
    findings: list[Finding] = field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0
    duration_ms: float = 0.0


class EngineeringReasoningEngine:
    def __init__(self):
        self._lock = threading.RLock()
        self._findings_history: list[Finding] = []

    def analyze_fragility(self) -> ReasoningResult:
        start = time.time()
        registry = get_registry()
        findings = []
        services = registry.get_by_type(EngineeringObjectType.SERVICE)
        agents = registry.get_by_type(EngineeringObjectType.AGENT)
        tasks = registry.get_by_type(EngineeringObjectType.TASK)
        sessions = registry.get_by_type(EngineeringObjectType.SESSION)

        if not services:
            findings.append(Finding(
                category="fragility",
                severity="critical",
                title="No registered services",
                description="ServiceRegistry is empty — no subsystems are advertising capabilities",
                evidence=["EngineeringRegistry by_type=service count=0"],
            ))

        running_tasks = [t for t in tasks if t.metadata.get("status") in ("running", "in_progress")]
        failed_tasks = [t for t in tasks if t.metadata.get("status") == "failed"]
        if failed_tasks:
            findings.append(Finding(
                category="fragility",
                severity="high" if len(failed_tasks) > 3 else "medium",
                title=f"{len(failed_tasks)} failed tasks detected",
                description=f"Tasks with failed status indicate execution fragility",
                evidence=[f"{t.name}: {t.metadata.get('status', 'unknown')}" for t in failed_tasks[:5]],
                object_ids=[t.id for t in failed_tasks[:5]],
            ))
        if running_tasks and not failed_tasks and not services:
            findings.append(Finding(
                category="fragility",
                severity="warning",
                title=f"{len(running_tasks)} tasks running in degraded environment",
                description="Tasks are executing but no services are registered — likely incomplete boot sequence",
                evidence=[f"running: {t.name}" for t in running_tasks[:3]],
            ))

        return ReasoningResult(
            question="fragility",
            findings=findings,
            summary=f"Found {len(findings)} fragility issues",
            duration_ms=(time.time() - start) * 1000,
        )

    def analyze_architecture_decay(self) -> ReasoningResult:
        start = time.time()
        registry = get_registry()
        findings = []
        objects = [obj for obj in registry._objects.values()] if hasattr(registry, '_objects') else []
        type_counts = registry.count_by_type()

        single_objects_of_type = {t: c for t, c in type_counts.items() if c == 1}
        if single_objects_of_type:
            findings.append(Finding(
                category="architecture_decay",
                severity="info",
                title=f"{len(single_objects_of_type)} singleton types detected",
                description="Types with only one instance may indicate underutilized architecture",
                evidence=[f"{t}: 1 instance" for t in single_objects_of_type],
            ))

        return ReasoningResult(
            question="architecture_decay",
            findings=findings,
            summary=f"Architecture analysis: {len(findings)} observations",
            duration_ms=(time.time() - start) * 1000,
        )

    def analyze_coupling(self) -> ReasoningResult:
        start = time.time()
        registry = get_registry()
        findings = []
        all_objects = []
        if hasattr(registry, '_objects'):
            all_objects = list(registry._objects.values())

        heavily_linked = [o for o in all_objects if len(o.links) > 5]
        if heavily_linked:
            findings.append(Finding(
                category="coupling",
                severity="info",
                title=f"{len(heavily_linked)} highly-coupled objects",
                description="Objects with many cross-links may indicate architectural coupling",
                evidence=[f"{o.name} ({o.object_type.value}): {len(o.links)} links" for o in heavily_linked[:5]],
                object_ids=[o.id for o in heavily_linked[:5]],
            ))

        return ReasoningResult(
            question="coupling",
            findings=findings,
            summary=f"Coupling analysis: {len(findings)} observations",
            duration_ms=(time.time() - start) * 1000,
        )

    def analyze_duplication(self) -> ReasoningResult:
        start = time.time()
        registry = get_registry()
        findings = []
        names_seen = {}
        if hasattr(registry, '_objects'):
            for o in registry._objects.values():
                name = o.name.lower().strip()
                if name:
                    names_seen.setdefault(name, []).append(o.id)

        duplicates = {n: ids for n, ids in names_seen.items() if len(ids) > 3}
        if duplicates:
            findings.append(Finding(
                category="duplication",
                severity="warning",
                title=f"{len(duplicates)} potentially duplicated names",
                description="Multiple EngineeringObjects share the same name — possible duplication",
                evidence=[f"'{n}': {len(ids)} occurrences" for n, ids in sorted(duplicates.items())[:5]],
            ))

        return ReasoningResult(
            question="duplication",
            findings=findings,
            summary=f"Duplication analysis: {len(findings)} observations",
            duration_ms=(time.time() - start) * 1000,
        )

    def analyze_debt(self) -> ReasoningResult:
        start = time.time()
        registry = get_registry()
        findings = []
        objects_without_desc = []
        objects_without_tags = []
        if hasattr(registry, '_objects'):
            for o in registry._objects.values():
                if not o.description:
                    objects_without_desc.append(o)
                if not o.tags:
                    objects_without_tags.append(o)

        if objects_without_desc:
            findings.append(Finding(
                category="debt",
                severity="low",
                title=f"{len(objects_without_desc)} objects lack descriptions",
                description="Missing descriptions reduce discoverability and AI summary quality",
                evidence=[f"{o.name} ({o.object_type.value})" for o in objects_without_desc[:5]],
                object_ids=[o.id for o in objects_without_desc[:5]],
            ))
        if objects_without_tags:
            findings.append(Finding(
                category="debt",
                severity="low",
                title=f"{len(objects_without_tags)} objects lack tags",
                description="Missing tags reduce searchability and categorization",
                evidence=[f"{o.name} ({o.object_type.value})" for o in objects_without_tags[:5]],
                object_ids=[o.id for o in objects_without_tags[:5]],
            ))

        return ReasoningResult(
            question="debt",
            findings=findings,
            summary=f"Debt analysis: {len(findings)} observations",
            duration_ms=(time.time() - start) * 1000,
        )

    def comprehensive_analysis(self) -> ReasoningResult:
        start = time.time()
        results = [
            self.analyze_fragility(),
            self.analyze_architecture_decay(),
            self.analyze_coupling(),
            self.analyze_duplication(),
            self.analyze_debt(),
        ]
        all_findings = []
        for r in results:
            all_findings.extend(r.findings)
        all_findings.sort(key=lambda f: {"critical": 0, "high": 1, "warning": 2, "medium": 3, "low": 4, "info": 5}.get(f.severity, 6))

        severity_counts = {}
        for f in all_findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        summary_parts = [f"Comprehensive engineering analysis:"]
        for sev, count in sorted(severity_counts.items()):
            summary_parts.append(f"  {sev}: {count} findings")
        summary_parts.append(f"  total: {len(all_findings)} findings")

        return ReasoningResult(
            question="comprehensive",
            findings=all_findings,
            summary="\n".join(summary_parts),
            duration_ms=(time.time() - start) * 1000,
        )

    def summary(self) -> dict[str, Any]:
        return {
            "findings_in_history": len(self._findings_history),
            "analyzers": ["fragility", "architecture_decay", "coupling", "duplication", "debt", "comprehensive"],
        }
