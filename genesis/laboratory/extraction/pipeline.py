"""
Knowledge Extraction Pipeline (Program C) — automatically extract engineering knowledge.

Extractors:
  - Architectural patterns & anti-patterns
  - Protocols & APIs
  - Dependency structures
  - Database schemas
  - Security policies
  - CI/CD pipelines
  - State machines
  - Build systems
  - Release workflows
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.laboratory.genome.model import SoftwareGenome


# ── Data Model ──


@dataclass
class ExtractedKnowledge:
    """A single piece of extracted engineering knowledge."""
    id: str = ""
    kind: str = ""  # pattern, protocol, dependency, schema, security, ci_cd, state_machine, build
    name: str = ""
    source_file: str = ""
    source_repo: str = ""
    confidence: float = 0.0
    evidence: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    related: list[str] = field(default_factory=list)


@dataclass
class ArchitecturePattern:
    """An architectural or anti-pattern."""
    name: str = ""
    pattern_type: str = ""  # pattern, antipattern
    description: str = ""
    indicators: list[str] = field(default_factory=list)
    prevalence: float = 0.0


@dataclass
class KnowledgeExtractionResult:
    """Result of running extraction on a repository."""
    repo_id: str = ""
    knowledge_pieces: list[ExtractedKnowledge] = field(default_factory=list)
    patterns: list[ArchitecturePattern] = field(default_factory=list)
    protocols: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    database_schemas: list[dict[str, Any]] = field(default_factory=list)
    security_policies: list[dict[str, Any]] = field(default_factory=list)
    ci_cd_pipelines: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (len(self.knowledge_pieces) + len(self.patterns) +
                len(self.protocols) + len(self.dependencies) +
                len(self.database_schemas) + len(self.security_policies) +
                len(self.ci_cd_pipelines))


# ── Extraction Pipeline ──


class ExtractionPipeline:
    """Orchestrate knowledge extraction across all extractors."""

    def __init__(self):
        self.extractors: list[BaseExtractor] = [
            PatternExtractor(),
            ProtocolExtractor(),
            DependencyExtractor(),
            DatabaseExtractor(),
            SecurityExtractor(),
            CICDExtractor(),
            StateMachineExtractor(),
            BuildSystemExtractor(),
        ]

    def extract(self, repo_path: str | Path, repo_id: str = "",
                genome: SoftwareGenome | None = None) -> KnowledgeExtractionResult:
        """Run all extractors on a repository."""
        result = KnowledgeExtractionResult(repo_id=repo_id)
        root = Path(repo_path)

        for extractor in self.extractors:
            try:
                extractor.extract(root, result, genome)
            except Exception:
                continue

        return result

    def extract_from_source(self, source_text: str, source_file: str,
                             repo_id: str = "") -> list[ExtractedKnowledge]:
        """Run pattern extractors on a single source file."""
        pieces = []
        for extractor in self.extractors:
            try:
                for piece in extractor.extract_file(source_text, source_file, repo_id):
                    pieces.append(piece)
            except Exception:
                continue
        return pieces


class BaseExtractor:
    """Base class for knowledge extractors."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        """Extract knowledge from the repository."""
        raise NotImplementedError

    def extract_file(self, source: str, file_path: str,
                     repo_id: str) -> list[ExtractedKnowledge]:
        """Extract from a single file. Override in subclasses."""
        return []


# ── Pattern Extractor ──


PATTERN_SIGNATURES: list[tuple[str, str, str, list[str]]] = [
    ("abstract_factory", "pattern", "AbstractFactory/FactoryMethod pattern",
     ["def create_", "class .*Factory", "Factory", "AbstractFactory"]),
    ("singleton", "pattern", "Singleton pattern",
     ["__new__", "_instance", "get_instance", "getInstance"]),
    ("observer", "pattern", "Observer/PubSub pattern",
     ["observers", "listeners", "subscribers", "emit", "publish", "notify", "on_event"]),
    ("strategy", "pattern", "Strategy pattern",
     ["Strategy", "def execute", "def run_strategy"]),
    ("repository", "pattern", "Repository pattern",
     ["class .*Repository", "def save", "def find_by", "def delete"]),
    ("dependency_injection", "pattern", "Dependency Injection",
     ["di_container", "inject", "DIContainer", "dependency", "provide"]),
    ("event_sourcing", "pattern", "Event Sourcing",
     ["event_store", "EventStore", "append_event", "get_events", "event_sourcing"]),
    ("cqrs", "pattern", "CQRS pattern",
     ["Command", "Query", "CommandHandler", "QueryHandler", "separate"]),
    ("god_class", "antipattern", "God Class — class doing too much",
     ["class .*Manager", "class .*Util", "class .*Helper"]),
    ("spaghetti", "antipattern", "Spaghetti Code — excessive conditional nesting",
     ["if " * 5, "elif " * 5]),
    ("circular_dependency", "antipattern", "Circular Dependency",
     ["import "]),
]


class PatternExtractor(BaseExtractor):
    """Extract architectural patterns and anti-patterns."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        detected: dict[str, ArchitecturePattern] = {}

        for py_file in sorted(root.rglob("*.py")):
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            for name, ptype, desc, indicators in PATTERN_SIGNATURES:
                matches = sum(1 for ind in indicators if re.search(ind, text))
                if matches >= 2:
                    if name not in detected:
                        detected[name] = ArchitecturePattern(
                            name=name, pattern_type=ptype,
                            description=desc, indicators=indicators[:3],
                            prevalence=0.0,
                        )

        for name, arch_pattern in detected.items():
            total_files = len(list(root.rglob("*.py"))) or 1
            arch_pattern.prevalence = round(detected.get(name, text) if False else 1.0, 4)
            result.patterns.append(arch_pattern)

    def extract_file(self, source: str, file_path: str,
                     repo_id: str) -> list[ExtractedKnowledge]:
        pieces = []
        for name, ptype, desc, indicators in PATTERN_SIGNATURES:
            matches = sum(1 for ind in indicators if re.search(ind, source))
            if matches >= 2:
                pieces.append(ExtractedKnowledge(
                    id=f"{repo_id}::{ptype}_{name}_{file_path}",
                    kind=ptype, name=name,
                    source_file=file_path, source_repo=repo_id,
                    confidence=min(0.3 + matches * 0.15, 0.95),
                    evidence=f"Matched {matches} indicators: {indicators[:2]}",
                    properties={"type": ptype, "description": desc},
                ))
        return pieces


