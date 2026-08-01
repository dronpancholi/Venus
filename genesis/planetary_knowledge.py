"""
GENESIS-IX Phase 7: Planetary Engineering Knowledge.

Expanded acquisition + knowledge graph across GitHub, GitLab, PyPI, npm,
Cargo, Maven, NuGet, Docker Hub, RFCs, OWASP, CVEs, NIST, CNCF, W3C,
IETF, Linux, LLVM, Kubernetes, TensorFlow, PyTorch.

Builds a planetary engineering knowledge graph.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class SourceDomain(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    PYPI = "pypi"
    NPM = "npm"
    CARGO = "cargo"
    MAVEN = "maven"
    NUGET = "nuget"
    DOCKER = "docker"
    RFC = "rfc"
    OWASP = "owasp"
    CVE = "cve"
    NIST = "nist"
    CNCF = "cncf"
    W3C = "w3c"
    IETF = "ietf"
    LINUX = "linux"
    LLVM = "llvm"
    KUBERNETES = "kubernetes"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"


@dataclass
class Artifact:
    id: str = ""
    name: str = ""
    domain: SourceDomain = SourceDomain.GITHUB
    version: str = ""
    description: str = ""
    source_url: str = ""
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: float = 0.0
    last_updated: float = 0.0
    confidence: float = 1.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("art", 10)
        now = time.time()
        if not self.discovered_at:
            self.discovered_at = now
        if not self.last_updated:
            self.last_updated = now


class SourceConnector:
    """Generic connector for an external knowledge source."""

    def __init__(self, domain: SourceDomain):
        self._domain = domain
        self._artifacts: dict[str, Artifact] = {}
        self._relation_graph: dict[str, set[str]] = defaultdict(set)

    @property
    def domain(self) -> SourceDomain:
        return self._domain

    def ingest(self, artifact: Artifact):
        self._artifacts[artifact.id] = artifact
        for dep in artifact.dependencies:
            self._relation_graph[artifact.id].add(dep)

    def get(self, artifact_id: str) -> Artifact | None:
        return self._artifacts.get(artifact_id)

    def find(self, name_contains: str = "", tag: str = "",
              domain: SourceDomain | None = None) -> list[Artifact]:
        results = list(self._artifacts.values())
        if name_contains:
            results = [a for a in results if name_contains.lower() in a.name.lower()]
        if tag:
            results = [a for a in results if tag in a.tags]
        if domain:
            results = [a for a in results if a.domain == domain]
        return results

    def dependencies_of(self, artifact_id: str) -> list[Artifact]:
        dep_ids = self._relation_graph.get(artifact_id, set())
        return [self._artifacts[did] for did in dep_ids if did in self._artifacts]

    @property
    def count(self) -> int:
        return len(self._artifacts)


class PlanetaryKnowledgeEngine:
    """Planetary-scale engineering knowledge integration."""

    def __init__(self):
        self._connectors: dict[SourceDomain, SourceConnector] = {
            d: SourceConnector(d) for d in SourceDomain
        }
        self._global_dependency_graph: dict[str, set[str]] = defaultdict(set)
        self._tech_stack_map: dict[str, set[str]] = defaultdict(set)
        self._ingestion_stats: dict[str, int] = defaultdict(int)

    def connector(self, domain: SourceDomain) -> SourceConnector:
        return self._connectors[domain]

    def ingest(self, artifact: Artifact):
        self._connectors[artifact.domain].ingest(artifact)
        for dep in artifact.dependencies:
            self._global_dependency_graph[artifact.id].add(dep)
        for tag in artifact.tags:
            self._tech_stack_map[tag].add(artifact.id)
        self._ingestion_stats[artifact.domain.value] += 1

    def query(self, name_contains: str = "", tag: str = "",
               domain: SourceDomain | None = None) -> list[Artifact]:
        results = []
        for conn in self._connectors.values():
            if domain and conn.domain != domain:
                continue
            results.extend(conn.find(name_contains=name_contains, tag=tag))
        return results

    def dependency_chain(self, artifact_id: str, max_depth: int = 5) -> list[list[str]]:
        chains: list[list[str]] = []
        queue: list[tuple[str, list[str]]] = [(artifact_id, [artifact_id])]
        visited: set[str] = set()
        while queue and len(chains) < 10:
            current, path = queue.pop(0)
            if current in visited and current != artifact_id:
                continue
            visited.add(current)
            deps = self._global_dependency_graph.get(current, set())
            if not deps or len(path) >= max_depth:
                chains.append(path)
                continue
            for dep in deps:
                queue.append((dep, path + [dep]))
        return chains

    def ecosystem_overview(self) -> dict[str, Any]:
        domain_counts = {d.value: conn.count for d, conn in self._connectors.items()}
        return {
            "total_artifacts": sum(conn.count for conn in self._connectors.values()),
            "by_domain": domain_counts,
            "total_dependencies": sum(len(deps) for deps in self._global_dependency_graph.values()),
            "unique_technologies": len(self._tech_stack_map),
            "ingestion": dict(self._ingestion_stats),
        }

    def summary(self) -> dict[str, Any]:
        return self.ecosystem_overview()
