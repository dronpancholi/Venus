from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class EvidenceNode:
    id: str
    label: str
    evidence: str = ""
    confidence: float = 1.0
    source: str = ""
    type: str = "observation"


@dataclass
class EvidenceEdge:
    source_id: str
    target_id: str
    relationship: str = "supports"
    weight: float = 1.0


@dataclass
class EvidenceGraph:
    nodes: list[EvidenceNode] = field(default_factory=list)
    edges: list[EvidenceEdge] = field(default_factory=list)

    def add_node(self, node: EvidenceNode):
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: EvidenceEdge):
        self.edges.append(edge)


class VisualReasoningEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._graphs: list[EvidenceGraph] = []
        self._vr_obj: EngineeringObject | None = None

    def boot(self):
        self._vr_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="VisualReasoningEngine",
            description="Explainable recommendations with evidence graphs",
            tags=["reasoning", "visual", "evidence"],
        )
        self._registry.register(self._vr_obj)

    def build_evidence_graph(self, recommendation: str,
                             reasoning: dict[str, Any] | None = None) -> EvidenceGraph:
        graph = EvidenceGraph()
        rec_node = EvidenceNode(
            id=f"rec_{int(time.time() * 1000)}",
            label=recommendation[:80],
            evidence=recommendation,
            type="recommendation",
            confidence=0.7,
        )
        graph.add_node(rec_node)

        if reasoning:
            for key, value in reasoning.items():
                if isinstance(value, dict):
                    obs_node = EvidenceNode(
                        id=f"obs_{key}",
                        label=key,
                        evidence=value.get("summary", str(value)),
                        confidence=value.get("confidence", 0.5),
                        type="observation",
                        source=value.get("source", "reasoning"),
                    )
                    graph.add_node(obs_node)
                    graph.add_edge(EvidenceEdge(
                        source_id=obs_node.id,
                        target_id=rec_node.id,
                        relationship="supports",
                        weight=obs_node.confidence,
                    ))
                    for dep in value.get("dependencies", []):
                        dep_node = EvidenceNode(
                            id=f"dep_{dep}",
                            label=str(dep)[:60],
                            evidence=str(dep),
                            type="dependency",
                            source=key,
                        )
                        graph.add_node(dep_node)
                        graph.add_edge(EvidenceEdge(
                            source_id=dep_node.id,
                            target_id=obs_node.id,
                            relationship="depends_on",
                        ))

        self._graphs.append(graph)
        obj = EngineeringObject(
            object_type=EngineeringObjectType.RECOMMENDATION,
            name=f"Evidence: {recommendation[:40]}...",
            description=recommendation[:200],
            tags=["evidence", "recommendation"],
            metadata={
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "recommendation": recommendation,
            },
        )
        self._registry.register(obj)
        return graph

    def list_graphs(self, limit: int = 10) -> list[dict[str, Any]]:
        return [
            {
                "nodes": len(g.nodes),
                "edges": len(g.edges),
                "recommendations": [n.label for n in g.nodes if n.type == "recommendation"],
            }
            for g in self._graphs[-limit:]
        ]

    def summary(self) -> dict[str, Any]:
        return {
            "total_graphs": len(self._graphs),
            "total_nodes": sum(len(g.nodes) for g in self._graphs),
            "total_edges": sum(len(g.edges) for g in self._graphs),
        }