# ── Protocol Extractor ──


class ProtocolExtractor(BaseExtractor):
    """Extract protocol/API definitions."""

    PROTOCOL_PATTERNS = [
        (r"class\s+(\w+)\s*:\s*Protocol", "python_protocol"),
        (r"class\s+(\w+).*ABC\b", "abstract_base_class"),
        (r"@abstractmethod", "abstract_method"),
        (r"def\s+(get|post|put|delete|patch)_", "http_endpoint"),
        (r"@(app|router)\.(get|post|put|delete|patch)\([\"'](/[\w/{}]+)[\"']", "route_decorator"),
        (r"interface\s+(\w+)", "typescript_interface"),
        (r"type\s+(\w+)\s*=\s*Protocol\[", "python_protocol_type"),
    ]

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        for py_file in sorted(root.rglob("*")):
            if py_file.suffix not in (".py", ".ts", ".js"):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = str(py_file.relative_to(root)) if root in py_file.parents else py_file.name
            for pattern, kind in self.PROTOCOL_PATTERNS:
                for m in re.finditer(pattern, text):
                    name = m.group(1) if m.groups() else kind
                    result.protocols.append({
                        "name": name,
                        "kind": kind,
                        "file": rel,
                        "line": text[:m.start()].count("\n") + 1,
                    })
                    break

    def extract_file(self, source: str, file_path: str,
                     repo_id: str) -> list[ExtractedKnowledge]:
        pieces = []
        for pattern, kind in self.PROTOCOL_PATTERNS:
            for m in re.finditer(pattern, source):
                name = m.group(1) if m.groups() else kind
                pieces.append(ExtractedKnowledge(
                    id=f"{repo_id}::protocol_{name}",
                    kind="protocol", name=name,
                    source_file=file_path, source_repo=repo_id,
                    confidence=0.7, evidence=f"Matched {kind}",
                    properties={"protocol_kind": kind},
                ))
        return pieces


# ── Dependency Extractor ──


