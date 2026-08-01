from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.engineering.reasoning import EngineeringReasoningEngine, Finding, ReasoningResult


@dataclass
class ReviewReport:
    id: str = ""
    timestamp: float = 0.0
    duration_ms: float = 0.0
    review_types: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "review_types": self.review_types,
            "findings_count": len(self.findings),
            "critical_count": len([f for f in self.findings if f.severity == "critical"]),
            "recommendations": self.recommendations,
        }


class AutonomousReview:
    def __init__(self, kernel=None, interval_secs: float = 300.0):
        self._kernel = kernel
        self._reasoning = EngineeringReasoningEngine()
        self._registry = get_registry()
        self._interval = interval_secs
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._reports: list[ReviewReport] = []
        self._max_reports = 100

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def interval_secs(self) -> float:
        return self._interval

    def set_interval(self, interval_secs: float):
        with self._lock:
            self._interval = max(10.0, interval_secs)

    def run_review(self, review_types: list[str] | None = None) -> ReviewReport:
        start = time.time()
        types = review_types or ["fragility", "architecture_decay", "coupling", "duplication", "debt"]
        all_findings = []
        recommendations = []

        for rt in types:
            try:
                if rt == "fragility":
                    result = self._reasoning.analyze_fragility()
                elif rt == "architecture_decay":
                    result = self._reasoning.analyze_architecture_decay()
                elif rt == "coupling":
                    result = self._reasoning.analyze_coupling()
                elif rt == "duplication":
                    result = self._reasoning.analyze_duplication()
                elif rt == "debt":
                    result = self._reasoning.analyze_debt()
                else:
                    continue
                all_findings.extend(result.findings)
            except Exception:
                continue

        all_findings.sort(key=lambda f: {"critical": 0, "high": 1, "warning": 2, "medium": 3, "low": 4, "info": 5}.get(f.severity, 6))

        severity_groups = {}
        for f in all_findings:
            severity_groups.setdefault(f.severity, []).append(f)

        for sev, sev_findings in sorted(severity_groups.items()):
            if sev in ("critical", "high", "warning"):
                for f in sev_findings[:3]:
                    if f.recommendation:
                        recommendations.append(f.recommendation)
                    else:
                        recommendations.append(f"Address {f.category}: {f.title}")

        report = ReviewReport(
            timestamp=time.time(),
            duration_ms=(time.time() - start) * 1000,
            review_types=types,
            findings=all_findings,
            recommendations=recommendations,
        )
        with self._lock:
            self._reports.append(report)
            if len(self._reports) > self._max_reports:
                self._reports = self._reports[-self._max_reports:]

        if self._kernel:
            try:
                report_obj = EngineeringObject(
                    object_type=EngineeringObjectType.RECOMMENDATION,
                    name=f"Autonomous Review ({len(all_findings)} findings)",
                    description=f"Review of {', '.join(types)}: {len(all_findings)} findings, {len(recommendations)} recommendations",
                    tags=types + ["autonomous_review"],
                    metadata=report.to_dict(),
                )
                self._registry.register(report_obj)
                self._kernel.emit("autonomous.review.completed", {
                    "findings": len(all_findings),
                    "recommendations": len(recommendations),
                    "types": types,
                }, origin="autonomous_review", tags=["review"])
            except Exception:
                pass

        return report

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="autonomous-review")
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                self.run_review()
            except Exception:
                pass
            time.sleep(self._interval)

    def get_latest_report(self) -> ReviewReport | None:
        with self._lock:
            return self._reports[-1] if self._reports else None

    def get_reports(self, limit: int = 10) -> list[ReviewReport]:
        with self._lock:
            return list(reversed(self._reports))[:limit]

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "interval_secs": self._interval,
                "reports_generated": len(self._reports),
                "total_findings": sum(len(r.findings) for r in self._reports),
                "total_recommendations": sum(len(r.recommendations) for r in self._reports),
            }
