#!/usr/bin/env python3
"""
VENUS COMPILER — Phase 4

Transforms Venus DSL definitions into all generated artifacts:
  - Markdown documentation
  - JSON Schema validation files
  - Mermaid diagrams
  - Prompt packs
  - Validation scripts
  - Agent specifications
  - Catalog updates
  - Knowledge graph updates

Usage:
  python3 venus_compiler.py [--input file.venus] [--output-dir ./_generated]
  python3 venus_compiler.py --compile-all    (recompile all DSL files)
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ONTOLOGY_PATH = ROOT_DIR / "Layer_1_Foundations" / "_ontology" / "ontology.types.json"
SCHEMAS_DIR = ROOT_DIR / "Layer_1_Foundations" / "_schemas"
CATALOG_PATH = ROOT_DIR / "Layer_1_Foundations" / "_registry" / "catalog.json"
GRAPH_NODES_PATH = ROOT_DIR / "Layer_1_Foundations" / "_graph" / "graph.nodes.json"
GRAPH_EDGES_PATH = ROOT_DIR / "Layer_1_Foundations" / "_graph" / "graph.edges.json"


# ──────────────────────────────────────────────────────────────────
# 1. Ontology & Type System
# ──────────────────────────────────────────────────────────────────

class Ontology:
    def __init__(self):
        self.types: dict[str, dict] = {}
        self._load()

    def _load(self):
        if ONTOLOGY_PATH.exists():
            data = json.loads(ONTOLOGY_PATH.read_text())
            for t in data["types"]:
                self.types[t["name"]] = t

    def is_valid_type(self, name: str) -> bool:
        return name in self.types

    def inheritance_chain(self, name: str) -> list[str]:
        chain = []
        current = name
        while current:
            chain.append(current)
            t = self.types.get(current)
            if t:
                current = t.get("extends")
            else:
                current = None
        return chain

    def validate_inheritance(self, child: str, parent: str) -> bool:
        return parent in self.inheritance_chain(child)


# ──────────────────────────────────────────────────────────────────
# 2. Parser
# ──────────────────────────────────────────────────────────────────

class DSLError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        super().__init__(f"Line {line}:{column} - {message}")


class DSLParser:
    BLOCK_TYPES = {
        "operatingsystem", "part", "module", "engine", "template",
        "certificate", "stage", "workflow", "policy", "agent",
        "memory", "schema", "interface", "ontology", "config"
    }

    def parse(self, source: str, filename: str = "<unknown>") -> dict:
        definitions = []
        self._source = source
        self._lines = source.split("\n")
        self._pos = 0
        self._filename = filename

        blocks = self._parse_blocks()
        return {"filename": filename, "definitions": blocks}

    def _parse_blocks(self) -> list:
        blocks = []
        while self._pos < len(self._lines):
            line = self._lines[self._pos].strip()
            self._pos += 1

            # Skip comments and blank lines
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            # Check for block start: type "name" {
            m = re.match(r'^(\w+)\s+"([^"]+)"\s*\{', line)
            if m:
                block_type, name = m.group(1), m.group(2)
                if block_type not in self.BLOCK_TYPES:
                    raise DSLError(f"Unknown block type: {block_type}", self._pos, 0)
                block = self._parse_block(block_type, name)
                blocks.append(block)
                continue

        return blocks

    @staticmethod
    def _balance(s: str) -> int:
        """Return net bracket depth: positive means more opens than closes."""
        depth = 0
        in_string = False
        for c in s:
            if c == '"':
                in_string = not in_string
            elif not in_string:
                if c in ("{", "["):
                    depth += 1
                elif c in ("}", "]"):
                    depth -= 1
        return depth

    def _parse_block(self, block_type: str, name: str) -> dict:
        block = {
            "type": block_type,
            "name": name,
            "fields": {},
            "sub_blocks": [],
        }
        brace_depth = 1

        while self._pos < len(self._lines) and brace_depth > 0:
            line = self._lines[self._pos].strip()
            self._pos += 1

            if not line or line.startswith("//") or line.startswith("#"):
                continue

            # Track brace depth for block nesting
            line_clean = re.sub(r'"[^"]*"', '', line)  # remove string contents for depth calc
            brace_depth += line_clean.count("{") - line_clean.count("}")

            # Check for sub-block definition: type "name" {
            m = re.match(r'^(\w+)\s+"([^"]+)"\s*\{', line)
            if m and m.group(1) in self.BLOCK_TYPES:
                sub = self._parse_block(m.group(1), m.group(2))
                block["sub_blocks"].append(sub)
                continue

            # Field assignment: key = value (possibly multi-line)
            m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
            if m:
                key = m.group(1)
                value_str = m.group(2).rstrip(",")
                # Accumulate multi-line values
                vdepth = self._balance(value_str)
                while vdepth > 0 and self._pos < len(self._lines):
                    next_line = self._lines[self._pos]
                    self._pos += 1
                    value_str += "\n" + next_line
                    vdepth = self._balance(value_str)
                try:
                    block["fields"][key] = self._parse_value(value_str.strip())
                except ValueError as e:
                    raise DSLError(f"Failed to parse value for {key}: {e}", self._pos, 0)
                continue

        return block

    def _parse_value(self, value_str: str) -> Any:
        value_str = value_str.strip()

        # String
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]

        # Number
        m = re.match(r'^-?\d+(\.\d+)?$', value_str)
        if m:
            return float(m.group(0)) if "." in m.group(0) else int(m.group(0))

        # Boolean
        if value_str in ("true", "false"):
            return value_str == "true"

        # Array: [a, b, c]
        if value_str.startswith("[") and value_str.endswith("]"):
            inner = value_str[1:-1].strip()
            if not inner:
                return []
            items = []
            for item in self._split_array(inner):
                items.append(self._parse_value(item.strip()))
            return items

        # Object: { k: v }
        if value_str.startswith("{") and value_str.endswith("}"):
            return self._parse_object(value_str[1:-1].strip())

        # Reference: @TargetName
        if value_str.startswith("@"):
            return {"$ref": value_str[1:]}

        raise ValueError(f"Cannot parse: {value_str}")

    def _split_array(self, inner: str) -> list[str]:
        items = []
        depth = 0
        current = []
        i = 0
        while i < len(inner):
            c = inner[i]
            if c in ("{", "["):
                depth += 1
                current.append(c)
            elif c in ("}", "]"):
                depth -= 1
                current.append(c)
            elif c == "," and depth == 0:
                items.append("".join(current).strip())
                current = []
            else:
                current.append(c)
            i += 1
        if current:
            items.append("".join(current).strip())
        return items

    def _parse_object(self, inner: str) -> dict:
        obj = {}
        for item in self._split_array(inner):
            m = re.match(r'^(\w+)\s*:\s*(.+)$', item)
            if m:
                obj[m.group(1)] = self._parse_value(m.group(2).strip())
        return obj


# ──────────────────────────────────────────────────────────────────
# 3. Semantic Model Builder
# ──────────────────────────────────────────────────────────────────

class SemanticModel:
    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self.entities: dict[str, dict] = {}
        self.errors: list[str] = []

    def build(self, definitions: list[dict]) -> dict:
        for defn in definitions:
            entity_id = self._make_id(defn)
            entity = self._resolve_entity(defn, entity_id)
            self.entities[entity_id] = entity
        return self.entities

    def _make_id(self, defn: dict) -> str:
        raw = f"VENUS-{defn['type']}-{defn['name']}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:12]
        return f"VENUS-{defn['type'].upper()[:4]}-{h}"

    def _resolve_entity(self, defn: dict, entity_id: str) -> dict:
        entity = {
            "id": entity_id,
            "type": defn["type"],
            "name": defn["name"],
            "fields": {},
            "sub_entities": [],
        }

        # Type check
        mapped_type = self._map_type(defn["type"])
        if not self.ontology.is_valid_type(mapped_type):
            self.errors.append(f"Unknown ontology type '{mapped_type}' for {defn['name']}")
        entity["ontology_type"] = mapped_type

        # Copy fields
        entity["fields"] = dict(defn.get("fields", {}))

        # Recursively process sub-blocks
        for sub in defn.get("sub_blocks", []):
            sub_id = self._make_id(sub)
            sub_entity = self._resolve_entity(sub, sub_id)
            entity["sub_entities"].append(sub_entity)
            self.entities[sub_id] = sub_entity

        return entity

    @staticmethod
    def _map_type(block_type: str) -> str:
        mapping = {
            "operatingsystem": "OperatingSystem",
            "part": "Part",
            "module": "Module",
            "engine": "Engine",
            "template": "Template",
            "certificate": "Certificate",
            "stage": "Stage",
            "workflow": "Workflow",
            "policy": "Policy",
            "agent": "Agent",
            "memory": "Memory",
            "schema": "Schema",
            "interface": "Interface",
        }
        return mapping.get(block_type, "Entity")


# ──────────────────────────────────────────────────────────────────
# 4. Generators
# ──────────────────────────────────────────────────────────────────

class MarkdownGenerator:
    def generate(self, entity: dict, output_dir: Path):
        rel_path = self._path(entity)
        abs_path = output_dir / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# {entity['name']}",
            f"",
            f"**Type**: {entity['ontology_type']}",
            f"**ID**: `{entity['id']}`",
            f"",
        ]

        fields = entity.get("fields", {})
        if fields.get("description"):
            lines.extend([fields["description"], ""])

        if fields.get("capabilities"):
            lines.extend(["## Capabilities", ""])
            for c in fields["capabilities"]:
                lines.append(f"- {c}")
            lines.append("")

        if fields.get("inputs"):
            lines.extend(["## Inputs", ""])
            for inp in fields["inputs"]:
                name = inp.get("name", "?")
                typ = inp.get("type", "any")
                lines.append(f"- `{name}`: `{typ}`")
            lines.append("")

        if fields.get("outputs"):
            lines.extend(["## Outputs", ""])
            for out in fields["outputs"]:
                name = out.get("name", "?")
                typ = out.get("type", "any")
                lines.append(f"- `{name}`: `{typ}`")
            lines.append("")

        if fields.get("validation"):
            lines.extend(["## Validation", ""])
            for v in fields["validation"]:
                rule = v.get("rule", "?")
                sev = v.get("severity", "medium")
                lines.append(f"- `{rule}` (severity: {sev})")
            lines.append("")

        if fields.get("produces"):
            lines.extend(["## Produces", ""])
            for p in fields["produces"]:
                lines.append(f"- {p}")
            lines.append("")

        if entity.get("sub_entities"):
            lines.extend(["## Components", ""])
            for sub in entity["sub_entities"]:
                lines.append(f"- [{sub['name']}](#{sub['name'].lower().replace(' ', '-')})")
            lines.append("")
            for sub in entity["sub_entities"]:
                lines.append(f"### {sub['name']}")
                lines.append("")
                sf = sub.get("fields", {})
                if sf.get("description"):
                    lines.append(sf["description"])
                    lines.append("")

        abs_path.write_text("\n".join(lines))
        return rel_path

    @staticmethod
    def _path(entity: dict) -> str:
        return f"_generated/{entity['ontology_type']}/{entity['name']}.md"


class SchemaGenerator:
    def generate(self, entity: dict, output_dir: Path) -> str:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"venus://generated/{entity['ontology_type'].lower()}/{entity['name'].lower()}/v1",
            "title": entity["name"],
            "type": "object",
            "properties": {},
            "required": [],
        }

        fields = entity.get("fields", {})
        for key, value in fields.items():
            schema["properties"][key] = {"type": self._infer_type(value)}
            schema["required"].append(key)

        rel_path = f"_generated/schemas/{entity['name']}.schema.json"
        abs_path = output_dir / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(json.dumps(schema, indent=2))
        return rel_path

    @staticmethod
    def _infer_type(value) -> str:
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "string"


class MermaidGenerator:
    def generate(self, entity: dict, output_dir: Path) -> str:
        lines = ["graph TD"]
        main_id = entity["name"].replace(" ", "_")

        lines.append(f"  {main_id}[\"{entity['name']}\"]")

        for sub in entity.get("sub_entities", []):
            sub_id = sub["name"].replace(" ", "_")
            lines.append(f"  {sub_id}[\"{sub['name']}\"]")
            lines.append(f"  {main_id} --> {sub_id}")

            ss = sub.get("sub_entities", [])
            for s in ss:
                s_id = s["name"].replace(" ", "_")
                lines.append(f"  {s_id}[\"{s['name']}\"]")
                lines.append(f"  {sub_id} --> {s_id}")

        fields = entity.get("fields", {})
        if fields.get("produces"):
            for p in fields["produces"]:
                p_id = p.replace(" ", "_")
                lines.append(f"  {p_id}(\"{p}\")")
                lines.append(f"  {main_id} -.-> {p_id}")

        rel_path = f"_generated/diagrams/{entity['name']}.mmd"
        abs_path = output_dir / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text("\n".join(lines))
        return rel_path


# ──────────────────────────────────────────────────────────────────
# 5. Main Compiler
# ──────────────────────────────────────────────────────────────────

class VenusCompiler:
    def __init__(self, output_dir: str | Path = None):
        self.ontology = Ontology()
        self.parser = DSLParser()
        self.semantic = SemanticModel(self.ontology)
        self.markdown_gen = MarkdownGenerator()
        self.schema_gen = SchemaGenerator()
        self.mermaid_gen = MermaidGenerator()

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = ROOT_DIR / "_generated"

    def compile(self, source: str, filename: str = "<unknown>") -> dict:
        print(f"  Parsing: {filename}")
        ast = self.parser.parse(source, filename)

        print(f"  Building semantic model...")
        entities = self.semantic.build(ast["definitions"])

        if self.semantic.errors:
            print(f"  Warnings:")
            for e in self.semantic.errors:
                print(f"    {e}")

        results = {"entities": {}, "files_generated": []}

        for eid, entity in entities.items():
            print(f"  Generating artifacts for: {entity['name']} ({entity['ontology_type']})")
            md_path = self.markdown_gen.generate(entity, self.output_dir)
            sc_path = self.schema_gen.generate(entity, self.output_dir)
            di_path = self.mermaid_gen.generate(entity, self.output_dir)

            results["entities"][eid] = entity
            results["files_generated"].extend([str(md_path), str(sc_path), str(di_path)])

        return results

    def compile_file(self, filepath: str | Path) -> dict:
        path = Path(filepath)
        source = path.read_text()
        return self.compile(source, str(path))

    def update_catalog(self, results: dict):
        """Append generated entities to catalog.json."""
        if not CATALOG_PATH.exists():
            return

        try:
            catalog = json.loads(CATALOG_PATH.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            catalog = {}

        for eid, entity in results["entities"].items():
            if eid not in catalog:
                catalog[eid] = {
                    "venus_id": eid,
                    "name": entity["name"],
                    "type": entity["ontology_type"],
                    "layer": entity.get("fields", {}).get("layer", 0),
                    "version": str(entity.get("fields", {}).get("version", "generated")),
                    "schema": f"venus://generated/{entity['ontology_type'].lower()}/v1",
                    "path": f"_generated/{entity['ontology_type']}/{entity['name']}.md",
                    "generated": datetime.now(timezone.utc).isoformat(),
                }

        CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
        print(f"  Updated catalog.json ({len(catalog)} entries)")

    def update_graph(self, results: dict):
        """Add generated entities to knowledge graph."""
        for eid, entity in results["entities"].items():
            node = {
                "id": eid,
                "type": entity["ontology_type"],
                "label": entity["name"],
                "layer": entity.get("fields", {}).get("layer", 0),
                "generated": True,
            }

            # Append to nodes file
            if GRAPH_NODES_PATH.exists():
                try:
                    nodes = json.loads(GRAPH_NODES_PATH.read_text())
                except (json.JSONDecodeError, FileNotFoundError):
                    nodes = []
                if not any(n["id"] == eid for n in nodes):
                    nodes.append(node)
                GRAPH_NODES_PATH.write_text(json.dumps(nodes, indent=2))

    def compile_all(self):
        """Find and compile all .venus and .dsl files in the repository."""
        patterns = ["**/*.venus", "**/*.dsl"]
        files = []
        for p in patterns:
            files.extend(ROOT_DIR.rglob(p))

        if not files:
            print("No .venus or .dsl files found.")
            return

        all_results = {"entities": {}, "files_generated": []}
        for f in files:
            results = self.compile_file(f)
            all_results["entities"].update(results["entities"])
            all_results["files_generated"].extend(results["files_generated"])

        self.update_catalog(all_results)
        self.update_graph(all_results)

        print(f"\n── Compilation Complete ──")
        print(f"  Files compiled: {len(files)}")
        print(f"  Entities generated: {len(all_results['entities'])}")
        print(f"  Artifacts generated: {len(all_results['files_generated'])}")
        return all_results


# ──────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Venus DSL Compiler")
    parser.add_argument("--input", "-i", type=str, help="Input .venus or .dsl file")
    parser.add_argument("--output-dir", "-o", type=str, default=str(ROOT_DIR / "_generated"),
                        help="Output directory for generated artifacts")
    parser.add_argument("--compile-all", "-a", action="store_true",
                        help="Compile all .venus/.dsl files in repository")
    parser.add_argument("--update-catalog", action="store_true",
                        help="Update catalog.json with generated entities")
    parser.add_argument("--update-graph", action="store_true",
                        help="Update knowledge graph with generated entities")
    args = parser.parse_args()

    compiler = VenusCompiler(output_dir=args.output_dir)

    if args.compile_all:
        compiler.compile_all()
    elif args.input:
        results = compiler.compile_file(args.input)
        if args.update_catalog:
            compiler.update_catalog(results)
        if args.update_graph:
            compiler.update_graph(results)
        print(f"\n  Generated {len(results['files_generated'])} files")
        for f in results["files_generated"]:
            print(f"    {f}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
