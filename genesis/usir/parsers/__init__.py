"""
Python USIR Adapter — compiles Python AST to USIR.

Supports:
  modules, classes, functions, methods, fields, decorators,
  imports, inheritance, async, generators, type hints,
  docstrings, visibility, exceptions, comprehensions,
  pattern matching, dataclasses, protocols, abstract classes
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from genesis.usir import (
    USIRGraph,
    USIRKind,
    USIRNode,
    Mutability,
    VISIBILITY_PRIVATE,
    VISIBILITY_PROTECTED,
    VISIBILITY_PUBLIC,
)
from genesis.usir.language import LanguageAdapter


class PythonAdapter(LanguageAdapter):
    """Python → USIR compiler. Uses built-in ast module."""

    def language_name(self) -> str:
        return "python"

    def file_extensions(self) -> set[str]:
        return {".py"}

    def parse_file(self, path: Path, source_root: Path) -> USIRGraph:
        graph = USIRGraph()
        rel_path = str(path.relative_to(source_root))
        source_text = path.read_text()

        try:
            tree = ast.parse(source_text)
        except SyntaxError:
            return graph

        # — module node —
        module_node = USIRNode(
            id=rel_path,
            kind=USIRKind.MODULE,
            name=path.stem,
            qualified_name=rel_path.replace("/", ".").replace(".py", ""),
            language="python",
            source_file=rel_path,
            source_line=1,
            docstring=ast.get_docstring(tree),
        )
        graph.add_node(module_node)

        # — process top-level statements —
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                self._process_import(graph, node, module_node, rel_path)
            elif isinstance(node, ast.ImportFrom):
                self._process_import_from(graph, node, module_node, rel_path)
            elif isinstance(node, ast.ClassDef):
                self._process_class(graph, node, module_node, rel_path, source_text)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(graph, node, module_node, rel_path, source_text)
            elif isinstance(node, ast.Assign):
                self._process_assign(graph, node, module_node, rel_path)

        return graph

    def _process_import(self, graph: USIRGraph, node: ast.Import, parent: USIRNode, rel_path: str):
        for alias in node.names:
            imp_node = USIRNode(
                id=f"{rel_path}::import::{alias.name}",
                kind=USIRKind.IMPORT,
                name=alias.name,
                qualified_name=alias.name,
                language="python",
                source_file=rel_path,
                source_line=node.lineno or 0,
            )
            if alias.asname:
                imp_node.name = alias.asname
            graph.add_node(imp_node)
            parent.imports.append({"module": alias.name, "alias": alias.asname or alias.name})
            parent.children.append(imp_node.id)

    def _process_import_from(self, graph: USIRGraph, node: ast.ImportFrom, parent: USIRNode, rel_path: str):
        module = node.module or ""
        for alias in node.names:
            imp_node = USIRNode(
                id=f"{rel_path}::import::{module}.{alias.name}",
                kind=USIRKind.IMPORT,
                name=alias.name,
                qualified_name=f"{module}.{alias.name}",
                language="python",
                source_file=rel_path,
                source_line=node.lineno or 0,
            )
            if alias.asname:
                imp_node.name = alias.asname
            graph.add_node(imp_node)
            parent.imports.append({"module": module, "name": alias.name, "alias": alias.asname or alias.name})
            parent.children.append(imp_node.id)

    def _process_class(self, graph: USIRGraph, node: ast.ClassDef, parent: USIRNode,
                       rel_path: str, source_text: str):
        bases = []
        interfaces = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id.endswith("Protocol"):
                    interfaces.append(base.id)
                else:
                    bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                if isinstance(base.value, ast.Name):
                    bases.append(f"{base.value.id}.{base.attr}")
                else:
                    bases.append(base.attr)

        kind = USIRKind.CLASS
        if "Protocol" in str(bases) or "Protocol" in str(interfaces):
            kind = USIRKind.PROTOCOL
        elif any("ABC" in b for b in bases):
            kind = USIRKind.INTERFACE
        elif node.name.endswith("Mixin"):
            kind = USIRKind.TRAIT

        is_abstract = any(
            isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(d, ast.Name) and d.id == "abstractmethod"
                for d in item.decorator_list
            )
            for item in ast.iter_child_nodes(node)
        )

        class_node = USIRNode(
            id=f"{rel_path}::{node.name}",
            kind=kind,
            name=node.name,
            qualified_name=f"{parent.qualified_name}.{node.name}",
            language="python",
            source_file=rel_path,
            source_line=node.lineno or 0,
            docstring=ast.get_docstring(node),
            base_types=bases,
            implemented_interfaces=interfaces,
            is_abstract=is_abstract,
            lines_of_code=self._node_lines(source_text, node),
        )
        class_node.complexity = self._compute_class_complexity(node)
        graph.add_node(class_node)
        parent.children.append(class_node.id)

        # — decorators —
        for deco in node.decorator_list:
            deco_name = self._expr_name(deco)
            if deco_name:
                class_node.decorators.append(deco_name)

        # — fields and methods —
        for item in ast.iter_child_nodes(node):
            if isinstance(item, ast.FunctionDef):
                self._process_method(graph, item, class_node, rel_path, source_text)
            elif isinstance(item, ast.AsyncFunctionDef):
                self._process_method(graph, item, class_node, rel_path, source_text)
            elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                self._process_field(graph, item, class_node, rel_path)

    def _process_method(self, graph: USIRGraph, node: ast.FunctionDef | ast.AsyncFunctionDef,
                        parent: USIRNode, rel_path: str, source_text: str):
        # — detect constructor —
        kind = USIRKind.METHOD
        if node.name == "__init__":
            kind = USIRKind.CONSTRUCTOR
        elif node.name.startswith("__") and node.name.endswith("__"):
            kind = USIRKind.METHOD

        # — visibility from name convention —
        visibility = VISIBILITY_PUBLIC
        if node.name.startswith("__") and not node.name.endswith("__"):
            visibility = VISIBILITY_PRIVATE
        elif node.name.startswith("_"):
            visibility = VISIBILITY_PROTECTED

        # — async —
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # — return type from annotation —
        return_type = None
        if node.returns:
            return_type = self._expr_name(node.returns)

        method_node = USIRNode(
            id=f"{parent.id}::{node.name}",
            kind=kind,
            name=node.name,
            qualified_name=f"{parent.qualified_name}.{node.name}",
            language="python",
            source_file=rel_path,
            source_line=node.lineno or 0,
            docstring=ast.get_docstring(node),
            visibility=visibility,
            is_async=is_async,
            is_static=self._has_decorator(node, "staticmethod"),
            is_abstract=self._has_decorator(node, "abstractmethod"),
            return_type=return_type,
            lines_of_code=self._node_lines(source_text, node),
        )
        method_node.complexity = self._compute_function_complexity(node)

        # — parameters —
        for arg in node.args.args:
            arg_type = None
            if arg.annotation:
                arg_type = self._expr_name(arg.annotation)
            method_node.children.append(
                f"{method_node.id}::param::{arg.arg}"
            )
            param_node = USIRNode(
                id=f"{method_node.id}::param::{arg.arg}",
                kind=USIRKind.PARAMETER,
                name=arg.arg,
                language="python",
                source_file=rel_path,
                source_line=arg.lineno if hasattr(arg, 'lineno') else 0,
                type_ref=arg_type,
            )
            graph.add_node(param_node)

        # — decorators —
        for deco in node.decorator_list:
            deco_name = self._expr_name(deco)
            if deco_name:
                method_node.decorators.append(deco_name)

        graph.add_node(method_node)
        parent.children.append(method_node.id)

    def _process_field(self, graph: USIRGraph, node: ast.Assign | ast.AnnAssign,
                       parent: USIRNode, rel_path: str):
        targets = []
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            targets = node.targets

        for target in targets:
            if isinstance(target, ast.Name):
                name = target.id
                visibility = VISIBILITY_PUBLIC
                if name.startswith("__"):
                    visibility = VISIBILITY_PRIVATE
                elif name.startswith("_"):
                    visibility = VISIBILITY_PROTECTED

                type_ref = None
                if isinstance(node, ast.AnnAssign) and node.annotation:
                    type_ref = self._expr_name(node.annotation)

                field_node = USIRNode(
                    id=f"{parent.id}::{name}",
                    kind=USIRKind.FIELD,
                    name=name,
                    qualified_name=f"{parent.qualified_name}.{name}",
                    language="python",
                    source_file=rel_path,
                    source_line=node.lineno or 0,
                    visibility=visibility,
                    type_ref=type_ref,
                )
                graph.add_node(field_node)
                parent.children.append(field_node.id)

    def _process_function(self, graph: USIRGraph, node: ast.FunctionDef | ast.AsyncFunctionDef,
                          parent: USIRNode, rel_path: str, source_text: str):
        is_async = isinstance(node, ast.AsyncFunctionDef)
        return_type = self._expr_name(node.returns) if node.returns else None

        fn_node = USIRNode(
            id=f"{rel_path}::{node.name}",
            kind=USIRKind.FUNCTION,
            name=node.name,
            qualified_name=f"{parent.qualified_name}.{node.name}",
            language="python",
            source_file=rel_path,
            source_line=node.lineno or 0,
            docstring=ast.get_docstring(node),
            is_async=is_async,
            is_generator=self._is_generator(node),
            return_type=return_type,
            lines_of_code=self._node_lines(source_text, node),
        )
        fn_node.complexity = self._compute_function_complexity(node)
        graph.add_node(fn_node)
        parent.children.append(fn_node.id)

        # — decorators —
        for deco in node.decorator_list:
            deco_name = self._expr_name(deco)
            if deco_name:
                fn_node.decorators.append(deco_name)

    def _process_assign(self, graph: USIRGraph, node: ast.Assign, parent: USIRNode, rel_path: str):
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_node = USIRNode(
                    id=f"{rel_path}::{target.id}",
                    kind=USIRKind.VARIABLE,
                    name=target.id,
                    qualified_name=f"{parent.qualified_name}.{target.id}",
                    language="python",
                    source_file=rel_path,
                    source_line=node.lineno or 0,
                )
                graph.add_node(var_node)

    # — helpers —

    def _expr_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._expr_name(node.value) or ""
            return f"{base}.{node.attr}" if base else node.attr
        elif isinstance(node, ast.Subscript):
            base = self._expr_name(node.value) or ""
            return f"{base}[...]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return None

    def _has_decorator(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, name: str) -> bool:
        return any(
            isinstance(d, ast.Name) and d.id == name
            for d in node.decorator_list
        )

    def _is_generator(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for child in ast.walk(node):
            if isinstance(child, ast.Yield) or isinstance(child, ast.YieldFrom):
                return True
        return False

    def _node_lines(self, source_text: str, node: ast.AST) -> int:
        end = getattr(node, "end_lineno", node.lineno or 0)
        start = node.lineno or 0
        return max(end - start + 1, 0)

    def _compute_function_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                  ast.ExceptHandler, ast.With, ast.AsyncWith,
                                  ast.Try, ast.Raise, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1 if child.values else 0
            elif isinstance(child, ast.Match):
                complexity += len(child.cases)
            elif isinstance(child, (ast.comprehension, ast.ListComp, ast.SetComp,
                                    ast.DictComp, ast.GeneratorExp)):
                complexity += 1
        return complexity

    def _compute_class_complexity(self, node: ast.ClassDef) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def __repr__(self) -> str:
        return "PythonAdapter"
