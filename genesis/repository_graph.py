"""
GENESIS XIII Phase 2: Complete Engineering Knowledge Graph.

Reads census catalogs and constructs a multi-layer graph of everything:
modules, classes, functions, tests, packages, services, APIs, dependencies.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from genesis.graph_v2.core import (
    GraphEdge, GraphLayer, GraphNode, LayerType, UnifiedGraph,
)
from genesis.graph_v2.index import GraphIndex
from genesis.graph_v2.analytics import GraphAnalytics

CENSUS_DIR = Path(__file__).parent / "census"


def _load_catalog(name: str) -> dict[str, Any]:
    path = CENSUS_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


class EngineeringKnowledgeGraph:
    """Multi-layer engineering knowledge graph built from repository census."""

    def __init__(self):
        self._graph = UnifiedGraph()
        self._index = GraphIndex()
        self._built = False

    def build(self) -> UnifiedGraph:
        module_cat = _load_catalog("module_catalog")
        test_cat = _load_catalog("test_catalog")
        service_cat = _load_catalog("service_catalog")
        dep_cat = _load_catalog("dependency_catalog")
        metrics = _load_catalog("metrics_catalog")

        # Layer 1: Structural — all modules as nodes
        structural = self._graph.create_layer("structural", LayerType.STRUCTURAL)
        for mod_key, mod_data in module_cat.items():
            node = GraphNode(
                id=f"mod:{mod_key}",
                name=mod_data.get("name", mod_key),
                node_type="module",
                properties={
                    "package": mod_data.get("package", ""),
                    "path": mod_data.get("path", ""),
                    "lines": mod_data.get("total_lines", 0),
                    "code_lines": mod_data.get("code_lines", 0),
                    "classes": mod_data.get("classes", []),
                    "functions": mod_data.get("functions", []),
                    "maturity": mod_data.get("maturity", 0.0),
                    "has_docstring": mod_data.get("has_docstring", False),
                    "has_type_hints": mod_data.get("has_type_hints", False),
                },
                labels=["module"],
                weight=mod_data.get("maturity", 0.5),
            )
            structural.add_node(node)

        # Layer 2: Dependency — edges between modules that import each other
        dependency = self._graph.create_layer("dependency", LayerType.DEPENDENCY)
        for mod_key, mod_data in module_cat.items():
            source_id = f"mod:{mod_key}"
            dep_node = GraphNode(
                id=source_id,
                name=mod_data.get("name", mod_key),
                node_type="module",
                properties={
                    "package": mod_data.get("package", ""),
                    "path": mod_data.get("path", ""),
                },
                labels=["module", "dependency_node"],
            )
            dependency.add_node(dep_node)

        for mod_key, mod_data in module_cat.items():
            source_id = f"mod:{mod_key}"
            for imp in mod_data.get("internal_imports", []):
                target_id = f"mod:{imp}"
                # Check if target exists (even as partial match)
                edge = GraphEdge(
                    source_id=source_id,
                    target_id=target_id,
                    edge_type="imports",
                    properties={"strength": "direct"},
                    weight=1.0,
                )
                try:
                    dependency.add_edge(edge)
                except ValueError:
                    pass

        # Add class nodes for every class in every module
        for mod_key, mod_data in module_cat.items():
            for cls_name in mod_data.get("classes", []):
                cls_id = f"cls:{mod_key}.{cls_name}"
                class_node = GraphNode(
                    id=cls_id,
                    name=cls_name,
                    node_type="class",
                    properties={"module": mod_key},
                    labels=["class"],
                )
                try:
                    structural.add_node(class_node)
                    edge = GraphEdge(
                        source_id=f"mod:{mod_key}",
                        target_id=cls_id,
                        edge_type="contains",
                    )
                    structural.add_edge(edge)
                except (ValueError, KeyError):
                    pass

        # Layer 3: Knowledge — catalog metrics and test coverage
        knowledge = self._graph.create_layer("knowledge", LayerType.KNOWLEDGE)
        by_pkg = metrics.get("by_package", {})
        for pkg_name, pkg_info in by_pkg.items():
            pkg_node = GraphNode(
                id=f"pkg:{pkg_name}",
                name=pkg_name,
                node_type="package",
                properties={
                    "modules": pkg_info.get("modules", 0),
                    "lines": pkg_info.get("lines", 0),
                    "tests": pkg_info.get("tests", 0),
                    "maturity": pkg_info.get("avg_maturity", 0.0),
                },
                labels=["package"],
            )
            knowledge.add_node(pkg_node)

        # Layer 4: Test coverage
        test_layer = self._graph.get_layer("structural") or structural
        for tname, tinfo in test_cat.items():
            tid = f"test:{tname}"
            test_node = GraphNode(
                id=tid,
                name=tname,
                node_type="test_suite",
                properties={
                    "test_count": tinfo.get("test_count", 0),
                    "test_classes": tinfo.get("test_classes", []),
                    "test_functions": tinfo.get("test_functions", []),
                },
                labels=["test"],
            )
            try:
                test_layer.add_node(test_node)
                for imp in tinfo.get("imports_under_test", []):
                    target_id = f"mod:{imp.partition('.')[-1].split('.')[0]}"
                    # Try to find the actual module key
                    for mk in module_cat:
                        if imp in mk or mk.endswith(imp):
                            target_id = f"mod:{mk}"
                            break
                    edge = GraphEdge(
                        source_id=tid,
                        target_id=target_id,
                        edge_type="tests",
                        properties={"count": tinfo.get("test_count", 0)},
                    )
                    try:
                        test_layer.add_edge(edge)
                    except ValueError:
                        pass
            except (ValueError, KeyError):
                pass

        self._index.index_layer(structural)
        self._index.index_layer(dependency)
        self._built = True
        return self._graph

    @property
    def graph(self) -> UnifiedGraph:
        if not self._built:
            self.build()
        return self._graph

    @property
    def index(self) -> GraphIndex:
        return self._index

    def query(self, query_str: str) -> list[dict[str, Any]]:
        if not self._built:
            self.build()
        return self._index.search(query_str)

    def find_module(self, name: str) -> GraphNode | None:
        if not self._built:
            self.build()
        layer = self._graph.get_layer("structural")
        if layer:
            for node in layer._nodes.values():
                if name in node.name or name in node.properties.get("package", ""):
                    return node
        return None

    def find_by_type(self, node_type: str) -> list[dict[str, Any]]:
        if not self._built:
            self.build()
        return self._index.find_by_type(node_type)

    def find_by_label(self, label: str) -> list[dict[str, Any]]:
        if not self._built:
            self.build()
        return self._index.find_by_label(label)

    def top_modules(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self._built:
            self.build()
        layer = self._graph.get_layer("structural")
        if not layer:
            return []
        scored = []
        for node in layer._nodes.values():
            if "module" in node.labels:
                scored.append((node.properties.get("maturity", 0) * node.weight,
                              {"id": node.id, "name": node.name, "maturity": node.properties.get("maturity"),
                               "lines": node.properties.get("lines"), "package": node.properties.get("package")}))
        scored.sort(key=lambda x: -x[0])
        return [s[1] for s in scored[:limit]]

    def summary(self) -> dict[str, Any]:
        if not self._built:
            self.build()
        return {
            "graph": self._graph.summary(),
            "index": self._index.summary(),
        }
