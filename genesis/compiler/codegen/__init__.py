"""Code generation — produces final artifacts from UIR."""

from .base import CodeGenerator, CodeGenRegistry
from .markdown_gen import MarkdownGenerator
from .schema_gen import SchemaGenerator
from .graph_gen import GraphGenerator

__all__ = [
    "CodeGenerator", "CodeGenRegistry",
    "MarkdownGenerator", "SchemaGenerator", "GraphGenerator",
]
