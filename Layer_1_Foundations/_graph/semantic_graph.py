#!/usr/bin/env python3
"""
VENUS SEMANTIC KNOWLEDGE GRAPH — Phase 6

Upgrades the knowledge graph from file-reference tracking to 
semantic meaning. Builds typed nodes and edges with inference.

Usage:
  python3 semantic_graph.py [--rebuild] [--infer]
"""

import argparse
import json
from collections import deque
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
GRAPH_DIR = ROOT_DIR / "Layer_1_Foundations" / "_graph"
REGISTRY_DIR = ROOT_DIR / "Layer_1_Foundations" / "_registry"
ONTOLOGY_PATH = ROOT_DIR / "Layer_1_Foundations" / "_ontology" / "ontology.types.json"
SEMANTIC_TYPES_PATH = GRAPH_DIR / "semantic_types.json"


class SemanticGraph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.inference_rules: list[dict] = []
        self._load_types()

    def _load_types(self):
        if SEMANTIC_TYPES_PATH.exists():
            data = json.loads(SEMANTIC_TYPES_PATH.read_text())
            self.inference_rules = data.get("inference_rules", [])

    def add_node(self, node_id: str, node_type: str, label: str, **attrs):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label,
                **attrs,
            }

    def add_edge(self, source: str, target: str, edge_type: str, **attrs):
        self.edges.append({
            "source": source,
            "target": target,
            "type": edge_type,
            **attrs,
        })

    def build_from_catalog(self, catalog: dict, dep_graph: list[dict]):
        """Upgrade existing catalog into semantic graph."""
        semantic_edges_added = 0

        for eid, entry in catalog.items():
            etype = entry.get("type", "unknown")
            name = entry.get("name", eid)

            # Map to semantic type
            semantic_type = self._map_to_semantic_type(etype)
            self.add_node(eid, semantic_type, name, layer=entry.get("layer", 0))

        for edge in dep_graph:
            src = edge.get("source")
            tgt = edge.get("target")
            etype = edge.get("type", "references")

            # Map to semantic edge
            semantic_etype = self._map_to_semantic_edge(etype)
            self.add_edge(src, tgt, semantic_etype)
            semantic_edges_added += 1

        return semantic_edges_added

    def infer(self):
        """Apply inference rules to derive new edges."""
        inferred = 0

        for rule in self.inference_rules:
            if rule["rule"] == "transitive_dependency":
                inferred += self._infer_transitive("depends_on", "depends_on")
            elif rule["rule"] == "inheritance_chain":
                inferred += self._infer_transitive("inherits", "inherits")
            elif rule["rule"] == "composition_transitivity":
                inferred += self._infer_transitive("contains", "contains")
            elif rule["rule"] == "policy_coverage":
                inferred += self._infer_transitive_through("governs", "depends_on", "governs")

        return inferred

    def _infer_transitive(self, edge_type: str, new_type: str) -> int:
        """If A ->[type] B and B ->[type] C, add A ->[type] C."""
        adj = {}
        for e in self.edges:
            if e["type"] == edge_type:
                adj.setdefault(e["source"], set()).add(e["target"])

        count = 0
        for source in adj:
            visited = set()
            queue = deque(adj.get(source, []))
            while queue:
                target = queue.popleft()
                if target in visited or target == source:
                    continue
                visited.add(target)
                if target in adj:
                    for next_t in adj[target]:
                        if next_t not in visited and next_t != source:
                            queue.append(next_t)
                # Add transitive edge if not direct
                if not any(e["source"] == source and e["target"] == target and e["type"] == new_type for e in self.edges):
                    self.add_edge(source, target, new_type, inferred=True)
                    count += 1
        return count

    def _infer_transitive_through(self, edge_a: str, edge_b: str, new_type: str) -> int:
        """If A ->[A] B and B ->[B] C, add A ->[new] C."""
        forward = {}
        backward = {}
        for e in self.edges:
            if e["type"] == edge_a:
                forward.setdefault(e["source"], set()).add(e["target"])
            if e["type"] == edge_b:
                backward.setdefault(e["source"], set()).add(e["target"])

        count = 0
        for source in forward:
            for mid in forward[source]:
                if mid in backward:
                    for target in backward[mid]:
                        if not any(e["source"] == source and e["target"] == target and e["type"] == new_type for e in self.edges):
                            self.add_edge(source, target, new_type, inferred=True)
                            count += 1
        return count

    @staticmethod
    def _map_to_semantic_type(etype: str) -> str:
        mapping = {
            "part": "artifact", "module": "artifact", "engine": "artifact",
            "template": "artifact", "stage": "artifact", "os_version": "artifact",
            "schema": "artifact", "certificate": "artifact", "constitution": "artifact",
            "layer": "context", "policy": "policy", "agent": "agent",
            "memory": "memory", "configuration": "artifact",
            "concept": "concept", "principle": "concept", "rule": "policy",
            "workflow": "workflow", "pipeline": "execution", "runtime": "execution",
        }
        return mapping.get(etype, "entity")

    @staticmethod
    def _map_to_semantic_edge(etype: str) -> str:
        mapping = {
            "contains": "contains",
            "references": "references",
            "depends_on": "depends_on",
            "inherits": "inherits",
            "validates": "validates",
            "produces": "produces",
            "implements": "implements",
            "satisfies": "satisfies",
            "triggers": "triggers",
            "governs": "governs",
        }
        return mapping.get(etype, "references")

    def write(self):
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        nodes_path = GRAPH_DIR / "semantic_graph.nodes.json"
        edges_path = GRAPH_DIR / "semantic_graph.edges.json"

        with open(nodes_path, "w") as f:
            json.dump(list(self.nodes.values()), f, indent=2)
        with open(edges_path, "w") as f:
            json.dump(self.edges, f, indent=2)

        print(f"  Nodes: {len(self.nodes)}")
        print(f"  Edges: {len(self.edges)}")


def main():
    parser = argparse.ArgumentParser(description="Venus Semantic Graph Builder")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild from catalog")
    parser.add_argument("--infer", action="store_true", help="Run inference rules")
    args = parser.parse_args()

    graph = SemanticGraph()

    if args.rebuild:
        catalog_path = REGISTRY_DIR / "catalog.json"
        dep_path = REGISTRY_DIR / "dependency_graph.json"

        if not catalog_path.exists() or not dep_path.exists():
            print("Run generate_catalog.py first")
            return

        catalog = json.loads(catalog_path.read_text())
        dep_graph = json.loads(dep_path.read_text())
        edges = graph.build_from_catalog(catalog, dep_graph)
        print(f"── Semantic Graph Build ──")
        print(f"  Built from catalog: {len(catalog)} entries, {edges} edges mapped")

    if args.infer:
        inf = graph.infer()
        print(f"  Inferred edges: {inf}")

    graph.write()


if __name__ == "__main__":
    main()
