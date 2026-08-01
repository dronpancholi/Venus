"""
TypeScript/JavaScript USIR Adapter.

Heuristic parser that handles:
  - ESM imports/exports, CommonJS require/module.exports
  - Classes, interfaces, type aliases, enums
  - Functions (async, arrow, generators), methods
  - Decorators, generics, visibility modifiers
  - JSX/TSX detection
"""

from __future__ import annotations

import ast  # only for node_id hashing
import re
from pathlib import Path
from typing import Any

from genesis.usir import (
    USIRGraph, USIRNode, USIRKind,
    Mutability, VISIBILITY_PUBLIC, VISIBILITY_PRIVATE, VISIBILITY_PROTECTED,
)
from genesis.usir.language import LanguageAdapter

# — regex patterns —

RE_IMPORT_DEFAULT = re.compile(
    r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
)
RE_IMPORT_NAMED = re.compile(
    r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]'
)
RE_IMPORT_NAMESPACE = re.compile(
    r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
)
RE_IMPORT_SIDE_EFFECT = re.compile(
    r'import\s+[\'"]([^\'"]+)[\'"]'
)
RE_IMPORT_TYPE = re.compile(
    r'import\s+type\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]'
)
RE_REQUIRE = re.compile(
    r'(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
)
RE_EXPORT_DEFAULT = re.compile(
    r'export\s+default\s+(class|function|const|let|var|abstract\s+class)\s+(\w+)'
)
RE_EXPORT_NAMED = re.compile(
    r'export\s+(?:declare\s+)?(?:abstract\s+)?(class|interface|type|enum|const|let|var|function|async\s+function|namespace|module)\s+(\w+)'
)
RE_EXPORT_MODULE = re.compile(
    r'module\.exports\s*=\s*(\w+)'
)
RE_CLASS = re.compile(
    r'(?:export\s+)?(?:declare\s+)?(?:abstract\s+)?class\s+(\w+)'
    r'(?:<([^>]+)>)?'
    r'(?:\s+extends\s+(\w+(?:\.\w+)*(?:<[^>]+>)?))?'
    r'(?:\s+implements\s+([\w\s,.<>]+))?'
)
RE_INTERFACE = re.compile(
    r'(?:export\s+)?(?:declare\s+)?interface\s+(\w+)'
    r'(?:<([^>]+)>)?'
    r'(?:\s+extends\s+([\w\s,.<>]+))?'
)
RE_TYPE_ALIAS = re.compile(
    r'(?:export\s+)?type\s+(\w+)(?:<([^>]+)>)?\s*='
)
RE_ENUM = re.compile(
    r'(?:export\s+)?(?:declare\s+)?(?:const\s+)?enum\s+(\w+)'
)
RE_FUNCTION = re.compile(
    r'(?:export\s+)?(?:async\s+)?function\s*(\w+)\s*\('
)
RE_ARROW_FN = re.compile(
    r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>'
)
RE_METHOD = re.compile(
    r'(?:public|private|protected|static|readonly|abstract|async|override|\s)*\s+'
    r'(?:get\s+|set\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[\w<>[\]|&, ]+)?\s*(?:\{|;)'
)
RE_CONSTRUCTOR = re.compile(
    r'constructor\s*\('
)
RE_DECORATOR = re.compile(
    r'@(\w+(?:\.\w+)?)(?:\(([^)]*)\))?'
)
RE_GETTER = re.compile(
    r'(?:public|private|protected)?\s*get\s+(\w+)\s*\(\)'
)
RE_SETTER = re.compile(
    r'(?:public|private|protected)?\s*set\s+(\w+)\s*\((\w+)\)'
)
RE_VISIBILITY = re.compile(
    r'(public|private|protected|readonly|static|abstract|override)\s+'
)
RE_GENERIC = re.compile(
    r'(\w+)<([^<>]+)>'
)
RE_NAMESPACE = re.compile(
    r'(?:export\s+)?(?:declare\s+)?namespace\s+(\w+(?:\.\w+)*)'
)
RE_MODULE_DECL = re.compile(
    r'(?:export\s+)?(?:declare\s+)?module\s+[\'"]([^\'"]+)[\'"]'
)

# — keywords that look like identifiers but aren't —
TS_RESERVED = {
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
    'try', 'catch', 'finally', 'throw', 'return', 'break', 'continue',
    'new', 'delete', 'typeof', 'instanceof', 'void', 'in', 'of',
    'this', 'super', 'yield', 'await', 'async', 'from',
}


