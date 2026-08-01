"""Multi-format parser: reads any source format and produces an AST."""

import json
import re
from pathlib import Path
from typing import Any

from genesis.compiler.ast import AST, ASTNode
from genesis.core.exceptions import CompilationError


class Parser:
    """Parses multiple formats into a unified AST."""

    SUPPORTED_FORMATS = {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".venus": "dsl",
        ".txt": "text",
    }

    @classmethod
    def detect_format(cls, path: str | Path) -> str:
        suffix = Path(path).suffix
        return cls.SUPPORTED_FORMATS.get(suffix, "unknown")

    @classmethod
    def parse(cls, path: str | Path) -> AST:
        path = Path(path)
        fmt = cls.detect_format(path)
        ast = AST(str(path), fmt)

        if fmt == "json":
            return cls._parse_json(path, ast)
        elif fmt == "yaml":
            return cls._parse_yaml(path, ast)
        elif fmt == "markdown":
            return cls._parse_markdown(path, ast)
        elif fmt == "dsl":
            return cls._parse_dsl(path, ast)
        elif fmt == "text":
            return cls._parse_text(path, ast)
        else:
            raise CompilationError(f"Unsupported format: {fmt} for {path}")

    @classmethod
    def parse_string(cls, content: str, fmt: str = "json", source_name: str = "<string>") -> AST:
        ast = AST(source_name, fmt)

        if fmt == "json":
            data = json.loads(content)
            root = ASTNode("json_document", name=source_name)
            cls._dict_to_ast(data, root)
            ast.root = root
        elif fmt == "markdown":
            ast.root = cls._parse_markdown_content(content, source_name)
        else:
            ast.root = ASTNode("document", value=content[:80], name=source_name)

        return ast

    @classmethod
    def _parse_json(cls, path: Path, ast: AST) -> AST:
        try:
            data = json.loads(path.read_text())
            root = ASTNode("json_document", name=path.stem)
            root.source_location = str(path)
            cls._dict_to_ast(data, root)
            ast.root = root
            return ast
        except json.JSONDecodeError as e:
            raise CompilationError(f"JSON parse error in {path}: {e}")

    @classmethod
    def _dict_to_ast(cls, data: Any, parent: ASTNode):
        if isinstance(data, dict):
            for key, value in data.items():
                node = ASTNode("key_value", name=str(key))
                node.source_location = parent.source_location
                parent.add_child(node)
                if isinstance(value, (dict, list)):
                    cls._dict_to_ast(value, node)
                else:
                    node.value = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                node = ASTNode("array_item", value=i)
                node.source_location = parent.source_location
                parent.add_child(node)
                if isinstance(item, (dict, list)):
                    cls._dict_to_ast(item, node)
                else:
                    node.value = item

    @classmethod
    def _parse_yaml(cls, path: Path, ast: AST) -> AST:
        try:
            import yaml
            data = yaml.safe_load(path.read_text())
            root = ASTNode("yaml_document", name=path.stem)
            root.source_location = str(path)
            cls._dict_to_ast(data, root)
            ast.root = root
            return ast
        except ImportError:
            raise CompilationError("PyYAML is required for YAML parsing")
        except Exception as e:
            raise CompilationError(f"YAML parse error in {path}: {e}")

    @classmethod
    def _parse_markdown(cls, path: Path, ast: AST) -> AST:
        content = path.read_text()
        ast.root = cls._parse_markdown_content(content, str(path))
        return ast

    @classmethod
    def _parse_markdown_content(cls, content: str, source: str) -> ASTNode:
        root = ASTNode("markdown_document", name=Path(source).stem)
        root.source_location = source

        current_section = root
        heading_stack = [root]

        for line in content.split("\n"):
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                node = ASTNode("heading", name=title)
                node.attributes["level"] = level
                node.source_location = source

                # Place under correct parent heading
                while len(heading_stack) > 1 and heading_stack[-1].attributes.get("level", 0) >= level:
                    heading_stack.pop()
                heading_stack[-1].add_child(node)
                heading_stack.append(node)
                current_section = node

            elif line.startswith("- "):
                node = ASTNode("list_item", value=line[2:])
                node.source_location = source
                current_section.add_child(node)

            elif line.startswith("|"):
                node = ASTNode("table_row", value=line)
                node.source_location = source
                current_section.add_child(node)

            elif line.strip():
                node = ASTNode("paragraph", value=line.strip())
                node.source_location = source
                current_section.add_child(node)

        return root

    @classmethod
    def _parse_dsl(cls, path: Path, ast: AST) -> AST:
        """Parse .venus DSL files."""
        content = path.read_text()
        root = ASTNode("dsl_program", name=path.stem)
        root.source_location = str(path)

        current_block = root
        for i, line in enumerate(content.split("\n")):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            # Entity definition: type name { ... }
            entity_match = re.match(r"^(\w+)\s+(\w+)\s*\{", line)
            if entity_match:
                node = ASTNode("entity_definition", name=entity_match.group(2))
                node.attributes["entity_type"] = entity_match.group(1)
                node.source_line = i + 1
                root.add_child(node)
                current_block = node

            # Key: value
            kv_match = re.match(r"^(\w+)\s*:\s*(.+)$", line)
            if kv_match:
                node = ASTNode("property", name=kv_match.group(1))
                node.value = kv_match.group(2).strip()
                node.source_line = i + 1
                current_block.add_child(node)

            # Closing brace
            if line == "}":
                current_block = root

            # Array: - value
            arr_match = re.match(r"^\s*-\s+(.+)$", line)
            if arr_match:
                node = ASTNode("array_item", value=arr_match.group(1).strip())
                current_block.add_child(node)

        ast.root = root
        return ast

    @classmethod
    def _parse_text(cls, path: Path, ast: AST) -> AST:
        content = path.read_text()
        root = ASTNode("text_document", name=path.stem)
        root.source_location = str(path)
        root.value = content[:500]
        ast.root = root
        return ast
