"""
CORE-02: Compiler Framework

LLVM-style multi-source compiler.

Pipeline:
  Source → Parser → AST → UIR → Optimization Passes → Code Generation

Supports:
  - Multiple input formats (JSON, YAML, Markdown, DSL, Text)
  - Compiler passes (extensible)
  - Optimization
  - Incremental compilation (via caching)
  - Multiple output formats (Markdown, Schema, Graph)
"""

from pathlib import Path
from typing import Any

from genesis.compiler.ast import AST
from genesis.compiler.parser import Parser
from genesis.compiler.uir_builder import UIRBuilder
from genesis.compiler.passes.base import PassRegistry
from genesis.compiler.passes.optimization import (
    DeadCodeEliminationPass,
    DependencyPruningPass,
    MetadataNormalizationPass,
)
from genesis.compiler.codegen.base import CodeGenRegistry
from genesis.compiler.codegen.markdown_gen import MarkdownGenerator
from genesis.compiler.codegen.schema_gen import SchemaGenerator
from genesis.compiler.codegen.graph_gen import GraphGenerator
from genesis.core.uir import CompilationUnit
from genesis.core.exceptions import CompilationError
from genesis.events.bus import EventBus
from genesis.persistence import ArtifactStore


class Compiler:
    """Main Venus compiler. Entry point for all compilation."""

    def __init__(self, event_bus: EventBus | None = None, artifact_store: ArtifactStore | None = None):
        self.pass_registry = PassRegistry()
        self.codegen_registry = CodeGenRegistry()
        self.output_dir: Path = Path("_build")
        self._bus = event_bus
        self._artifact_store = artifact_store

        # Register default passes
        self.pass_registry.register(DeadCodeEliminationPass())
        self.pass_registry.register(DependencyPruningPass())
        self.pass_registry.register(MetadataNormalizationPass())

        # Register default code generators
        self.codegen_registry.register(MarkdownGenerator())
        self.codegen_registry.register(SchemaGenerator())
        self.codegen_registry.register(GraphGenerator())

        # Build cache (primary: in-memory, secondary: ArtifactStore)
        self._cache: dict[str, CompilationUnit] = {}

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def compile(self, source_path: str | Path, passes: list[str] | None = None) -> CompilationUnit:
        """Compile a source file through the full pipeline."""
        source_path = Path(source_path)
        spath = str(source_path)

        self._emit("compiler.compile.started", {"source_path": spath})

        if not source_path.exists():
            err = f"Source not found: {source_path}"
            self._emit("compiler.compile.failed", {"source_path": spath, "error": err})
            raise CompilationError(err)

        # Phase 1: Parse
        ast = Parser.parse(source_path)

        # Phase 2: Build UIR
        builder = UIRBuilder()
        cu = builder.build(ast)

        # Phase 3: Optimization passes
        cu = self.pass_registry.run_sequence(cu, passes)

        # Phase 4: Cache (in-memory + persistent)
        self._cache[spath] = cu
        if self._artifact_store is not None:
            self._artifact_store.save({
                "source_path": spath,
                "source_hash": "",
                "compiled_at": cu.compiled_at,
                "cache_data": cu.to_dict(),
            })

        self._emit("compiler.compile.completed", {
            "source_path": spath,
            "node_count": len(cu.graph.nodes) if hasattr(cu, 'graph') else 0,
            "edge_count": len(cu.graph.edges) if hasattr(cu, 'graph') else 0,
        })

        return cu

    def compile_string(self, content: str, fmt: str = "json", source_name: str = "<string>") -> CompilationUnit:
        """Compile a string directly (no file needed)."""
        source_path = f"string:{source_name}"
        self._emit("compiler.compile.started", {"source_path": source_path, "format": fmt})

        ast = Parser.parse_string(content, fmt, source_name)
        builder = UIRBuilder()
        cu = builder.build(ast)
        cu = self.pass_registry.run_sequence(cu)

        self._cache[source_path] = cu
        if self._artifact_store is not None:
            self._artifact_store.save({
                "source_path": source_path,
                "source_hash": "",
                "compiled_at": cu.compiled_at,
                "cache_data": cu.to_dict(),
            })

        self._emit("compiler.compile.completed", {
            "source_path": source_path,
            "node_count": len(cu.graph.nodes) if hasattr(cu, 'graph') else 0,
            "edge_count": len(cu.graph.edges) if hasattr(cu, 'graph') else 0,
        })

        return cu

    def incremental_compile_string(self, content: str, fmt: str = "json", source_name: str = "<string>") -> CompilationUnit:
        """Incremental compile from string — uses cache if available."""
        source_path = f"string:{source_name}"
        if source_path in self._cache:
            return self._cache[source_path]
        return self.compile_string(content, fmt, source_name)

    def generate(self, cu: CompilationUnit, output_dir: str | Path | None = None) -> dict[str, list[Path]]:
        """Run all registered code generators."""
        out = Path(output_dir) if output_dir else self.output_dir
        self._emit("compiler.generate.started", {"output_dir": str(out)})

        artifacts = self.codegen_registry.generate_all(cu, out)

        total_files = sum(len(files) for files in artifacts.values())
        self._emit("compiler.generate.completed", {
            "output_dir": str(out),
            "artifact_count": total_files,
            "formats": list(artifacts.keys()),
        })

        return artifacts

    def compile_and_generate(
        self, source_path: str | Path, output_dir: str | Path | None = None,
        passes: list[str] | None = None,
    ) -> tuple[CompilationUnit, dict[str, list[Path]]]:
        """Compile and generate in one call."""
        cu = self.compile(source_path, passes)
        artifacts = self.generate(cu, output_dir)
        return cu, artifacts

    def incremental_compile(self, source_path: str | Path) -> CompilationUnit:
        """Incremental compilation — uses cache if unchanged.

        Cache hierarchy:
          1. In-memory cache (fastest)
          2. ArtifactStore (persistent, survives restart)
          3. Full compilation
        """
        source_path = Path(source_path)
        cache_key = str(source_path)

        if cache_key in self._cache:
            self._emit("compiler.cache.hit", {"source_path": cache_key})
            return self._cache[cache_key]

        if self._artifact_store is not None:
            stored = self._artifact_store.get(cache_key)
            if stored is not None:
                cu = CompilationUnit.from_dict(stored["cache_data"])
                self._cache[cache_key] = cu
                self._emit("compiler.cache.hit", {"source_path": cache_key, "source": "artifact_store"})
                return cu

        return self.compile(source_path)

    def invalidate_cache(self, source_path: str | Path | None = None):
        if source_path:
            spath = str(source_path)
            self._cache.pop(spath, None)
            if self._artifact_store is not None:
                self._artifact_store.delete(spath)
        else:
            self._cache.clear()
            if self._artifact_store is not None:
                for art in self._artifact_store.all():
                    self._artifact_store.delete(art["source_path"])

    def register_pass(self, pass_instance):
        self.pass_registry.register(pass_instance)

    def register_codegen(self, generator):
        self.codegen_registry.register(generator)