def _sanitize_id(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def _count_lines(text: str, start: int, char: str = '{') -> tuple[str, int]:
    """Extract a brace-delimited block starting at position, returning content and end line."""
    depth = 0
    in_block = False
    lines = text[start:].split('\n')
    result_lines = []
    for i, line in enumerate(lines):
        in_string = False
        in_template = False
        j = 0
        while j < len(line):
            c = line[j]
            if c in ('"', "'", '`') and (j == 0 or line[j-1] != '\\'):
                if c == '`':
                    in_template = not in_template
                else:
                    in_string = not in_string
            if not in_string and not in_template:
                if c == '{':
                    depth += 1
                    in_block = True
                elif c == '}':
                    depth -= 1
                    if depth == 0 and in_block:
                        result_lines.append(line[:j])
                        return '\n'.join(result_lines), start + sum(len(l) + 1 for l in result_lines)
            j += 1
        result_lines.append(line)
    return '\n'.join(result_lines), start + sum(len(l) + 1 for l in result_lines)


def _extract_body(source: str, start_pos: int) -> tuple[str, int]:
    """Extract the body of a braced construct starting at or after start_pos."""
    brace_pos = source.find('{', start_pos)
    if brace_pos == -1:
        return "", start_pos
    return _count_lines(source, brace_pos)


class TypeScriptAdapter(LanguageAdapter):
    """USIR adapter for TypeScript (.ts, .tsx) and JavaScript (.js, .jsx, .mjs)."""

    def language_name(self) -> str:
        return "typescript"

    def file_extensions(self) -> set[str]:
        return {'.ts', '.tsx'}

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.file_extensions() and path.is_file()

    def parse_file(self, path: Path, source_root: Path | None = None) -> USIRGraph:
        graph = USIRGraph()
        source = path.read_text(encoding='utf-8', errors='replace')
        lines = source.split('\n')
        if source_root:
            try:
                rel_path = path.relative_to(source_root)
            except ValueError:
                rel_path = Path(path.name)
        else:
            rel_path = Path(path.name)
        file_id = f"{self.language_name()}::{_sanitize_id(str(rel_path))}"

        # — module node —
        module_node = USIRNode(
            id=file_id,
            kind=USIRKind.MODULE,
            name=path.stem,
            qualified_name=str(rel_path).replace('/', '.'),
            language=self.language_name(),
            source_file=str(rel_path),
            source_line=1,
            lines_of_code=len(lines),
        )
        graph.add_node(module_node)
        module_children = []

        # — state —
        imports: list[dict[str, str]] = []
        decorators: list[str] = []
        next_node_id = 0
        construct_id: int = 0

        def _make_id(prefix: str, name: str, sfx: str = "") -> str:
            nonlocal next_node_id
            next_node_id += 1
            s = f"{file_id}::{prefix}_{_sanitize_id(name)}"
            if sfx:
                s += f"_{sfx}"
            return s

        # — Pass 1: Collect decorators (need to track before class/fn declarations) —
        decorator_map: dict[int, list[str]] = {}
        for i, line in enumerate(lines):
            m = RE_DECORATOR.search(line)
            if m:
                decorator_map[i] = decorator_map.get(i, []) + [m.group(1)]

        # — Pass 2: Parse constructs —
        i = 0
        while i < len(lines):
            line = lines[i]
            trimmed = line.strip()
            line_decorators = decorator_map.get(i, [])

            # — Imports: named { a, b } from 'mod' —
            m = RE_IMPORT_NAMED.search(trimmed)
            if m:
                parts = [p.strip() for p in m.group(1).split(',') if p.strip()]
                mod = m.group(2)
                for p in parts:
                    p = p.split(' as ')[0].strip()
                    if p:
                        imports.append({'module': mod, 'symbol': p})
                i += 1
                continue

            # — Imports: default import from 'mod' —
            m = RE_IMPORT_DEFAULT.search(trimmed)
            if m:
                imports.append({'module': m.group(2), 'symbol': m.group(1)})
                i += 1
                continue

            # — Imports: namespace * as name from 'mod' —
            m = RE_IMPORT_NAMESPACE.search(trimmed)
            if m:
                imports.append({'module': m.group(2), 'symbol': m.group(1), 'namespace': 'true'})
                i += 1
                continue

            # — Imports: side-effect import 'mod' —
            m = RE_IMPORT_SIDE_EFFECT.search(trimmed)
            if m and trimmed.startswith('import'):
                imports.append({'module': m.group(1), 'symbol': ''})
                i += 1
                continue

            # — Imports: type-only { a, b } from 'mod' —
            m = RE_IMPORT_TYPE.search(trimmed)
            if m:
                parts = [p.strip() for p in m.group(1).split(',') if p.strip()]
                for p in parts:
                    imports.append({'module': m.group(2), 'symbol': p, 'type_only': 'true'})
                i += 1
                continue

            # — CommonJS require —
            m = RE_REQUIRE.search(trimmed)
            if m:
                imports.append({'module': m.group(2), 'symbol': m.group(1)})
                i += 1
                continue

            # — Export default —
            m = RE_EXPORT_DEFAULT.search(trimmed)
            if m:
                name = m.group(2)
                nid = _make_id('export_default', name)
                kind_map = {'class': USIRKind.CLASS, 'function': USIRKind.FUNCTION,
                            'const': USIRKind.CONSTANT}
                kind = kind_map.get(m.group(1), USIRKind.VARIABLE)
                node = USIRNode(
                    id=nid, kind=kind, name=name,
                    qualified_name=f"{path.stem}.default.{name}",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1, decorators=line_decorators,
                )
                graph.add_node(node)
                module_children.append(nid)
                graph.add_edge(file_id, nid, "contains", f"export_default:{name}")
                i += 1
                continue

            # — Export named —
            m = RE_EXPORT_NAMED.search(trimmed)
            if m:
                kind_str = m.group(1).replace('async ', '')
                name = m.group(2)
                if name not in TS_RESERVED:
                    nid = _make_id('export', name)
                    kind_map = {'class': USIRKind.CLASS, 'interface': USIRKind.INTERFACE,
                                'type': USIRKind.ALIAS, 'enum': USIRKind.ENUM,
                                'const': USIRKind.CONSTANT, 'function': USIRKind.FUNCTION,
                                'namespace': USIRKind.NAMESPACE, 'module': USIRKind.MODULE}
                    kind = kind_map.get(kind_str, USIRKind.VARIABLE)
                    node = USIRNode(
                        id=nid, kind=kind, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1, decorators=line_decorators,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"export:{name}")
                i += 1
                continue

            # — Class declaration —
            m = RE_CLASS.search(trimmed)
            if m:
                name = m.group(1)
                if name not in TS_RESERVED:
                    nid = _make_id('class', name)
                    base = m.group(3) or ''
                    impl_str = m.group(4) or ''
                    interfaces = [x.strip() for x in impl_str.split(',') if x.strip()]
                    node = USIRNode(
                        id=nid, kind=USIRKind.CLASS, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1, decorators=line_decorators,
                        base_types=[base] if base else [],
                        implemented_interfaces=interfaces,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"class:{name}")

                    # — extract class body —
                    body_start = source.find('{', sum(len(lines[j]) + 1 for j in range(i)))
                    if body_start > 0:
                        body, end_pos = _extract_body(source, body_start)
                        self._parse_class_body(body, name, nid, graph, rel_path, file_id)
                    i += 1
                    continue

            # — Interface declaration —
            m = RE_INTERFACE.search(trimmed)
            if m:
                name = m.group(1)
                if name not in TS_RESERVED:
                    nid = _make_id('interface', name)
                    extends_str = m.group(3) or ''
                    base_types = [x.strip() for x in extends_str.split(',') if x.strip()]
                    node = USIRNode(
                        id=nid, kind=USIRKind.INTERFACE, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1, base_types=base_types,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"interface:{name}")
                i += 1
                continue

            # — Type alias —
            m = RE_TYPE_ALIAS.search(trimmed)
            if m:
                name = m.group(1)
                if name not in TS_RESERVED:
                    nid = _make_id('type', name)
                    node = USIRNode(
                        id=nid, kind=USIRKind.ALIAS, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"type:{name}")
                i += 1
                continue

            # — Enum —
            m = RE_ENUM.search(trimmed)
            if m:
                name = m.group(1)
                if name not in TS_RESERVED:
                    nid = _make_id('enum', name)
                    node = USIRNode(
                        id=nid, kind=USIRKind.ENUM, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"enum:{name}")

                    # — extract enum members —
                    body_start = source.find('{', sum(len(lines[j]) + 1 for j in range(i)))
                    if body_start > 0:
                        body, end_pos = _extract_body(source, body_start)
                        for line_b in body.split('\n'):
                            enum_m = re.match(r'\s*(\w+)\s*(?:=|,)', line_b)
                            if enum_m:
                                ev_name = enum_m.group(1)
                                ev_id = _make_id('enum_variant', name, ev_name)
                                ev_node = USIRNode(
                                    id=ev_id, kind=USIRKind.ENUM_VARIANT, name=ev_name,
                                    qualified_name=f"{path.stem}.{name}.{ev_name}",
                                    language=self.language_name(), source_file=str(rel_path),
                                    source_line=i + 1,
                                )
                                graph.add_node(ev_node)
                                graph.add_edge(nid, ev_id, "contains", f"variant:{ev_name}")
                    i += 1
                    continue

            # — Namespace —
            m = RE_NAMESPACE.search(trimmed)
            if m:
                name = m.group(1)
                nid = _make_id('namespace', name)
                node = USIRNode(
                    id=nid, kind=USIRKind.NAMESPACE, name=name,
                    qualified_name=f"{path.stem}.{name}",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1,
                )
                graph.add_node(node)
                module_children.append(nid)
                graph.add_edge(file_id, nid, "contains", f"namespace:{name}")
                i += 1
                continue

            # — Function declaration —
            if trimmed.startswith('function') or trimmed.startswith('async function') or \
               trimmed.startswith('export function') or trimmed.startswith('export async function'):
                m = RE_FUNCTION.search(trimmed)
                if m:
                    name = m.group(1)
                    if name not in TS_RESERVED:
                        nid = _make_id('function', name)
                        node = USIRNode(
                            id=nid, kind=USIRKind.FUNCTION, name=name,
                            qualified_name=f"{path.stem}.{name}",
                            language=self.language_name(), source_file=str(rel_path),
                            source_line=i + 1, is_async='async' in trimmed,
                        )
                        graph.add_node(node)
                        module_children.append(nid)
                        graph.add_edge(file_id, nid, "contains", f"function:{name}")
                i += 1
                continue

            # — Arrow function assigned to variable —
            m = RE_ARROW_FN.search(trimmed)
            if m and trimmed.count('=>') >= 1:
                name = m.group(1)
                if name not in TS_RESERVED and not trimmed.startswith('import'):
                    nid = _make_id('fn', name)
                    node = USIRNode(
                        id=nid, kind=USIRKind.FUNCTION, name=name,
                        qualified_name=f"{path.stem}.{name}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1, is_async='async' in trimmed,
                    )
                    graph.add_node(node)
                    module_children.append(nid)
                    graph.add_edge(file_id, nid, "contains", f"arrow_fn:{name}")
                i += 1
                continue

            # — module.exports —
            m = RE_EXPORT_MODULE.search(trimmed)
            if m:
                name = m.group(1)
                nid = _make_id('export', name)
                node = USIRNode(
                    id=nid, kind=USIRKind.VARIABLE, name=name,
                    qualified_name=f"{path.stem}.exports.{name}",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1,
                )
                graph.add_node(node)
                module_children.append(nid)
                graph.add_edge(file_id, nid, "contains", f"exports:{name}")
                i += 1
                continue

            i += 1

        # — attach imports to module —
        if imports:
            module_node.imports = imports
            for imp in imports:
                imp_id = _make_id('import', _sanitize_id(imp.get('symbol', imp.get('module', 'unknown'))))
                imp_node = USIRNode(
                    id=imp_id, kind=USIRKind.IMPORT,
                    name=imp.get('symbol', imp.get('module', '')),
                    qualified_name=imp.get('module', ''),
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=1,
                )
                graph.add_node(imp_node)
                graph.add_edge(file_id, imp_id, "contains", f"import:{imp.get('module')}")

        module_node.children = module_children
        return graph

    def _parse_class_body(self, body: str, class_name: str, class_id: str,
                          graph: USIRGraph, rel_path: Path, file_id: str):
        """Parse class body for methods, properties, constructor."""
        lines = body.split('\n')
        is_inside_method = False
        brace_depth = 0

        for i, line in enumerate(lines):
            trimmed = line.strip()

            # — constructor —
            if RE_CONSTRUCTOR.search(trimmed):
                cid = f"{class_id}::constructor"
                cnode = USIRNode(
                    id=cid, kind=USIRKind.CONSTRUCTOR, name=f"{class_name}.constructor",
                    qualified_name=f"{rel_path.stem}.{class_name}.constructor",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1,
                )
                graph.add_node(cnode)
                graph.add_edge(class_id, cid, "contains", "constructor")
                continue

            # — getter —
            m = RE_GETTER.search(trimmed)
            if m and not trimmed.startswith('//'):
                prop_name = m.group(1)
                pid = f"{class_id}::get_{prop_name}"
                pnode = USIRNode(
                    id=pid, kind=USIRKind.PROPERTY, name=prop_name,
                    qualified_name=f"{rel_path.stem}.{class_name}.{prop_name}",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1,
                )
                graph.add_node(pnode)
                graph.add_edge(class_id, pid, "contains", f"getter:{prop_name}")
                continue

            # — setter —
            m = RE_SETTER.search(trimmed)
            if m and not trimmed.startswith('//'):
                prop_name = m.group(1)
                pid = f"{class_id}::set_{prop_name}"
                pnode = USIRNode(
                    id=pid, kind=USIRKind.PROPERTY, name=prop_name,
                    qualified_name=f"{rel_path.stem}.{class_name}.{prop_name}",
                    language=self.language_name(), source_file=str(rel_path),
                    source_line=i + 1,
                )
                graph.add_node(pnode)
                graph.add_edge(class_id, pid, "contains", f"setter:{prop_name}")
                continue

            # — method (name followed by parentheses) —
            method_match = re.match(
                r'\s*(?:public|private|protected|static|readonly|abstract|async|override|\s)*\s*'
                r'(\w+)\s*\(', trimmed
            )
            if method_match and not trimmed.startswith(('//', '*', '/**')):
                mname = method_match.group(1)
                if mname not in TS_RESERVED and mname != class_name:
                    is_async = 'async' in trimmed
                    mid = f"{class_id}::method_{mname}"
                    visibility = VISIBILITY_PUBLIC
                    if 'private' in trimmed:
                        visibility = VISIBILITY_PRIVATE
                    elif 'protected' in trimmed:
                        visibility = VISIBILITY_PROTECTED
                    mnode = USIRNode(
                        id=mid, kind=USIRKind.METHOD, name=mname,
                        qualified_name=f"{rel_path.stem}.{class_name}.{mname}",
                        language=self.language_name(), source_file=str(rel_path),
                        source_line=i + 1, visibility=visibility,
                        is_static='static' in trimmed,
                        is_async=is_async,
                        is_abstract='abstract' in trimmed,
                        is_override='override' in trimmed,
                    )
                    graph.add_node(mnode)
                    graph.add_edge(class_id, mid, "contains", f"method:{mname}")

                    # — check for arrow method instead —
                    if '=>' in trimmed.split('(')[-1] if '(' in trimmed else False:
                        pass

        # — property declarations (field: type) —
        prop_pattern = re.compile(
            r'\s*(?:public|private|protected|readonly|static)?\s*'
            r'(\w+)\s*:\s*([\w<>[\]|&, ]+)\s*[;=]'
        )
        for line in body.split('\n'):
            # skip method-looking lines
            if '(' in line.split(':')[0] if ':' in line else False:
                continue
            m = prop_pattern.search(line)
            if m:
                pname = m.group(1)
                ptype = m.group(2)
                if pname not in TS_RESERVED and pname != class_name:
                    # only create property if not a method
                    # heuristic: if line has parentheses, it's likely a method
                    if '(' not in line or line.find('(') > line.find(':'):
                        pid2 = f"{class_id}::field_{pname}"
                        pnode2 = USIRNode(
                            id=pid2, kind=USIRKind.FIELD, name=pname,
                            qualified_name=f"{rel_path.stem}.{class_name}.{pname}",
                            language=self.language_name(), source_file=str(rel_path),
                            type_ref=ptype.strip(),
                            visibility=(
                                VISIBILITY_PRIVATE if 'private' in line
                                else VISIBILITY_PROTECTED if 'protected' in line
                                else VISIBILITY_PUBLIC
                            ),
                            decorators=[deco for deco in []],
                        )
                        graph.add_node(pnode2)
                        graph.add_edge(class_id, pid2, "contains", f"field:{pname}")

    def detect(self, path: Path) -> bool:
        return self.can_parse(path)


class JavaScriptAdapter(LanguageAdapter):
    """USIR adapter for JavaScript (.js, .jsx, .mjs, .cjs).
    Reuses the TypeScript adapter logic (JS is a subset of TS syntax).
    """

    def language_name(self) -> str:
        return "javascript"

    def file_extensions(self) -> set[str]:
        return {'.js', '.jsx', '.mjs', '.cjs'}

    def parse_file(self, path: Path, source_root: Path | None = None) -> USIRGraph:
        return TypeScriptAdapter().parse_file(path, source_root)
