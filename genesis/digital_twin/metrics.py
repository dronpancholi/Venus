"""
Repository Mathematics — compute repository-wide metrics from the Digital Twin.

Metrics computed:
  Architectural entropy        — distribution uniformity of nodes across kinds
  Information density          — avg edge-to-node ratio per kind
  Dependency centrality        — most-imported modules (hub factor)
  Knowledge centrality         — most-depended-upon nodes
  Evolution velocity           — avg change frequency
  Maintainability index        — composite (test coverage + layer compliance + low coupling)
  Specification completeness   — % specs with implementation links
  Architectural stability      — % nodes with stable layer assignment
  Module volatility            — % nodes with high churn
  Subsystem cohesion           — % of edges within same subsystem
  Repository complexity tensor — multi-dimensional complexity vector
  Graph diameter               — longest shortest path in import graph
  Architectural fractal score  — self-similarity across layers
  Semantic duplication index   — % duplicate class names
  Contract coverage            — % contracts with tests
  Capability maturity          — % capabilities with adjacent dependencies
  Repository intelligence score — composite platform intelligence
  Engineering leverage score   — ROI estimate for next change
"""

from __future__ import annotations

from collections import Counter, defaultdict
from math import log2, sqrt
from typing import Any

from genesis.digital_twin.model import DigitalTwin


