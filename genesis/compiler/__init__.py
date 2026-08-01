"""Compiler Framework — multi-source parser, LLVM-style passes, code generation."""

from .compiler import Compiler
from .ast import ASTNode, AST
from .parser import Parser
from .uir_builder import UIRBuilder

__all__ = ["Compiler", "ASTNode", "AST", "Parser", "UIRBuilder"]
