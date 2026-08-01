#!/usr/bin/env python3
"""
Venus Catalog & Knowledge Graph Generator.

Scans the Venus repository, extracts metadata from directory structure and
file naming conventions, and generates:
  1. catalog.json          — Machine-readable index of all artifacts
  2. dependency_graph.json — Cross-file dependency edges
  3. graph.nodes.json      — Knowledge graph nodes
  4. graph.edges.json      — Knowledge graph edges
  5. manifest_v*.json      — Per-OS version manifests

Usage:
  python3 generate_catalog.py [--repo-path /path/to/Venus] [--output-dir /path/to/output]
"""

import argparse
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

LAYER_PATTERN = re.compile(r"^Layer_(\d)_(.+)$")
OS_PATTERN = re.compile(r"^V(\d+)\.(\d+)_([A-Z]+)$")
PART_PATTERN = re.compile(r"^(PART|MODULE)_(\d+)_(.+)\.md$")
ENGINE_PATTERN = re.compile(r"^ENGINE_(.+)\.md$")
TEMPLATE_PATTERN = re.compile(r"^TEMPLATE_(\d+)_(.+)\.md$")
TEMPLATE2_PATTERN = re.compile(r"^([A-Z][A-Z_]+)\.md$")
STAGE_PATTERN = re.compile(r"^STAGE_(\d+)_(.+)\.md$")
SCHEMA_PATTERN = re.compile(r"^(.+_SCHEMA)\.json$")

NODE_TYPES = {
    "parts": "part",
    "modules": "module",
    "engines": "engine",
    "templates": "template",
    "stages": "stage",
    "decision_matrices": "framework",
    "problem_templates": "problem_template",
    "automation": "automation",
    "_schemas": "schema",
    "_registry": "registry",
    "_graph": "graph",
    "_validation": "validation",
}

# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def generate_venus_id() -> str:
    return f"VENUS-{uuid.uuid4()}"


def parse_layer_dir(dirname: str):
    m = LAYER_PATTERN.match(dirname)
    if m:
        return int(m.group(1)), m.group(2).replace("_", " ").title()
    return None, None


def parse_os_dir(dirname: str):
    m = OS_PATTERN.match(dirname)
    if m:
        return int(m.group(1)), int(m.group(2)), m.group(3)
    return None, None, None


def artifact_type_from_parent(parent_name: str) -> str:
    parent_lower = parent_name.lower()
    for key, val in NODE_TYPES.items():
        if key in parent_lower:
            return val
    if parent_lower.endswith("parts") or parent_lower.endswith("modules"):
        return "part"
    if parent_lower.endswith("templates"):
        return "template"
    return "unknown"


def readme_description(dir_path: Path) -> str:
    """Extract the first heading from the main markdown file in an OS directory."""
    for f in dir_path.iterdir():
        if f.is_file() and f.suffix == ".md" and f.stem.startswith("V0"):
            content = f.read_text(errors="replace")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("# ") and "PROJECT VENUS" not in line.upper():
                    return line.lstrip("# ").strip()
    return ""


