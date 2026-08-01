"""JSON Schema generator — produces schemas from UIR."""

import json
from pathlib import Path
from typing import Any

from genesis.compiler.codegen.base import CodeGenerator
from genesis.core.uir import CompilationUnit


class SchemaGenerator(CodeGenerator):
    """Generates JSON Schemas from UIR type information."""

    def __init__(self):
        super().__init__("schema_generator", "schema")

    def generate(self, cu: CompilationUnit, output_dir: str | Path) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        for nid, node in cu.ast.nodes.items():
            if "value" not in node.attributes:
                continue
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": node.label,
                "type": "object",
                "properties": {},
                "required": [],
            }
            schema_path = output_dir / f"{node.label.upper() if node.label else 'UNNAMED'}_SCHEMA.json"
            schema_path.write_text(json.dumps(schema, indent=2))
            generated.append(schema_path)

        if not generated:
            generic = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "CompiledArtifact",
                "type": "object",
                "properties": {},
            }
            schema_path = output_dir / "COMPILED_ARTIFACT_SCHEMA.json"
            schema_path.write_text(json.dumps(generic, indent=2))
            generated.append(schema_path)

        return generated