class RepositoryMetrics:
    """Compute all repository mathematics from a Digital Twin."""

    def compute(self, twin: DigitalTwin) -> dict[str, Any]:
        m: dict[str, Any] = {}

        m["architectural_entropy"] = self._entropy(twin)
        m["information_density"] = self._info_density(twin)
        m["dependency_centrality"] = self._dependency_centrality(twin)
        m["knowledge_centrality"] = self._knowledge_centrality(twin)
        m["evolution_velocity"] = self._evolution_velocity(twin)
        m["maintainability_index"] = self._maintainability(twin)
        m["specification_completeness"] = self._spec_completeness(twin)
        m["architectural_stability"] = self._stability(twin)
        m["module_volatility"] = self._volatility(twin)
        m["subsystem_cohesion"] = self._cohesion(twin)
        m["complexity_tensor"] = self._complexity_tensor(twin)
        m["graph_diameter"] = self._graph_diameter(twin)
        m["architectural_fractal_score"] = self._fractal_score(twin)
        m["semantic_duplication_index"] = self._dup_index(twin)
        m["contract_coverage"] = self._contract_coverage(twin)
        m["capability_maturity"] = self._capability_maturity(twin)
        m["repository_intelligence_score"] = self._intelligence_score(m)
        m["engineering_leverage_score"] = self._leverage_score(m)

        twin.metrics = m
        return m

    def _entropy(self, twin: DigitalTwin) -> float:
        counts = twin.count_by_kind().values()
        total = sum(counts)
        if total == 0:
            return 0.0
        return -sum((c / total) * log2(c / total) for c in counts if c > 0)

    def _info_density(self, twin: DigitalTwin) -> float:
        if twin.node_count == 0:
            return 0.0
        return round(twin.edge_count / twin.node_count, 4)

    def _dependency_centrality(self, twin: DigitalTwin) -> dict[str, float]:
        in_degree: Counter = Counter()
        for edge in twin.find_edges("imports"):
            in_degree[edge[1]] += 1
        if not in_degree:
            return {}
        max_deg = max(in_degree.values())
        return {
            node: round(deg / max_deg, 4)
            for node, deg in in_degree.most_common(5)
        }

    def _knowledge_centrality(self, twin: DigitalTwin) -> dict[str, float]:
        dep_counts: Counter = Counter()
        for node in twin.nodes:
            for ref in node.depended_by:
                dep_counts[ref] += 1
        if not dep_counts:
            return {}
        max_c = max(dep_counts.values())
        return {
            node: round(c / max_c, 4)
            for node, c in dep_counts.most_common(5)
        }

    def _evolution_velocity(self, twin: DigitalTwin) -> float:
        changes = [n.change_frequency for n in twin.nodes]
        return round(sum(changes) / len(changes), 2) if changes else 0.0

    def _maintainability(self, twin: DigitalTwin) -> float:
        factors = []
        classes = twin.find_nodes(kind="class")
        tested = sum(1 for c in classes if c.test_count > 0)
        factors.append(tested / max(len(classes), 1))

        violations = twin.find_edges("imports")
        factors.append(1.0 if len(violations) < twin.node_count * 2 else 0.5)

        nodes_with_layer = sum(1 for n in twin.nodes if n.layer is not None)
        factors.append(nodes_with_layer / max(twin.node_count, 1))

        return round(sum(factors) / len(factors), 4) if factors else 0.0

    def _spec_completeness(self, twin: DigitalTwin) -> float:
        specs = twin.find_nodes(kind="normative")
        if not specs:
            return 1.0
        linked = 0
        for s in specs:
            edges = twin.edges_from(s.id)
            if any("implements" in str(e) for e in edges):
                linked += 1
        return round(linked / len(specs), 4)

    def _stability(self, twin: DigitalTwin) -> float:
        classes = twin.find_nodes(kind="class")
        with_layer = sum(1 for c in classes if c.layer is not None)
        return round(with_layer / max(len(classes), 1), 4)

    def _volatility(self, twin: DigitalTwin) -> float:
        files = twin.find_nodes(kind="file")
        if not files:
            return 0.0
        high_churn = sum(1 for f in files if f.change_frequency > 20)
        return round(high_churn / len(files), 4)

    def _cohesion(self, twin: DigitalTwin) -> float:
        subsystem_edges = 0
        total_edges = 0
        for edge in twin.find_edges("imports"):
            total_edges += 1
            sn = twin.get_node(edge[0])
            tn = twin.get_node(edge[1])
            if sn and tn and sn.layer == tn.layer:
                subsystem_edges += 1
        return round(subsystem_edges / max(total_edges, 1), 4)

    def _complexity_tensor(self, twin: DigitalTwin) -> dict[str, float]:
        kinds = twin.count_by_kind()
        total = twin.node_count or 1
        return {
            kind: round(count / total, 4)
            for kind, count in kinds.items()
        }

    def _graph_diameter(self, twin: DigitalTwin) -> int:
        import_edges = twin.find_edges("imports")
        if not import_edges:
            return 0
        adj: dict[str, set[str]] = defaultdict(set)
        for s, t, _ in import_edges:
            adj[s].add(t)
        nodes = list(adj.keys())
        if not nodes:
            return 0
        max_dist = 0
        for start in nodes[:20]:
            visited = {start}
            queue = [(start, 0)]
            for node, dist in queue:
                max_dist = max(max_dist, dist)
                for neighbor in adj.get(node, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
        return max_dist

    def _fractal_score(self, twin: DigitalTwin) -> float:
        layers = set()
        for n in twin.nodes:
            if n.layer is not None:
                layers.add(n.layer)
        if not layers:
            return 0.0
        layer_dists: dict[int, list[str]] = defaultdict(list)
        for n in twin.nodes:
            if n.layer is not None:
                layer_dists[n.layer].append(n.kind)
        kind_sets = [set(kinds) for kinds in layer_dists.values()]
        if len(kind_sets) < 2:
            return 1.0
        overlap = sum(len(a & b) for a in kind_sets for b in kind_sets if a is not b)
        pairs = len(kind_sets) * (len(kind_sets) - 1)
        return round(overlap / max(pairs, 1), 4)

    def _dup_index(self, twin: DigitalTwin) -> float:
        names = [n.label for n in twin.find_nodes(kind="class")]
        if not names:
            return 0.0
        dups = sum(count - 1 for count in Counter(names).values() if count > 1)
        return round(dups / len(names), 4)

    def _contract_coverage(self, twin: DigitalTwin) -> float:
        contracts = [
            n for n in twin.nodes
            if n.protocols or n.interfaces
        ]
        if not contracts:
            return 1.0
        tested = sum(1 for c in contracts if c.test_count > 0)
        return round(tested / len(contracts), 4)

    def _capability_maturity(self, twin: DigitalTwin) -> float:
        classes = twin.find_nodes(kind="class")
        if not classes:
            return 0.0
        with_deps = sum(1 for c in classes if len(c.depends_on) > 0 or len(c.depended_by) > 0)
        return round(with_deps / len(classes), 4)

    def _intelligence_score(self, m: dict[str, Any]) -> float:
        factors = [
            m.get("maintainability_index", 0),
            m.get("specification_completeness", 0),
            m.get("architectural_stability", 0),
            m.get("subsystem_cohesion", 0),
            m.get("contract_coverage", 0),
            m.get("capability_maturity", 0),
            1.0 - m.get("semantic_duplication_index", 0),
            1.0 - m.get("module_volatility", 0),
        ]
        return round(sum(factors) / len(factors), 4) if factors else 0.0

    def _leverage_score(self, m: dict[str, Any]) -> float:
        entropy = m.get("architectural_entropy", 0)
        maturity = m.get("capability_maturity", 0)
        completeness = m.get("specification_completeness", 0)
        intelligence = m.get("repository_intelligence_score", 0)
        return round((entropy * 0.2 + (1 - maturity) * 0.3 + (1 - completeness) * 0.2 + intelligence * 0.3), 4)
