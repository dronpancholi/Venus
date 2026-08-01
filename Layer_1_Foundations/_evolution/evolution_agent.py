#!/usr/bin/env python3
"""
VENUS SELF-EVOLUTION AGENT — Phase 9

Automated structural review, dedup, consolidation, and migration.

Usage:
  python3 evolution_agent.py --mode=review
  python3 evolution_agent.py --mode=dedup
  python3 evolution_agent.py --mode=consolidate
"""

import argparse
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
GRAPH_DIR = ROOT_DIR / "Layer_1_Foundations" / "_graph"
REGISTRY_DIR = ROOT_DIR / "Layer_1_Foundations" / "_registry"
RULES_DIR = ROOT_DIR / "Layer_1_Foundations" / "_rule_engine"


class EvolutionAgent:
    def __init__(self):
        self.catalog: dict = {}
        self.dep_graph: list[dict] = []
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.proposals: list[dict] = []
        self._load()

    def _load(self):
        catalog_path = REGISTRY_DIR / "catalog.json"
        if catalog_path.exists():
            self.catalog = json.loads(catalog_path.read_text())

        dep_path = REGISTRY_DIR / "dependency_graph.json"
        if dep_path.exists():
            self.dep_graph = json.loads(dep_path.read_text())

        nodes_path = GRAPH_DIR / "semantic_graph.nodes.json"
        if nodes_path.exists():
            self.nodes = json.loads(nodes_path.read_text())

        edges_path = GRAPH_DIR / "semantic_graph.edges.json"
        if edges_path.exists():
            self.edges = json.loads(edges_path.read_text())

    def review(self) -> list[dict]:
        """Full structural review."""
        findings = []
        findings.extend(self._find_orphans())
        findings.extend(self._find_density_clusters())
        findings.extend(self._find_circular_deps())
        return findings

    def dedup(self, threshold: float = 0.8) -> list[dict]:
        """Find duplicate entities by name similarity."""
        groups = defaultdict(list)
        # Normalize names
        for eid, entry in self.catalog.items():
            name = entry.get("name", eid)
            normal = re.sub(r"[^a-z0-9]", "", name.lower())
            groups[entry.get("type", "unknown")].append((eid, name, normal))

        proposals = []
        for etype, items in groups.items():
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    sim = SequenceMatcher(None, items[i][2], items[j][2]).ratio()
                    if sim >= threshold:
                        proposals.append({
                            "type": "deduplication",
                            "confidence": round(sim, 4),
                            "primary": items[i][0],
                            "secondary": items[j][0],
                            "names": (items[i][1], items[j][1]),
                            "etype": etype,
                        })
        return proposals

    def consolidate(self) -> list[dict]:
        """Find entities with overlapping dependencies."""
        dep_map = defaultdict(set)
        for edge in self.edges:
            dep_map[edge["source"]].add(edge["target"])

        proposals = []
        sources = list(dep_map.keys())
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                overlap = dep_map[sources[i]] & dep_map[sources[j]]
                total = dep_map[sources[i]] | dep_map[sources[j]]
                if total and len(overlap) / len(total) > 0.5:
                    proposals.append({
                        "type": "consolidation",
                        "overlap_ratio": round(len(overlap) / len(total), 4),
                        "entities": (sources[i], sources[j]),
                        "shared_deps": list(overlap),
                    })
        return proposals

    def _find_orphans(self) -> list[dict]:
        """Entities with no incoming or outgoing edges."""
        if not self.nodes:
            return []

        node_ids = {n["id"] for n in self.nodes}
        referenced = set()
        for e in self.edges:
            referenced.add(e["source"])
            referenced.add(e["target"])

        orphans = node_ids - referenced
        return [{
            "type": "orphan",
            "severity": "medium",
            "entity_id": oid,
            "detail": "No edges of any kind in semantic graph",
        } for oid in sorted(orphans)]

    def _find_density_clusters(self) -> list[dict]:
        """Identify high-density clusters for possible consolidation."""
        clusters = defaultdict(list)
        for e in self.edges:
            cluster_key = (e["source"][:3], e["type"])
            clusters[cluster_key].append(e)

        return [{
            "type": "density_cluster",
            "severity": "info",
            "prefix_group": k[0],
            "edge_type": k[1],
            "edge_count": len(v),
        } for k, v in sorted(clusters.items(), key=lambda x: -len(x[1]))
          if len(v) > 20]

    def _find_circular_deps(self) -> list[dict]:
        """Find circular dependency chains."""
        adj = defaultdict(set)
        for e in self.edges:
            if e["type"] in ("depends_on", "references"):
                adj[e["source"]].add(e["target"])

        # Simple cycle detection via DFS
        cycles = []
        visited = set()
        path = []

        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            for neighbor in adj.get(node, set()):
                dfs(neighbor)
            path.pop()

        for node in list(adj.keys())[:100]:
            dfs(node)

        return [{
            "type": "circular_dependency",
            "severity": "high",
            "cycle": cycle,
        } for cycle in cycles[:10]]

    def run(self, mode: str):
        if mode == "review":
            findings = self.review()
            print(f"── Structural Review ──")
            self._print_findings(findings)

        elif mode == "dedup":
            proposals = self.dedup()
            print(f"── Deduplication ──")
            print(f"  Candidates found: {len(proposals)}")
            for p in proposals[:20]:
                print(f"  [{p['etype']}] {p['names'][0]} ↔ {p['names'][1]} (conf={p['confidence']})")

        elif mode == "consolidate":
            proposals = self.consolidate()
            print(f"── Consolidation ──")
            print(f"  Potential consolidations: {len(proposals)}")
            for p in proposals[:10]:
                print(f"  Overlap={p['overlap_ratio']}: {p['entities'][0]} ↔ {p['entities'][1]}")

    def _print_findings(self, findings):
        by_type = defaultdict(list)
        for f in findings:
            by_type[f["type"]].append(f)

        for ftype, items in sorted(by_type.items()):
            severities = defaultdict(list)
            for item in items:
                severities[item.get("severity", "info")].append(item)
            for sev, sitems in sorted(severities.items()):
                print(f"  {sev.upper()}: {ftype} — {len(sitems)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Venus Self-Evolution Agent")
    parser.add_argument("--mode", choices=["review", "dedup", "consolidate"], required=True)
    args = parser.parse_args()

    agent = EvolutionAgent()
    agent.run(args.mode)
