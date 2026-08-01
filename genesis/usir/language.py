"""
Language Adapter Protocol — interface for adding USIR parser backends.

Each language implements:
  parse_file(path) → list[USIRNode]
  detect(path) → bool  (can this adapter parse this file?)
  language_name() → str
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from genesis.usir import USIRGraph


class LanguageAdapter(ABC):
    """Protocol for language-specific USIR parsers."""

    @abstractmethod
    def language_name(self) -> str:
        ...

    @abstractmethod
    def file_extensions(self) -> set[str]:
        ...

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.file_extensions() and path.is_file()

    @abstractmethod
    def parse_file(self, path: Path, source_root: Path) -> USIRGraph:
        """Parse a single file and return its USIR graph."""
        ...

    def parse_files(self, paths: list[Path], source_root: Path) -> USIRGraph:
        """Parse multiple files and merge into a single USIR graph."""
        combined = USIRGraph()
        for path in paths:
            try:
                graph = self.parse_file(path, source_root)
                for node in graph.nodes:
                    combined.add_node(node)
                for kind, edges in graph._edges.items():
                    for s, t, l in edges:
                        combined.add_edge(s, t, kind, l)
            except Exception as e:
                pass  # Skip unparseable files
        return combined