class DependencyExtractor(BaseExtractor):
    """Extract dependency structures from import graphs."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        dep_map: dict[str, set[str]] = defaultdict(set)

        for py_file in sorted(root.rglob("*.py")):
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            rel = str(py_file.relative_to(root)) if root in py_file.parents else py_file.name

            for m in re.finditer(r"^from\s+([\w.]+)\s+import|^import\s+([\w.]+)", text, re.MULTILINE):
                target = m.group(1) or m.group(2)
                if target:
                    dep_map[rel].add(target.split(".")[0])

        for source, targets in dep_map.items():
            for t in sorted(targets):
                result.dependencies.append({
                    "source": source,
                    "target": t + ".py",
                    "kind": "import",
                })


# ── Database Schema Extractor ──


DB_MODEL_PATTERNS = [
    (r"class\s+(\w+)\(.*Model.*\)", "orm_model"),
    (r"class\s+(\w+)\(.*Base.*\)", "sqlalchemy_model"),
    (r"__tablename__\s*=\s*[\"'](\w+)[\"']", "table_name"),
    (r"Column\s*\(\s*[\"']?(\w+)[\"']?", "column"),
    (r"db\.(String|Integer|Float|Boolean|DateTime|Text|JSON)\b", "column_type"),
    (r"relationship\s*\(\s*[\"'](\w+)[\"']", "relationship"),
    (r"ForeignKey\s*\(\s*[\"'](\w+)[\"']", "foreign_key"),
    (r"@Table\s*\(\s*[\"'](\w+)[\"']", "typeorm_entity"),
    (r"@Entity\s*\(\s*[\"'](\w+)[\"']", "typeorm_entity"),
    (r"@Column\b", "typeorm_column"),
]


class DatabaseExtractor(BaseExtractor):
    """Extract database schema definitions."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        for py_file in sorted(root.rglob("*")):
            if py_file.suffix not in (".py", ".ts"):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = str(py_file.relative_to(root)) if root in py_file.parents else py_file.name
            schemas = []
            current_model = ""

            for line in text.split("\n"):
                for pattern, kind in DB_MODEL_PATTERNS:
                    m = re.search(pattern, line)
                    if m:
                        name = m.group(1) if m.groups() else kind
                        if kind in ("orm_model", "sqlalchemy_model", "typeorm_entity"):
                            current_model = name
                            schemas.append({"model": name, "table": "", "columns": [], "relations": []})
                        elif kind == "table_name" and schemas:
                            schemas[-1]["table"] = name
                        elif kind in ("column", "column_type") and schemas:
                            schemas[-1]["columns"].append(name)
                        elif kind in ("relationship", "foreign_key") and schemas:
                            schemas[-1]["relations"].append({"type": kind, "target": name})

            for s in schemas:
                if s["columns"]:
                    s["file"] = rel
                    result.database_schemas.append(s)


# ── Security Policy Extractor ──


SECURITY_PATTERNS = [
    (r"(?:auth|authenticate|authorize|login|logout)", "authentication"),
    (r"(?:password|hash|bcrypt|argon)", "password_hashing"),
    (r"(?:jwt|JWT|JsonWebToken)", "jwt"),
    (r"(?:token|refresh_token|access_token)", "token_management"),
    (r"(?:permission|role|scope|acl)", "authorization"),
    (r"(?:csrf|CORS|cross_origin)", "web_security"),
    (r"(?:rate_limit|throttle)", "rate_limiting"),
    (r"(?:encrypt|decrypt|cipher|AES|RSA)", "encryption"),
    (r"(?:validate|sanitize|escape)", "input_validation"),
    (r"(?:https|SSL|TLS|certificate)", "transport_security"),
    (r"(?:sqlalchemy\.event|listener|before_insert|before_update)", "database_security"),
    (r"(?:__salt__|secret|SECRET_KEY)", "secrets_management"),
]


