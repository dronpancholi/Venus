"""
Sync Adapters — Bidirectional mappers between existing subsystems and BrainEntity.

Every adapter knows how to convert an external entity into a BrainEntity
and optionally how to push BrainEntity changes back.
"""

from __future__ import annotations

import time
from typing import Any

from genesis.brain.entity import (
    BrainEntity, BrainEntityType, Relationship, Confidence, Evidence,
    Lineage, Capability, RuntimeState, ResearchState,
)

try:
    from genesis.digital_twin.model import TwinNode
except ImportError:
    TwinNode = None

try:
    from genesis.core.uir import UIRNode
except ImportError:
    UIRNode = None

try:
    from genesis.civilization.knowledge import KnowledgeArtifact
except ImportError:
    KnowledgeArtifact = None

try:
    from genesis.civilization.agents.base import ResearchFinding
except ImportError:
    ResearchFinding = None

try:
    from genesis.intelligence.kgraph import KnowledgeGraph as VRIPKnowledgeGraph
except ImportError:
    VRIPKnowledgeGraph = None


class GraphAdapter:
    """Base class for all sync adapters."""

    SOURCE_SYSTEM: str = "unknown"

    def to_entity(self, obj: Any) -> BrainEntity:
        """Convert an external object to BrainEntity."""
        raise NotImplementedError

    def from_entity(self, entity: BrainEntity) -> Any | None:
        """Convert BrainEntity back to external format. Optional."""
        return None

    def extract_entities(self, container: Any) -> list[BrainEntity]:
        """Extract all BrainEntities from a container (e.g., a graph)."""
        return []


class DigitalTwinAdapter(GraphAdapter):
    """Sync adapter for genesis.digital_twin.model.DigitalTwin / TwinNode."""

    SOURCE_SYSTEM = "digital_twin"

    def to_entity(self, node: Any) -> BrainEntity:
        kwargs = {}
        if hasattr(node, "id"):
            kwargs["source_id"] = node.id
        if hasattr(node, "label"):
            kwargs["label"] = node.label
        if hasattr(node, "kind"):
            kwargs["entity_type"] = node.kind
        if hasattr(node, "purpose") and node.purpose:
            kwargs["description"] = node.purpose

        etype = getattr(node, "kind", "twin_node")
        twin_type_map = {
            "class": "class",
            "function": "function",
            "method": "method",
            "interface": "interface",
            "module": "module",
            "package": "package",
            "file": "module",
        }
        mapped = twin_type_map.get(etype, etype)
        kwargs["entity_type"] = mapped

        entity = BrainEntity(source_system=self.SOURCE_SYSTEM, **kwargs)

        if hasattr(node, "depends_on"):
            for dep in node.depends_on:
                entity.relationships.append(Relationship(target_id=dep, relation="depends_on"))

        if hasattr(node, "interfaces"):
            for iface in node.interfaces:
                entity.capabilities.append(Capability(name=iface, interface=iface))

        if hasattr(node, "tags"):
            entity.tags = list(node.tags)

        entity.evidence = Evidence(
            source_system=self.SOURCE_SYSTEM,
            confidence=getattr(node, "confidence", 1.0),
        )

        entity.runtime_state = RuntimeState(
            status=getattr(node, "service_name", "unknown"),
        )

        return entity

    def extract_entities(self, twin) -> list[BrainEntity]:
        if not hasattr(twin, "nodes"):
            return []
        return [self.to_entity(n) for n in twin.nodes if hasattr(n, "id")]


class UIRAdapter(GraphAdapter):
    """Sync adapter for genesis.core.uir.UIRNode."""

    SOURCE_SYSTEM = "uir"

    def to_entity(self, node: Any) -> BrainEntity:
        entity = BrainEntity(
            source_system=self.SOURCE_SYSTEM,
            source_id=getattr(node, "node_id", ""),
            label=getattr(node, "label", ""),
            entity_type=getattr(node, "semantic_type", "unknown"),
            attributes=dict(getattr(node, "attributes", {})),
        )
        return entity

    def extract_entities(self, graph) -> list[BrainEntity]:
        if not hasattr(graph, "nodes"):
            return []
        return [self.to_entity(n) for n in graph.nodes.values()]


