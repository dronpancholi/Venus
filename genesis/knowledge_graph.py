"""
GENESIS-VIII Program 6: Planetary Knowledge Graph.

Ingest millions of engineering entities: repositories, packages, libraries,
frameworks, RFCs, standards, CVEs, research papers, organizations,
contributors, architectures, languages, patterns, protocols, specifications.

Builds: global graph, semantic graph, temporal graph, lineage graph,
causal graph, technology evolution graph.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class EntityDomain(Enum):
    REPOSITORY = "repository"
    PACKAGE = "package"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    RFC = "rfc"
    STANDARD = "standard"
    CVE = "cve"
    RESEARCH_PAPER = "research_paper"
    ORGANIZATION = "organization"
    CONTRIBUTOR = "contributor"
    ARCHITECTURE = "architecture"
    LANGUAGE = "language"
    PATTERN = "pattern"
    PROTOCOL = "protocol"
    SPECIFICATION = "specification"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"


class GraphType(Enum):
    GLOBAL = "global"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    LINEAGE = "lineage"
    CAUSAL = "causal"
    EVOLUTION = "evolution"


@dataclass
class KEntity:
    id: str = ""
    name: str = ""
    domain: EntityDomain = EntityDomain.CONCEPT
    description: str = ""
    aliases: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    source_url: str = ""
    confidence: float = 1.0
    created_at: float = 0.0
    updated_at: float = 0.0
    graph_types: list[GraphType] = field(default_factory=lambda: [GraphType.GLOBAL])

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ke", 10)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now


@dataclass
class KRelation:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    graph_types: list[GraphType] = field(default_factory=lambda: [GraphType.GLOBAL])

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("kr", 12)
        if not self.created_at:
            self.created_at = time.time()


class KnowledgeGraph:
    """Planetary knowledge graph with multiple graph views."""

    def __init__(self):
        self._entities: dict[str, KEntity] = {}
        self._relations: dict[str, KRelation] = {}
        self._index_by_domain: dict[str, set[str]] = {}
        self._index_by_tag: dict[str, set[str]] = {}
        self._index_by_graph: dict[str, set[str]] = {}
        self._relation_index_by_type: dict[str, set[str]] = {}
        self._neighbors: dict[str, set[str]] = {}

    @property
    def entity_count(self) -> int:
        return len(self._entities)

    @property
    def relation_count(self) -> int:
        return len(self._relations)

    def add_entity(self, entity: KEntity) -> KEntity:
        self._entities[entity.id] = entity
        self._index_by_domain.setdefault(entity.domain.value, set()).add(entity.id)
        for tag in entity.tags:
            self._index_by_tag.setdefault(tag, set()).add(entity.id)
        for gt in entity.graph_types:
            self._index_by_graph.setdefault(gt.value, set()).add(entity.id)
        return entity

    def add_relation(self, relation: KRelation) -> KRelation:
        self._relations[relation.id] = relation
        self._relation_index_by_type.setdefault(relation.relation_type, set()).add(relation.id)
        self._neighbors.setdefault(relation.source_id, set()).add(relation.target_id)
        self._neighbors.setdefault(relation.target_id, set()).add(relation.source_id)
        for gt in relation.graph_types:
            self._index_by_graph.setdefault(gt.value, set()).add(relation.id)
        return relation

    def relate(self, source_id: str, target_id: str, relation_type: str,
               weight: float = 1.0, properties: dict[str, Any] | None = None,
               graph_types: list[GraphType] | None = None) -> KRelation | None:
        if source_id not in self._entities or target_id not in self._entities:
            return None
        return self.add_relation(KRelation(
            source_id=source_id, target_id=target_id,
            relation_type=relation_type, weight=weight,
            properties=properties or {},
            graph_types=graph_types or [GraphType.GLOBAL],
        ))

    def get_entity(self, entity_id: str) -> KEntity | None:
        return self._entities.get(entity_id)

    def find_entities(self, name_contains: str = "", domain: EntityDomain | None = None,
                       tag: str = "", graph_type: GraphType | None = None) -> list[KEntity]:
        results = list(self._entities.values())
        if domain:
            ids = self._index_by_domain.get(domain.value, set())
            results = [e for e in results if e.id in ids]
        if tag:
            ids = self._index_by_tag.get(tag, set())
            results = [e for e in results if e.id in ids]
        if graph_type:
            ids = self._index_by_graph.get(graph_type.value, set())
            results = [e for e in results if e.id in ids]
        if name_contains:
            results = [e for e in results if name_contains.lower() in e.name.lower()]
        return sorted(results, key=lambda e: e.name)

    def neighbors_of(self, entity_id: str, relation_type: str = "") -> list[KEntity]:
        neighbor_ids = self._neighbors.get(entity_id, set())
        results = []
        for nid in neighbor_ids:
            if relation_type:
                matching = [r for r in self._relations.values()
                           if r.source_id == entity_id and r.target_id == nid
                           and r.relation_type == relation_type]
                if not matching:
                    continue
            e = self._entities.get(nid)
            if e:
                results.append(e)
        return results

    def subgraph(self, graph_type: GraphType) -> dict[str, Any]:
        eids = self._index_by_graph.get(graph_type.value, set())
        entities = {eid: self._entities[eid] for eid in eids if eid in self._entities}
        rids = self._index_by_graph.get(graph_type.value, set())
        relations = {rid: self._relations[rid] for rid in rids if rid in self._relations
                     and self._relations[rid].source_id in entities
                     and self._relations[rid].target_id in entities}
        return {"entities": entities, "relations": relations}

    def global_graph(self) -> dict[str, Any]:
        return self.subgraph(GraphType.GLOBAL)

    def graph_for_domain(self, domain: EntityDomain) -> dict[str, Any]:
        eids = self._index_by_domain.get(domain.value, set())
        entities = {eid: self._entities[eid] for eid in eids if eid in self._entities}
        eid_set = set(entities)
        relations = {rid: r for rid, r in self._relations.items()
                     if r.source_id in eid_set and r.target_id in eid_set}
        return {"entities": entities, "relations": relations}

    def query(self, cypher_like: str) -> list[KEntity]:
        """Simple pattern matcher: MATCH (n:Domain) WHERE n.name CONTAINS 'x'."""
        results = list(self._entities.values())
        parts = cypher_like.lower().split()
        for i, p in enumerate(parts):
            if p.startswith(":") and i > 0:
                domain = p[1:]
                results = [e for e in results if e.domain.value == domain]
            if p == "contains" and i + 1 < len(parts):
                search = parts[i + 1].strip("'\"")
                results = [e for e in results if search in e.name.lower()]
        return results

    def summary(self) -> dict[str, Any]:
        domain_counts: dict[str, int] = {}
        for e in self._entities.values():
            domain_counts[e.domain.value] = domain_counts.get(e.domain.value, 0) + 1
        rel_type_counts: dict[str, int] = {}
        for r in self._relations.values():
            rel_type_counts[r.relation_type] = rel_type_counts.get(r.relation_type, 0) + 1
        return {
            "entities": len(self._entities),
            "relations": len(self._relations),
            "by_domain": domain_counts,
            "by_relation_type": rel_type_counts,
            "graph_types": [gt.value for gt in GraphType],
            "domains": [d.value for d in EntityDomain],
        }


class PlanetaryKnowledgeGraph:
    """Planetary-scale knowledge graph with ingestion pipelines."""

    def __init__(self):
        self._graphs: dict[GraphType, KnowledgeGraph] = {
            gt: KnowledgeGraph() for gt in GraphType
        }
        self._ingestion_stats: dict[str, int] = {}

    @property
    def global_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.GLOBAL]

    @property
    def semantic_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.SEMANTIC]

    @property
    def temporal_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.TEMPORAL]

    @property
    def lineage_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.LINEAGE]

    @property
    def causal_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.CAUSAL]

    @property
    def evolution_graph(self) -> KnowledgeGraph:
        return self._graphs[GraphType.EVOLUTION]

    def ingest_entity(self, entity: KEntity):
        for gt in entity.graph_types:
            self._graphs[gt].add_entity(entity)
        self._ingestion_stats["entities"] = self._ingestion_stats.get("entities", 0) + 1

    def ingest_relation(self, relation: KRelation):
        for gt in relation.graph_types:
            self._graphs[gt].add_relation(relation)
        self._ingestion_stats["relations"] = self._ingestion_stats.get("relations", 0) + 1

    def ingest_repository(self, name: str, language: str,
                           stars: int = 0, description: str = "") -> KEntity:
        return self._graphs[GraphType.GLOBAL].add_entity(KEntity(
            name=name, domain=EntityDomain.REPOSITORY,
            description=description,
            properties={"language": language, "stars": stars},
            tags=["repository", language, "open_source"],
        ))

    def ingest_package(self, name: str, ecosystem: str,
                        version: str = "latest") -> KEntity:
        return self._graphs[GraphType.GLOBAL].add_entity(KEntity(
            name=name, domain=EntityDomain.PACKAGE,
            properties={"ecosystem": ecosystem, "version": version},
            tags=["package", ecosystem],
        ))

    def ingest_cve(self, cve_id: str, severity: str,
                    affected: list[str]) -> KEntity:
        entity = KEntity(
            name=cve_id, domain=EntityDomain.CVE,
            description=f"CVE: {cve_id} (severity: {severity})",
            properties={"severity": severity, "affected": affected},
            tags=["security", "vulnerability", severity],
        )
        self._graphs[GraphType.GLOBAL].add_entity(entity)
        self._graphs[GraphType.CAUSAL].add_entity(entity)
        for dep in affected:
            self._graphs[GraphType.GLOBAL].add_relation(KRelation(
                source_id=entity.id,
                target_id=self._find_or_create_entity(dep).id,
                relation_type="affects", weight=1.0,
                graph_types=[GraphType.GLOBAL, GraphType.CAUSAL],
            ))
        return entity

    def _find_or_create_entity(self, name: str,
                                domain: EntityDomain = EntityDomain.PACKAGE) -> KEntity:
        for e in self._graphs[GraphType.GLOBAL].find_entities(name_contains=name):
            if e.name == name:
                return e
        return self._graphs[GraphType.GLOBAL].add_entity(KEntity(
            name=name, domain=domain,
        ))

    def summary(self) -> dict[str, Any]:
        return {
            "graphs": {gt.value: self._graphs[gt].summary() for gt in GraphType},
            "ingestion": self._ingestion_stats,
        }
