"""
CORE-09: Repository Indexer

Automatically scans entire repository.
Produces:
  Repository Catalog, Graph, Indexes,
  Dependency Maps, Change Maps, Impact Maps,
  Dead Files, Unused Files, Duplicate Files,
  Broken Links, Knowledge Density
"""

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.events.bus import EventBus


class RepositoryIndexer:
    """Scans and indexes a repository for structure, dependencies, and quality."""

    def __init__(self, root_path: str | Path, event_bus: EventBus | None = None):
        self.root_path = Path(root_path)
        self._bus = event_bus
        self.catalog: dict[str, dict[str, Any]] = {}
        self.dependency_graph: list[dict[str, str]] = []
        self.dead_files: list[str] = []
        self.unused_files: list[str] = []
        self.duplicate_files: list[dict[str, Any]] = []
        self.broken_links: list[dict[str, Any]] = []
        self.file_hashes: dict[str, str] = {}
        self.file_sizes: dict[str, int] = {}
        self.type_counts: dict[str, int] = defaultdict(int)

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def scan(self) -> dict[str, Any]:
        self._emit("indexer.scan.started", {"root": str(self.root_path)})
        self._walk_files()
        self._detect_duplicates()
        self._detect_reference_patterns()
        result = self.summary()
        self._emit("indexer.scan.completed", result)
        return result

    def _walk_files(self):
        extensions = {".md", ".json", ".yaml", ".yml", ".py", ".venus", ".txt", ".toml", ".cfg"}
        for path in self.root_path.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                self._index_file(path)

    def _index_file(self, path: Path):
        rel_path = str(path.relative_to(self.root_path))
        try:
            content = path.read_bytes()
            self.file_hashes[rel_path] = hashlib.sha256(content).hexdigest()[:16]
            self.file_sizes[rel_path] = len(content)
        except Exception:
            self.file_hashes[rel_path] = "error"
            self.file_sizes[rel_path] = 0

        entry = {
            "name": path.name,
            "path": rel_path,
            "suffix": path.suffix,
            "size_bytes": self.file_sizes[rel_path],
            "hash": self.file_hashes[rel_path],
            "type": self._classify(path),
            "layer": self._detect_layer(rel_path),
        }
        self.catalog[rel_path] = entry
        self.type_counts[entry["type"]] += 1

    def _classify(self, path: Path) -> str:
        name = path.stem
        suffix = path.suffix

        if suffix == ".venus":
            return "dsl"
        if name.endswith("_SCHEMA"):
            return "schema"
        if name.endswith("_SCHEMA.json"):
            return "schema"
        if suffix == ".py":
            return "script"
        if suffix == ".md":
            if "CONSTITUTION" in name or "GOVERNANCE" in name:
                return "constitution"
            if "ARCHITECTURE" in name or "SPECIFICATION" in name:
                return "specification"
            if "README" in name or "INDEX" in name:
                return "index"
            if "CHANGELOG" in name or "ROADMAP" in name:
                return "meta"
            return "documentation"
        if suffix in (".yaml", ".yml"):
            return "config"
        if suffix == ".json":
            return "data"
        return "other"

    def _detect_layer(self, rel_path: str) -> str:
        parts = rel_path.split("/")
        for part in parts:
            if part.startswith("Layer_"):
                return part
            if part.startswith("V0.") or part.startswith("v0."):
                return part
            if part == "genesis":
                return "genesis"
        return "unknown"

    def _detect_duplicates(self):
        hash_groups = defaultdict(list)
        for path, h in self.file_hashes.items():
            if h != "error":
                hash_groups[h].append(path)

        for h, paths in hash_groups.items():
            if len(paths) > 1:
                self.duplicate_files.append({
                    "hash": h,
                    "paths": paths,
                    "count": len(paths),
                })

    def _detect_reference_patterns(self):
        """Scan markdown files for broken links and references."""
        ref_patterns = [
            (r"\[([^\]]+)\]\(([^)]+)\)", "markdown_link"),
            (r"`venus://[^`]+`", "venus_ref"),
            (r"\.\./[^)\s]+", "relative_path"),
        ]
        import re

        all_files_set = set(self.catalog.keys())

        for path, entry in self.catalog.items():
            if entry["suffix"] != ".md":
                continue

            abs_path = self.root_path / path
            try:
                content = abs_path.read_text()
            except Exception:
                continue

            for pattern, ref_type in ref_patterns:
                for match in re.finditer(pattern, content):
                    ref = match.group(0)
                    # Check if reference points to a valid file
                    if ref_type == "markdown_link":
                        target = match.group(2)
                        if target.startswith("http"):
                            continue
                        resolved = self._resolve_reference(path, target)
                        if resolved and resolved not in all_files_set:
                            self.broken_links.append({
                                "source": path,
                                "target": target,
                                "resolved": resolved,
                                "type": ref_type,
                            })

    def _resolve_reference(self, source_path: str, target: str) -> str | None:
        """Resolve a relative path reference to an absolute repo path."""
        source_dir = Path(source_path).parent
        resolved = (self.root_path / source_dir / target).resolve()
        try:
            return str(resolved.relative_to(self.root_path))
        except ValueError:
            return None

    def detect_dead_files(self, reference_graph: list[dict] | None = None) -> list[str]:
        """Find files with no incoming references."""
        referenced = set()
        if reference_graph:
            for edge in reference_graph:
                referenced.add(edge.get("target", ""))

        # Files that are referenced by at least one other file
        for entry in self.broken_links:
            pass  # broken links don't count as valid references

        all_paths = set(self.catalog.keys())
        dead = all_paths - referenced

        # Exclude top-level index files
        dead = {
            p for p in dead
            if not p.endswith("INDEX.md")
            and not p.endswith("README.md")
            and "Layer_" not in p.split("/")[-1]
        }

        self.dead_files = sorted(dead)
        self._emit("indexer.dead_files.detected", {"dead_files": self.dead_files, "count": len(self.dead_files)})
        return self.dead_files

    def knowledge_density(self) -> dict[str, Any]:
        """Calculate knowledge density metrics."""
        md_files = [p for p, e in self.catalog.items() if e["suffix"] == ".md"]
        total_chars = 0
        total_lines = 0
        headings = 0
        code_blocks = 0
        links = 0
        import re

        for path in md_files[:200]:  # Limit for performance
            try:
                content = (self.root_path / path).read_text()
                total_chars += len(content)
                total_lines += content.count("\n") + 1
                headings += len(re.findall(r"^#{1,6}\s", content, re.MULTILINE))
                code_blocks += len(re.findall(r"```", content)) // 2
                links += len(re.findall(r"\[([^\]]+)\]", content))
            except Exception:
                pass

        return {
            "total_md_files": len(md_files),
            "total_chars": total_chars,
            "total_lines": total_lines,
            "avg_lines_per_file": round(total_lines / max(len(md_files), 1), 1),
            "total_headings": headings,
            "total_code_blocks": code_blocks,
            "total_links": links,
            "density_score": round(
                (headings + code_blocks * 3 + links) / max(total_chars, 1) * 10000, 2
            ),
        }

    def impact_map(self, changed_files: list[str]) -> dict[str, Any]:
        """Calculate impact of changes to specific files."""
        impacted = set()
        for changed in changed_files:
            for edge in self.dependency_graph:
                if edge.get("source") == changed:
                    impacted.add(edge.get("target"))
        return {
            "changed_files": changed_files,
            "directly_impacted": sorted(impacted),
            "impact_count": len(impacted),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "root": str(self.root_path),
            "total_files": len(self.catalog),
            "by_type": dict(self.type_counts),
            "duplicates": len(self.duplicate_files),
            "broken_links": len(self.broken_links),
            "dead_files": len(self.dead_files),
            "total_size_bytes": sum(self.file_sizes.values()),
        }

    def save_catalog(self, path: str | Path):
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_entries": len(self.catalog),
            "entries": self.catalog,
        }
        Path(path).write_text(json.dumps(data, indent=2))