class KnowledgeArtifactAdapter(GraphAdapter):
    """Sync adapter for genesis.civilization.knowledge.KnowledgeArtifact."""

    SOURCE_SYSTEM = "civilization_knowledge"

    def to_entity(self, artifact: Any) -> BrainEntity:
        entity = BrainEntity(
            source_system=self.SOURCE_SYSTEM,
            source_id=getattr(artifact, "id", ""),
            label=getattr(artifact, "title", ""),
            entity_type="knowledge_node",
            description=getattr(artifact, "content", "")[:500],
        )

        artifact_type = getattr(artifact, "artifact_type", "")
        if artifact_type:
            entity.attributes["artifact_type"] = artifact_type

        domain = getattr(artifact, "domain", "")
        if domain:
            entity.attributes["domain"] = domain

        findings = getattr(artifact, "findings", [])
        entity.research_state.findings_count = len(findings)

        evidence_list = getattr(artifact, "evidence", [])
        entity.research_state = ResearchState(
            findings_count=len(findings),
            average_confidence=getattr(artifact, "confidence", 0.0),
        )

        lineage = getattr(artifact, "lineage", [])
        for parent_id in lineage:
            entity.lineage.derivation_path.append(parent_id)
            entity.relationships.append(
                Relationship(target_id=parent_id, relation="derives_from")
            )

        tags = getattr(artifact, "tags", [])
        entity.tags = list(tags) if tags else []

        entity.confidence.overall = getattr(artifact, "confidence", 1.0)

        entity.evidence = Evidence(
            source_system=self.SOURCE_SYSTEM,
            source_file=getattr(artifact, "source", ""),
        )

        entity.attributes["status"] = getattr(artifact, "status", "")

        return entity

    def from_entity(self, entity: BrainEntity) -> dict[str, Any] | None:
        if entity.source_system != self.SOURCE_SYSTEM:
            return None
        return {
            "id": entity.source_id or entity.brain_id,
            "title": entity.label,
            "content": entity.description,
            "domain": entity.attributes.get("domain", ""),
            "confidence": entity.confidence.overall,
            "tags": entity.tags,
        }


class FindingAdapter(GraphAdapter):
    """Sync adapter for genesis.civilization.agents.base.ResearchFinding."""

    SOURCE_SYSTEM = "civilization_agents"

    def to_entity(self, finding: Any) -> BrainEntity:
        entity = BrainEntity(
            source_system=self.SOURCE_SYSTEM,
            source_id=getattr(finding, "id", ""),
            label=getattr(finding, "title", ""),
            entity_type="finding",
            description=getattr(finding, "description", "")[:500],
        )

        entity.confidence.overall = getattr(finding, "confidence", 0.0)
        entity.tags = list(getattr(finding, "tags", []))
        entity.research_state = ResearchState(
            findings_count=1,
            citations_count=len(getattr(finding, "citations", [])),
            average_confidence=entity.confidence.overall,
        )
        entity.evidence = Evidence(
            source_system=self.SOURCE_SYSTEM,
            raw_data={"evidence": getattr(finding, "evidence", "")},
        )

        return entity


class VRIPAdapter(GraphAdapter):
    """Sync adapter for genesis.intelligence.kgraph.KnowledgeGraph (VRIP)."""

    SOURCE_SYSTEM = "vrip"

    def to_entity(self, node_data: dict[str, Any]) -> BrainEntity:
        return BrainEntity(
            source_system=self.SOURCE_SYSTEM,
            source_id=node_data.get("id", ""),
            label=node_data.get("label", ""),
            entity_type=node_data.get("type", "knowledge_node"),
            attributes={k: v for k, v in node_data.items()
                       if k not in ("id", "label", "type")},
        )

    def extract_entities(self, kg) -> list[BrainEntity]:
        if not hasattr(kg, "nodes"):
            return []
        entities = []
        for node_list in kg.nodes.values():
            for node_data in node_list:
                if isinstance(node_data, dict):
                    entities.append(self.to_entity(node_data))
        return entities


class GraphDBAdapter(GraphAdapter):
    """Sync adapter for genesis.graphdb's Node objects."""

    SOURCE_SYSTEM = "graphdb"

    def to_entity(self, node) -> BrainEntity:
        attrs = getattr(node, "attributes", {}) or {}

        entity = BrainEntity(
            source_system=self.SOURCE_SYSTEM,
            source_id=getattr(node, "uid", ""),
            label=getattr(node, "name", ""),
            entity_type=getattr(node, "node_type", "entity"),
            description=getattr(node, "description", ""),
        )

        entity.confidence.overall = getattr(node, "confidence", 1.0)
        entity.tags = list(getattr(node, "tags", []) or [])
        entity.attributes = attrs

        return entity

    def extract_entities(self, graphdb) -> list[BrainEntity]:
        if hasattr(graphdb, "query"):
            nodes = graphdb.query().execute()
            return [self.to_entity(n) for n in nodes]
        return []


# ——— Adapter Registry ———

ADAPTERS: dict[str, GraphAdapter] = {
    DigitalTwinAdapter.SOURCE_SYSTEM: DigitalTwinAdapter(),
    UIRAdapter.SOURCE_SYSTEM: UIRAdapter(),
    KnowledgeArtifactAdapter.SOURCE_SYSTEM: KnowledgeArtifactAdapter(),
    FindingAdapter.SOURCE_SYSTEM: FindingAdapter(),
    VRIPAdapter.SOURCE_SYSTEM: VRIPAdapter(),
    GraphDBAdapter.SOURCE_SYSTEM: GraphDBAdapter(),
}


def get_adapter(source_system: str) -> GraphAdapter | None:
    return ADAPTERS.get(source_system)


def register_adapter(name: str, adapter: GraphAdapter) -> None:
    ADAPTERS[name] = adapter
