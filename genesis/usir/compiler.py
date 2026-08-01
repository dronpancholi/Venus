"""
Multi-Language Compiler — source → USIR → DigitalTwin enrichment.

Pipeline:
  1. Discover files by language
  2. Select appropriate adapter
  3. Parse each file into USIR
  4. Merge into combined USIR graph
  5. Enrich DigitalTwin with USIR data
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from genesis.usir import USIRGraph, USIRKind, USIRNode
from genesis.usir.language import LanguageAdapter
from genesis.usir.parsers import PythonAdapter
from genesis.usir.parsers.typescript import TypeScriptAdapter, JavaScriptAdapter


class MultiLanguageCompiler:
    """Compile any repository into a unified USIR graph."""

    def __init__(self):
        self.adapters: dict[str, LanguageAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self):
        python = PythonAdapter()
        self.adapters[python.language_name()] = python
        ts = TypeScriptAdapter()
        self.adapters[ts.language_name()] = ts
        js = JavaScriptAdapter()
        self.adapters[js.language_name()] = js

    def register_adapter(self, adapter: LanguageAdapter):
        self.adapters[adapter.language_name()] = adapter

    def discover_files(self, root: Path) -> dict[str, list[Path]]:
        """Discover all parseable files grouped by language."""
        ext_to_lang: dict[str, str] = {}
        for name, adapter in self.adapters.items():
            for ext in adapter.file_extensions():
                ext_to_lang[ext] = name

        files_by_lang: dict[str, list[Path]] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "__pycache__" in str(path):
                continue
            lang = ext_to_lang.get(path.suffix)
            if lang:
                files_by_lang.setdefault(lang, []).append(path)

        return files_by_lang

    def compile(self, root: Path | str) -> USIRGraph:
        """Compile entire repository into USIR."""
        root = Path(root).resolve()
        combined = USIRGraph()

        files_by_lang = self.discover_files(root)
        for lang_name, paths in files_by_lang.items():
            adapter = self.adapters.get(lang_name)
            if not adapter:
                continue
            for path in paths:
                try:
                    graph = adapter.parse_file(path, root)
                    for node in graph.nodes:
                        combined.add_node(node)
                    for kind, edges in graph._edges.items():
                        for s, t, l in edges:
                            combined.add_edge(s, t, kind, l)
                except Exception:
                    continue

        return combined

    def enrich_digital_twin(self, usir: USIRGraph, twin):
        """Enrich an existing DigitalTwin with USIR data."""
        for node in usir.nodes:
            if node.kind in (USIRKind.CLASS, USIRKind.PROTOCOL, USIRKind.INTERFACE, USIRKind.TRAIT):
                # — find or create twin node —
                nid = node.source_file and f"{node.source_file}::{node.name}" or node.id
                existing = twin.get_node(nid)
                if not existing:
                    from genesis.digital_twin.model import TwinNode
                    existing = TwinNode(id=nid, kind="class", label=node.name)
                    existing.file_path = node.source_file
                    existing.module = node.qualified_name

                # — enrich from USIR —
                existing.base_classes = node.base_types or existing.base_classes
                if node.implemented_interfaces:
                    existing.interfaces = node.implemented_interfaces
                if node.is_abstract:
                    existing.role = "abstract"
                if node.docstring:
                    existing.docstring = node.docstring[:500]
                    existing.purpose = node.docstring.split("\n")[0][:100]

                twin.add_node(existing)

            elif node.kind == USIRKind.FUNCTION:
                nid = node.source_file and f"{node.source_file}::{node.name}" or node.id
                existing = twin.get_node(nid)
                if not existing:
                    from genesis.digital_twin.model import TwinNode
                    existing = TwinNode(id=nid, kind="function", label=node.name)
                    existing.file_path = node.source_file
                    existing.module = node.qualified_name

                if node.docstring:
                    existing.docstring = node.docstring[:500]
                existing.tags = list(set(existing.tags + self._infer_tags(node)))
                twin.add_node(existing)

            # — imports → dependency edges —
            if node.kind == USIRKind.IMPORT and node.source_file:
                source_mod = node.source_file
                for imp in node.imports:
                    target_mod = imp.get("module", "").replace(".", "/")
                    twin.add_edge(source_mod, target_mod + ".py", "imports")

    def summary(self, usir: USIRGraph) -> dict[str, Any]:
        return {
            "total_nodes": usir.node_count,
            "node_kinds": usir.count_by_kind(),
            "languages_detected": list(self.adapters.keys()),
        }

    def _infer_tags(self, node: USIRNode) -> list[str]:
        tags = []
        if node.is_async:
            tags.append("async")
        if node.is_generator:
            tags.append("generator")
        if node.decorators:
            tags.append("decorated")
        return tags