class SecurityExtractor(BaseExtractor):
    """Extract security policies and mechanisms."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        found: dict[str, int] = defaultdict(int)

        for py_file in sorted(root.rglob("*")):
            if py_file.suffix not in (".py", ".ts", ".js", ".yaml", ".yml", ".json"):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            for pattern, category in SECURITY_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found[category] += len(matches)

        for category, count in sorted(found.items(), key=lambda x: -x[1]):
            result.security_policies.append({
                "category": category,
                "evidence_count": count,
                "confidence": min(count / 10, 1.0),
            })


# ── CI/CD Extractor ──


CICD_FILE_PATTERNS = {
    ".github/workflows/": "github_actions",
    ".gitlab-ci.yml": "gitlab_ci",
    "Jenkinsfile": "jenkins",
    "circle.yml": "circle_ci",
    ".circleci/": "circle_ci",
    "azure-pipelines.yml": "azure_pipelines",
    "Dockerfile": "docker",
    "docker-compose": "docker_compose",
    "Makefile": "make",
    "Taskfile": "taskfile",
    "justfile": "just",
}


class CICDExtractor(BaseExtractor):
    """Extract CI/CD pipeline configurations."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        detected: dict[str, list[str]] = defaultdict(list)

        for f in sorted(root.rglob("*")):
            if not f.is_file():
                continue
            rel = str(f.relative_to(root)) if root in f.parents else f.name
            for pattern, ci_type in CICD_FILE_PATTERNS.items():
                if pattern in rel:
                    detected[ci_type].append(rel)

        for ci_type, files in sorted(detected.items()):
            result.ci_cd_pipelines.append({
                "type": ci_type,
                "files": files,
                "file_count": len(files),
            })


# ── State Machine Extractor ──


STATEMACHINE_PATTERNS = [
    (r"(?:state|status|phase|stage)\s*(?:=|:)", "enumeration_state"),
    (r"class\s+\w+State", "state_class"),
    (r"class\s+\w+Machine", "state_machine_class"),
    (r"def\s+(?:transition|next_state|change_state|advance)", "state_transition"),
    (r"(?:from_state|to_state|current_state)", "state_tracking"),
    (r"(?:transitions|states|initial_state)", "state_machine_lib"),
    (r"transitions\.Machine", "transitions_library"),
]


class StateMachineExtractor(BaseExtractor):
    """Extract state machines and state management."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        for py_file in sorted(root.rglob("*.py")):
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = str(py_file.relative_to(root)) if root in py_file.parents else py_file.name
            for pattern, kind in STATEMACHINE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    result.knowledge_pieces.append(ExtractedKnowledge(
                        id=f"{result.repo_id}::state_machine::{kind}",
                        kind="state_machine", name=kind,
                        source_file=rel, source_repo=result.repo_id,
                        confidence=0.6, evidence=f"Matched: {pattern}",
                    ))


# ── Build System Extractor ──


BUILD_FILE_PATTERNS = {
    "setup.py": "python_setuptools",
    "setup.cfg": "python_setuptools",
    "pyproject.toml": "python_pyproject",
    "Pipfile": "python_pipenv",
    "poetry.lock": "python_poetry",
    "requirements.txt": "python_pip",
    "Cargo.toml": "rust_cargo",
    "package.json": "node_npm",
    "yarn.lock": "node_yarn",
    "pom.xml": "java_maven",
    "build.gradle": "java_gradle",
    "go.mod": "go_modules",
    "CMakeLists.txt": "cmake",
    "Makefile": "make",
    "BUILD": "bazel",
    "WORKSPACE": "bazel",
    "Cargo.lock": "rust_cargo",
    "Gemfile": "ruby_bundler",
    "composer.json": "php_composer",
}


class BuildSystemExtractor(BaseExtractor):
    """Extract build system configurations."""

    def extract(self, root: Path, result: KnowledgeExtractionResult,
                genome: SoftwareGenome | None = None):
        build_files: dict[str, list[str]] = defaultdict(list)

        for f in sorted(root.rglob("*")):
            if not f.is_file():
                continue
            name = f.name
            rel = str(f.relative_to(root)) if root in f.parents else f.name
            for pattern, bs_type in BUILD_FILE_PATTERNS.items():
                if name == pattern or f.name == pattern:
                    build_files[bs_type].append(rel)

        for bs_type, files in sorted(build_files.items()):
            result.knowledge_pieces.append(ExtractedKnowledge(
                id=f"{result.repo_id}::build_{bs_type}",
                kind="build_system", name=bs_type,
                source_repo=result.repo_id,
                confidence=0.9,
                evidence=f"Found {len(files)} files: {files[:3]}",
                properties={"files": files, "type": bs_type},
            ))
