"""Abstract Syntax Tree definitions for all source formats."""

from datetime import datetime, timezone
from typing import Any


class ASTNode:
    """A single node in the Abstract Syntax Tree."""

    def __init__(self, node_type: str, value: Any = None, name: str = ""):
        self.node_type = node_type
        self.value = value
        self.name = name
        self.children: list[ASTNode] = []
        self.attributes: dict[str, Any] = {}
        self.source_location: str = ""
        self.source_line: int = 0

    def add_child(self, child: "ASTNode"):
        self.children.append(child)

    def find(self, node_type: str) -> list["ASTNode"]:
        """Recursively find all children of a given type."""
        results = []
        if self.node_type == node_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find(node_type))
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_type": self.node_type,
            "value": self.value,
            "name": self.name,
            "children": [c.to_dict() for c in self.children],
            "attributes": dict(self.attributes),
        }

    def __repr__(self) -> str:
        return f"<AST:{self.node_type}:{self.name or self.value}>"


class AST:
    """Complete Abstract Syntax Tree for a compilation unit."""

    def __init__(self, source_path: str = "", source_format: str = ""):
        self.source_path = source_path
        self.source_format = source_format
        self.root: ASTNode = ASTNode("program", name="root")
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_node(self, parent_type: str, node: ASTNode) -> bool:
        """Add a node under the first parent matching parent_type."""
        parents = self.root.find(parent_type)
        if parents:
            parents[0].add_child(node)
            return True
        # Fall back to root
        self.root.add_child(node)
        return False

    def find(self, node_type: str) -> list[ASTNode]:
        return self.root.find(node_type)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "source_format": self.source_format,
            "root": self.root.to_dict(),
            "created_at": self.created_at,
        }