def slugify(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def extract_os_name(os_dir: Path) -> str:
    """Derive human-readable OS name from the directory."""
    parts = os_dir.name.split("_", 2)
    if len(parts) >= 3:
        return parts[2]
    return os_dir.name


# ──────────────────────────────────────────────────────────────────
# Scanner
# ──────────────────────────────────────────────────────────────────

def scan_repository(repo_path: Path):
    catalog = {}
    dep_edges = []
    nodes = []
    edges = []

    # Visit each Layer directory
    for layer_dir in sorted(repo_path.iterdir()):
        if not layer_dir.is_dir():
            continue
        layer_num, layer_name = parse_layer_dir(layer_dir.name)
        if layer_num is None:
            continue

        # Layer-level node
        layer_id = f"VENUS-LAYER-{layer_num}"
        catalog[layer_id] = {
            "venus_id": layer_id,
            "name": layer_name,
            "type": "layer",
            "layer": layer_num,
            "version": "N/A",
            "schema": "venus://schemas/base/entity/v1",
            "path": str(layer_dir.relative_to(repo_path)),
        }
        nodes.append({
            "id": layer_id,
            "type": "layer",
            "label": f"Layer {layer_num}: {layer_name}",
            "layer": layer_num,
        })

        # Scan layer contents
        _scan_directory(layer_dir, layer_num, catalog, dep_edges, nodes, edges, repo_path)

    return catalog, dep_edges, nodes, edges


def _scan_directory(
    directory: Path,
    layer_num: int,
    catalog: dict,
    dep_edges: list,
    nodes: list,
    edges: list,
    repo_path: Path,
    parent_id: str = None,
):
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.name == "__pycache__":
            continue

        rel_path = str(entry.relative_to(repo_path))

        if entry.is_dir():
            # Check if it's an OS version directory
            major, minor, code = parse_os_dir(entry.name)
            if major is not None:
                os_name = extract_os_name(entry)
                os_id = f"VENUS-V{major}.{minor}-{code}"
                desc = readme_description(entry)

                catalog[os_id] = {
                    "venus_id": os_id,
                    "name": f"V{major}.{minor} {os_name}",
                    "type": "os_version",
                    "layer": layer_num,
                    "version": f"V{major}.{minor}",
                    "schema": "venus://schemas/base/entity/v1",
                    "path": rel_path,
                    "description": desc,
                }
                nodes.append({
                    "id": os_id,
                    "type": "os_version",
                    "label": f"V{major}.{minor} {os_name}",
                    "layer": layer_num,
                    "version": f"{major}.{minor}",
                })
                if parent_id:
                    edges.append({
                        "source": parent_id,
                        "target": os_id,
                        "type": "contains",
                    })

                # Recursively scan OS subdirectories
                _scan_directory(entry, layer_num, catalog, dep_edges, nodes, edges, repo_path, os_id)

            else:
                # Regular subdirectory
                dir_id = f"VENUS-DIR-{slugify(rel_path)}"
                catalog[dir_id] = {
                    "venus_id": dir_id,
                    "name": entry.name,
                    "type": artifact_type_from_parent(entry.name),
                    "layer": layer_num,
                    "version": "N/A",
                    "schema": "venus://schemas/base/entity/v1",
                    "path": rel_path,
                }
                nodes.append({
                    "id": dir_id,
                    "type": "directory",
                    "label": entry.name,
                    "layer": layer_num,
                })
                if parent_id:
                    edges.append({
                        "source": parent_id,
                        "target": dir_id,
                        "type": "contains",
                    })
                _scan_directory(entry, layer_num, catalog, dep_edges, nodes, edges, repo_path, dir_id)

        elif entry.is_file() and entry.suffix in (".md", ".json", ".py", ".yaml", ".yml"):
            _catalog_file(entry, layer_num, catalog, nodes, edges, repo_path, parent_id)


def _catalog_file(
    file_path: Path,
    layer_num: int,
    catalog: dict,
    nodes: list,
    edges: list,
    repo_path: Path,
    parent_id: str = None,
):
    rel_path = str(file_path.relative_to(repo_path))
    stem = file_path.stem
    ftype = "unknown"

    # Determine artifact type from filename
    if PART_PATTERN.match(stem):
        ftype = "part"
    elif ENGINE_PATTERN.match(stem):
        ftype = "engine"
    elif TEMPLATE_PATTERN.match(stem):
        ftype = "template"
    elif TEMPLATE2_PATTERN.match(stem) and file_path.parent.name.endswith("templates"):
        ftype = "template"
    elif STAGE_PATTERN.match(stem):
        ftype = "stage"
    elif SCHEMA_PATTERN.match(stem):
        ftype = "schema"
    elif stem == "UVCOS":
        ftype = "constitution"
    elif file_path.suffix == ".py":
        ftype = "script"
    elif file_path.suffix == ".json" and "schema" not in stem.lower():
        ftype = "registry"
    elif file_path.suffix in (".yaml", ".yml"):
        ftype = "config"

    # Fallback to parent directory type
    if ftype == "unknown":
        ftype = artifact_type_from_parent(file_path.parent.name)

    file_id = f"VENUS-FILE-{slugify(rel_path)}"
    catalog[file_id] = {
        "venus_id": file_id,
        "name": stem,
        "type": ftype,
        "layer": layer_num,
        "version": _derive_version(file_path),
        "schema": f"venus://schemas/{ftype}/v1" if ftype in ("part", "engine", "template") else "venus://schemas/base/entity/v1",
        "path": rel_path,
    }
    nodes.append({
        "id": file_id,
        "type": ftype,
        "label": stem,
        "layer": layer_num,
    })
    if parent_id:
        edges.append({
            "source": parent_id,
            "target": file_id,
            "type": "contains",
        })

    # Extract cross-references from markdown links
    if file_path.suffix == ".md":
        _extract_references(file_path, file_id, catalog, edges, repo_path)


def _derive_version(file_path: Path) -> str:
    """Extract the OS version from the file path."""
    for part in file_path.parts:
        m = OS_PATTERN.match(part)
        if m:
            return f"V{m.group(1)}.{m.group(2)}"
    return "N/A"


def _extract_references(
    file_path: Path,
    source_id: str,
    catalog: dict,
    edges: list,
    repo_path: Path,
):
    """Scan markdown content for cross-references and add graph edges."""
    try:
        content = file_path.read_text(errors="replace")
    except Exception:
        return

    # Find markdown links: [text](./path/to/file.md)
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", content):
        target_path = m.group(2)
        if target_path.startswith("http"):
            continue  # skip external links
        # Normalize relative path
        target_abs = (file_path.parent / target_path).resolve()
        try:
            target_rel = str(target_abs.relative_to(repo_path))
        except ValueError:
            continue

        target_id = f"VENUS-FILE-{slugify(target_rel)}"
        if target_id not in catalog:
            catalog[target_id] = {
                "venus_id": target_id,
                "name": target_abs.stem,
                "type": "unknown",
                "layer": 0,
                "version": "N/A",
                "schema": "venus://schemas/base/entity/v1",
                "path": target_rel,
            }

        edges.append({
            "source": source_id,
            "target": target_id,
            "type": "references",
        })


# ──────────────────────────────────────────────────────────────────
# Manifest Generation
# ──────────────────────────────────────────────────────────────────

def generate_manifests(catalog: dict, nodes: list, edges: list, output_dir: Path):
    """Generate per-OS version manifests."""
    os_versions = {}
    for entry in catalog.values():
        if entry["type"] == "os_version" and entry["version"] != "N/A":
            ver = entry["version"]
            if ver not in os_versions:
                os_versions[ver] = {
                    "version": ver,
                    "name": entry["name"],
                    "path": entry["path"],
                    "description": entry.get("description", ""),
                    "capabilities": [],
                    "constraints": [],
                    "components": [],
                    "dependencies": [],
                }
            os_versions[ver]["components"].append(entry["venus_id"])

    # Build dependency chain (V0.X inherits from V0.X-1)
    sorted_versions = sorted(os_versions.keys())
    for i, ver in enumerate(sorted_versions):
        if i > 0:
            prev_ver = sorted_versions[i - 1]
            os_versions[ver]["dependencies"].append(prev_ver)

    for ver, manifest in os_versions.items():
        ver_slug = ver.lower().replace(".", "_")
        manifest_path = output_dir / f"manifest_{ver_slug}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"  Generated {manifest_path.name}")


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Venus Catalog & Knowledge Graph Generator")
    parser.add_argument("--repo-path", type=str, default=str(ROOT_DIR),
                        help="Path to Venus repository root")
    parser.add_argument("--output-dir", type=str,
                        default=str(ROOT_DIR / "Layer_1_Foundations" / "_registry"),
                        help="Output directory for generated files")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_dir = repo_path / "Layer_1_Foundations" / "_graph"
    graph_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning repository: {repo_path}")
    catalog, dep_edges, nodes, edges = scan_repository(repo_path)

    # Sort for deterministic output
    catalog = dict(sorted(catalog.items()))
    nodes = sorted(nodes, key=lambda n: n["id"])
    edges = sorted(edges, key=lambda e: (e["source"], e["target"], e["type"]))

    # Write catalog.json
    catalog_path = output_dir / "catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"  Generated catalog.json ({len(catalog)} entries)")

    # Write dependency_graph.json
    dep_path = output_dir / "dependency_graph.json"
    with open(dep_path, "w") as f:
        json.dump(edges, f, indent=2)
    print(f"  Generated dependency_graph.json ({len(edges)} edges)")

    categorical = _categorize_edges(edges)

    # Write graph.nodes.json
    nodes_path = graph_dir / "graph.nodes.json"
    with open(nodes_path, "w") as f:
        json.dump(nodes, f, indent=2)
    print(f"  Generated graph.nodes.json ({len(nodes)} nodes)")

    # Write graph.edges.json
    edges_path = graph_dir / "graph.edges.json"
    with open(edges_path, "w") as f:
        json.dump(edges, f, indent=2)
    print(f"  Generated graph.edges.json ({len(edges)} edges)")

    # Write graph.cypher
    cypher_path = graph_dir / "graph.cypher"
    with open(cypher_path, "w") as f:
        f.write(_generate_cypher(nodes, edges))
    print(f"  Generated graph.cypher")

    # Write per-OS manifests
    generate_manifests(catalog, nodes, edges, output_dir)

    # Write summary
    type_counts = {}
    for n in nodes:
        t = n["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\n── Catalog Summary ──")
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count}")
    print(f"\n  Total nodes: {len(nodes)}")
    print(f"  Total edges: {len(edges)}")
    print(f"  Reference edges: {len(categorical.get('references', []))}")
    print(f"  Containment edges: {len(categorical.get('contains', []))}")


def _categorize_edges(edges: list) -> dict:
    categories = {}
    for e in edges:
        t = e["type"]
        if t not in categories:
            categories[t] = []
        categories[t].append(e)
    return categories


def _generate_cypher(nodes: list, edges: list) -> str:
    lines = [
        "// PROJECT VENUS — Knowledge Graph",
        f"// Generated: {datetime.utcnow().isoformat()}Z",
        "// Import into Neo4j or ArangoDB for graph traversal",
        "",
        "// ── Nodes ──",
    ]

    for n in nodes:
        props = json.dumps({k: v for k, v in n.items() if k != "type"})
        lines.append(f"CREATE (:{n['type'].upper()} {{{props.strip('{}')}}})")

    lines.extend(["", "// ── Edges ──"])
    for e in edges:
        lines.append(
            f"MATCH (a {{id: '{e['source']}'}}), "
            f"(b {{id: '{e['target']}'}}) "
            f"CREATE (a)-[:{e['type'].upper()}]->(b)"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    main()
