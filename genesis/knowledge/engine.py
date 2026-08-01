from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import (
    EngineeringLink,
    EngineeringObject,
    EngineeringObjectType,
    EngineeringRelationship,
    get_registry,
)
from genesis.fabric.kernel import FabricKernel
from genesis.knowledge.parser import ParsedReport, parse_reports_directory


@dataclass
class KnowledgeItem:
    id: str = ""
    kind: str = ""  # entity, decision, recommendation, risk, pattern
    source: str = ""
    content: str = ""
    tags: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    created_at: float = 0.0


class KnowledgeEngine:
    def __init__(self, kernel: FabricKernel | None = None, reports_dir: str = ""):
        self._kernel = kernel or FabricKernel.instance()
        self._registry = get_registry()
        self._reports_dir = reports_dir or os.path.join(os.getcwd(), "Reports")
        self._reports: dict[str, ParsedReport] = {}
        self._knowledge_items: dict[str, KnowledgeItem] = {}
        self._lock = threading.RLock()
        self._indexed = False

    def index_reports(self, force: bool = False):
        if self._indexed and not force:
            return
        reports = parse_reports_directory(self._reports_dir)
        with self._lock:
            for report in reports:
                self._index_report(report)
            self._indexed = True

    def index_report(self, report: ParsedReport):
        with self._lock:
            self._index_report(report)

    def _index_report(self, report: ParsedReport):
        if not report or not report.title:
            return
        report_key = report.path
        self._reports[report_key] = report

        report_obj = EngineeringObject(
            object_type=EngineeringObjectType.REPORT,
            name=report.title,
            description=report.description,
            tags=report.tags + [f"cycle_{report.cycle}", f"seq_{report.sequence:02d}"],
            metadata={
                "path": report.path,
                "filename": report.filename,
                "cycle": report.cycle,
                "sequence": report.sequence,
                "word_count": report.word_count,
            },
        )
        self._registry.register(report_obj)

        for entity_name in report.entities:
            item_id = self._add_knowledge_item(
                kind="entity",
                content=entity_name,
                source=report.path,
                tags=["entity"] + report.tags,
            )
            rel = EngineeringRelationship(
                target_id=item_id,
                target_type="knowledge",
                relationship_type="mentions",
                label=f"Mentions {entity_name}",
            )
            report_obj.add_relationship(rel)

        for decision in report.decisions:
            self._add_knowledge_item(
                kind="decision",
                content=decision,
                source=report.path,
                tags=["decision"] + report.tags,
            )

        for rec in report.recommendations:
            self._add_knowledge_item(
                kind="recommendation",
                content=rec,
                source=report.path,
                tags=["recommendation"] + report.tags,
            )

        for risk in report.risks:
            self._add_knowledge_item(
                kind="risk",
                content=risk,
                source=report.path,
                tags=["risk"] + report.tags,
            )

        for pattern in report.patterns:
            self._add_knowledge_item(
                kind="pattern",
                content=pattern,
                source=report.path,
                tags=["pattern"] + report.tags,
            )

    def _add_knowledge_item(self, kind: str, content: str, source: str = "",
                            tags: list[str] | None = None) -> str:
        if not content.strip():
            return ""
        key = f"{kind}:{content[:80]}:{source}"
        if key in self._knowledge_items:
            return self._knowledge_items[key].id

        item = KnowledgeItem(
            kind=kind,
            source=source,
            content=content,
            tags=tags or [],
            created_at=time.time(),
        )
        self._knowledge_items[key] = item

        obj = EngineeringObject(
            object_type=EngineeringObjectType.KNOWLEDGE_NODE,
            name=f"{kind}: {content[:80]}",
            description=content,
            tags=(tags or []) + [kind],
            metadata={"source": source, "kind": kind},
        )
        self._registry.register(obj)
        item.id = obj.id
        return obj.id

    def search(self, query: str = "", kind: str = "",
               tag: str = "", limit: int = 50) -> list[EngineeringObject]:
        results = self._registry.search(query, limit=limit)
        if kind:
            results = [r for r in results if kind in r.tags]
        if tag:
            results = [r for r in results if tag in r.tags]
        return results[:limit]

    def search_reports(self, query: str = "",
                       cycle: int = 0, limit: int = 20) -> list[ParsedReport]:
        results = []
        for report in self._reports.values():
            if len(results) >= limit:
                break
            if cycle and report.cycle != cycle:
                continue
            q = query.lower()
            if (q in report.title.lower() or
                q in report.description.lower() or
                any(q in d.lower() for d in report.decisions) or
                any(q in e.lower() for e in report.entities)):
                results.append(report)
        return results

    def get_decisions(self, limit: int = 50) -> list[KnowledgeItem]:
        with self._lock:
            decisions = [item for item in self._knowledge_items.values()
                         if item.kind == "decision"]
            decisions.sort(key=lambda i: i.created_at, reverse=True)
            return decisions[:limit]

    def get_recommendations(self, limit: int = 50) -> list[KnowledgeItem]:
        with self._lock:
            recs = [item for item in self._knowledge_items.values()
                    if item.kind == "recommendation"]
            recs.sort(key=lambda i: i.created_at, reverse=True)
            return recs[:limit]

    def get_entities(self, limit: int = 100) -> list[KnowledgeItem]:
        with self._lock:
            ents = [item for item in self._knowledge_items.values()
                    if item.kind == "entity"]
            return ents[:limit]

    def summary(self) -> dict[str, Any]:
        with self._lock:
            report_count = len(self._reports)
            kinds: dict[str, int] = {}
            for item in self._knowledge_items.values():
                kinds[item.kind] = kinds.get(item.kind, 0) + 1
            return {
                "reports_indexed": report_count,
                "knowledge_items": len(self._knowledge_items),
                "by_kind": kinds,
                "indexed": self._indexed,
            }

    def clear(self):
        with self._lock:
            self._reports.clear()
            self._knowledge_items.clear()
            self._indexed = False
