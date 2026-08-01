"""
Specialized Research Agents — 12 domain-specific research scientists.

Each agent extends ResearchAgent with domain-specific investigation logic:
  - ArchitectureScientist: architectural patterns, coupling, cohesion
  - SecurityScientist: security vulnerabilities, threat models
  - LanguageScientist: language features, type systems, compilers
  - RuntimeScientist: performance, concurrency, resource usage
  - TestingScientist: test patterns, coverage, quality
  - EconomicsScientist: cost of change, ROI, technical debt
  - SystemsScientist: OS interfaces, IPC, system calls
  - CompilerScientist: compiler optimization, code generation
  - DatabaseScientist: database design, ORM, queries
  - NetworkingScientist: networking protocols, APIs, RPC
  - DistributedSystemsScientist: consensus, replication, distribution
  - FormalMethodsScientist: model checking, proofs, invariants
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from genesis.civilization.agents.base import ResearchAgent, ResearchFinding, ResearchQuestion
from genesis.utils.identity import generate_id


class ArchitectureScientist(ResearchAgent):
    """Researcher focused on software architecture, patterns, coupling."""

    def research_domain(self) -> str:
        return "software_architecture"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        twin = context.get("twin")
        repo_path = context.get("repo_path")

        if genome:
            # Analyze coupling
            coupling = genome.fitness.coupling if genome.fitness else 0.0
            maintainability = genome.fitness.maintainability if genome.fitness else 0.0
            chrom_count = genome.chromosome_count
            gene_count = genome.gene_count

            findings.append(ResearchFinding(
                id=generate_id("arch", 12),
                title=f"Architectural coupling: {coupling:.4f}",
                description=f"Repository {genome.repository_name} has coupling {coupling:.4f} "
                           f"({chrom_count} chromosomes, {gene_count} genes)",
                evidence=f"Maintainability: {maintainability:.4f}, Species: {genome.species}",
                confidence=0.8, impact=coupling * 0.5,
                tags=["architecture", "coupling", genome.species],
            ))

            # Species classification
            findings.append(ResearchFinding(
                id=generate_id("arch", 12),
                title=f"Species: {genome.species}",
                description=f"Classified as '{genome.species}' based on "
                           f"{chrom_count} chromosomes, {genome.total_dependencies} dependencies",
                evidence=f"Dominant traits: {dict(genome.dominant_traits[:5])}",
                confidence=0.7, impact=0.3,
                tags=["species", "taxonomy", genome.species],
            ))

            if gene_count > 0:
                # Gene type distribution
                type_counts: dict[str, int] = {}
                for g in genome.all_genes:
                    type_counts[g.gene_type.name.lower()] = type_counts.get(g.gene_type.name.lower(), 0) + 1

                findings.append(ResearchFinding(
                    id=generate_id("arch", 12),
                    title=f"Gene composition: {len(type_counts)} types",
                    description=f"Gene type distribution: {type_counts}",
                    evidence=f"Total genes: {gene_count}",
                    confidence=0.9, impact=0.2,
                    tags=["composition", "gene_types"],
                ))

        if twin:
            # Analyze dependencies
            all_edges = []
            if hasattr(twin, 'find_edges'):
                all_edges = twin.find_edges()
            if all_edges:
                hub_modules = self._find_hubs(all_edges)
                if hub_modules:
                    findings.append(ResearchFinding(
                        id=generate_id("arch", 12),
                        title=f"Hubs detected: {len(hub_modules)} modules",
                        description=f"Highly coupled modules: {hub_modules[:5]}",
                        evidence=f"Total edges: {len(all_edges)}",
                        confidence=0.6, impact=-0.3,
                        tags=["hub", "coupling", "bottleneck"],
                    ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the optimal coupling range for this architecture?",
                hypothesis="Coupling between 0.3 and 0.7 correlates with highest fitness",
                priority=0.8, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Which modules are architectural bottlenecks?",
                hypothesis="Modules with >5 incoming dependencies degrade maintainability",
                priority=0.7, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Is there evidence of architectural drift?",
                hypothesis="Growing module count without layer boundaries indicates drift",
                priority=0.6, status="open", created_at=time.time(),
            ),
        ]

    def _find_hubs(self, edges: list, threshold: int = 5) -> list[str]:
        targets: dict[str, int] = {}
        for e in edges:
            tgt = e[1] if len(e) > 1 else ""
            targets[tgt] = targets.get(tgt, 0) + 1
        return [m for m, c in sorted(targets.items(), key=lambda x: -x[1]) if c >= threshold][:10]


class SecurityScientist(ResearchAgent):
    """Researcher focused on software security."""

    def research_domain(self) -> str:
        return "software_security"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        extraction = context.get("extraction")

        if extraction and hasattr(extraction, 'security_policies'):
            for sp in extraction.security_policies:
                findings.append(ResearchFinding(
                    id=generate_id("sec", 12),
                    title=f"Security mechanism: {sp['category']}",
                    description=f"Detected {sp.get('evidence_count', 0)} instances of {sp['category']}",
                    evidence=f"Confidence: {sp.get('confidence', 0.5):.2f}",
                    confidence=sp.get('confidence', 0.5),
                    impact=0.4,
                    tags=["security", sp["category"]],
                ))

        repo_path = context.get("repo_path")
        if repo_path:
            path = Path(repo_path)
            secrets = self._scan_secrets(path)
            if secrets:
                findings.append(ResearchFinding(
                    id=generate_id("sec", 12),
                    title=f"Potential secrets: {len(secrets)}",
                    description=f"Files with potential secrets: {secrets[:5]}",
                    evidence="Detected using pattern matching",
                    confidence=0.5, impact=-0.7,
                    tags=["security", "secrets", "risk"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the security posture of this repository?",
                hypothesis="Repos with auth, encryption, and validation have fewer vulnerabilities",
                priority=0.8, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Are there hardcoded secrets?",
                hypothesis="Secret keys in source code are the most common security risk",
                priority=0.9, status="open", created_at=time.time(),
            ),
        ]

    def _scan_secrets(self, path: Path) -> list[str]:
        secret_patterns = [
            r'SECRET_KEY\s*=\s*["\'][^"\']+["\']',
            r'API_KEY\s*=\s*["\'][^"\']+["\']',
            r'PASSWORD\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
        ]
        hits = []
        for f in path.rglob("*.py"):
            try:
                text = f.read_text(errors="replace")
                for pat in secret_patterns:
                    if re.search(pat, text):
                        hits.append(str(f.relative_to(path)))
                        break
            except Exception:
                continue
        return hits


class LanguageScientist(ResearchAgent):
    """Researcher focused on programming languages, type systems, compilers."""

    def research_domain(self) -> str:
        return "programming_languages"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        repo_path = context.get("repo_path")

        if genome:
            findings.append(ResearchFinding(
                id=generate_id("lang", 12),
                title=f"Primary language: {genome.language}",
                description=f"Repository uses {genome.language} with {genome.gene_count} genes",
                evidence=f"Chromosomes: {genome.chromosome_count}",
                confidence=0.95, impact=0.1,
                tags=["language", genome.language],
            ))

            protocol_genes = [g for g in genome.all_genes
                             if g.gene_type.name.lower() in ('protocol', 'interface_gene')]
            if protocol_genes:
                findings.append(ResearchFinding(
                    id=generate_id("lang", 12),
                    title=f"Protocol richness: {len(protocol_genes)}",
                    description=f"Uses {len(protocol_genes)} protocol/interface abstractions",
                    evidence=f"This indicates {'strong' if len(protocol_genes) > 3 else 'moderate'} "
                            f"abstraction usage",
                    confidence=0.7, impact=0.3,
                    tags=["language", "protocols", "abstraction"],
                ))

        if repo_path:
            lang_dist = self._language_distribution(Path(repo_path))
            if len(lang_dist) > 1:
                findings.append(ResearchFinding(
                    id=generate_id("lang", 12),
                    title=f"Multi-language: {len(lang_dist)} languages",
                    description=f"Languages detected: {lang_dist}",
                    evidence="Cross-language analysis may require multiple USIR adapters",
                    confidence=0.9, impact=0.4,
                    tags=["language", "multi-language", "polyglot"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the optimal abstraction level for this codebase?",
                hypothesis=f"Higher protocol/interface ratio correlates with maintainability",
                priority=0.6, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Are there language-specific anti-patterns?",
                hypothesis="Each language has characteristic anti-patterns detectable via USIR",
                priority=0.5, status="open", created_at=time.time(),
            ),
        ]

    def _language_distribution(self, path: Path) -> dict[str, int]:
        dist: dict[str, int] = {}
        ext_map = {'.py': 'python', '.ts': 'typescript', '.tsx': 'typescript',
                    '.js': 'javascript', '.jsx': 'javascript', '.rs': 'rust',
                    '.go': 'go', '.java': 'java'}
        for f in path.rglob("*"):
            if f.suffix in ext_map:
                lang = ext_map[f.suffix]
                dist[lang] = dist.get(lang, 0) + 1
        return dist


class RuntimeScientist(ResearchAgent):
    """Researcher focused on runtime, performance, concurrency."""

    def research_domain(self) -> str:
        return "runtime_performance"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        repo_path = context.get("repo_path")

        if genome:
            # Analyze complexity
            complexities = [g.complexity for g in genome.all_genes if g.complexity > 0]
            if complexities:
                avg_c = sum(complexities) / len(complexities)
                max_c = max(complexities)
                if max_c > 10:
                    findings.append(ResearchFinding(
                        id=generate_id("runtime", 12),
                        title=f"High complexity: max={max_c}, avg={avg_c:.1f}",
                        description=f"Maximum gene complexity {max_c} exceeds threshold of 10",
                        evidence=f"Average complexity: {avg_c:.2f}",
                        confidence=0.7, impact=-0.3 * (max_c / 20),
                        tags=["runtime", "complexity", "performance"],
                    ))

            # Async usage — detect from USIR patterns
            async_count = 0
            try:
                from genesis.usir.core import USIRNode, NodeKind
                for g in genome.all_genes:
                    if hasattr(g, 'metadata') and g.metadata:
                        raw = g.metadata
                        if isinstance(raw, dict) and raw.get('async_mode'):
                            async_count += 1
                        elif isinstance(raw, str) and 'async' in raw.lower():
                            async_count += 1
            except ImportError:
                pass
            if async_count > 0:
                findings.append(ResearchFinding(
                    id=generate_id("runtime", 12),
                    title=f"Async usage: {async_count} async functions",
                    description=f"Repository uses async patterns",
                    evidence="Async concurrency detected",
                    confidence=0.6, impact=0.2,
                    tags=["runtime", "async", "concurrency"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the performance profile of this repository?",
                hypothesis="High complexity genes correlate with runtime bottlenecks",
                priority=0.7, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Is concurrency handled correctly?",
                hypothesis="Async usage without proper error handling indicates risk",
                priority=0.5, status="open", created_at=time.time(),
            ),
        ]


class TestingScientist(ResearchAgent):
    """Researcher focused on testing patterns and quality."""

    def research_domain(self) -> str:
        return "software_testing"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        extraction = context.get("extraction")

        if genome and genome.gene_count > 0:
            test_genes = [g for g in genome.all_genes if g.gene_type.name.lower() == 'test']
            test_ratio = len(test_genes) / genome.gene_count if genome.gene_count > 0 else 0

            findings.append(ResearchFinding(
                id=generate_id("test", 12),
                title=f"Test coverage ratio: {test_ratio:.2%}",
                description=f"{len(test_genes)} test genes out of {genome.gene_count} total",
                evidence=f"Test density: {test_ratio:.4f}",
                confidence=0.8, impact=test_ratio * 0.5,
                tags=["testing", "coverage"],
            ))

            if test_ratio < 0.1:
                findings.append(ResearchFinding(
                    id=generate_id("test", 12),
                    title=f"Low test coverage: {test_ratio:.1%}",
                    description=f"Test coverage below 10% indicates testing debt",
                    evidence=f"Only {len(test_genes)} test genes detected",
                    confidence=0.9, impact=-0.5,
                    tags=["testing", "debt", "risk"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the optimal test ratio?",
                hypothesis="Repos with 15-30% test genes have highest long-term fitness",
                priority=0.8, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="What test patterns are most effective?",
                hypothesis="Repos using parameterized tests have fewer regressions",
                priority=0.6, status="open", created_at=time.time(),
            ),
        ]


class EconomicsScientist(ResearchAgent):
    """Researcher focused on engineering economics, cost, value."""

    def research_domain(self) -> str:
        return "engineering_economics"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")

        if genome:
            gene_count = genome.gene_count
            chrom_count = genome.chromosome_count
            fitness = genome.fitness.overall if genome.fitness else 0

            # Estimate technical debt
            complexity = genome.traits.get('avg_complexity', 0)
            debt_ratio = min(complexity / 10, 1.0) if complexity > 0 else 0

            findings.append(ResearchFinding(
                id=generate_id("econ", 12),
                title=f"Estimated technical debt: {debt_ratio:.1%}",
                description=f"Based on avg complexity {complexity:.2f}, "
                           f"{gene_count} genes, {chrom_count} modules",
                evidence=f"Fitness: {fitness:.4f}, Debt ratio: {debt_ratio:.4f}",
                confidence=0.6, impact=-debt_ratio * 0.5,
                tags=["economics", "debt", "cost"],
            ))

            # Cost of change estimation
            coupling = genome.traits.get('avg_dependencies', 0)
            change_cost = min(coupling / 5, 1.0) if coupling > 0 else 0

            findings.append(ResearchFinding(
                id=generate_id("econ", 12),
                title=f"Change cost index: {change_cost:.2f}",
                description=f"Estimated cost of architectural change "
                           f"(0=cheap, 1=prohibitively expensive)",
                evidence=f"Average dependencies: {coupling:.2f}",
                confidence=0.5, impact=-change_cost * 0.4,
                tags=["economics", "change_cost", "maintainability"],
            ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the economic value of refactoring?",
                hypothesis="Reducing complexity by 20% increases development velocity by 15%",
                priority=0.9, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="What is the optimal module size?",
                hypothesis="Modules with 200-500 lines minimize change cost",
                priority=0.7, status="open", created_at=time.time(),
            ),
        ]


class SystemsScientist(ResearchAgent):
    """Researcher focused on operating systems, IPC, system calls."""

    def research_domain(self) -> str:
        return "systems_software"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        repo_path = context.get("repo_path")

        if genome:
            # Detect system-level interfaces
            sys_genes = [g for g in genome.all_genes
                         if any(kw in (g.name or '').lower() for kw in
                                ('ioctl', 'syscall', 'mmap', 'signal', 'socket',
                                 'inotify', 'epoll', 'kqueue', 'fork', 'exec',
                                 'ptrace', 'capability', 'namespace'))]
            if sys_genes:
                findings.append(ResearchFinding(
                    id=generate_id("sys", 12),
                    title=f"System interface count: {len(sys_genes)}",
                    description=f"Uses {len(sys_genes)} system-level interfaces",
                    evidence=f"Interfaces: {[g.name for g in sys_genes[:5]]}",
                    confidence=0.8, impact=0.3,
                    tags=["systems", "os", "interfaces"],
                ))

            # Detect IPC patterns
            ipc_genes = [g for g in genome.all_genes
                         if any(kw in (g.name or '').lower() for kw in
                                ('pipe', 'shm', 'msg', 'semaphore', 'mutex',
                                 'lock', 'barrier', 'condition'))]
            if ipc_genes:
                findings.append(ResearchFinding(
                    id=generate_id("sys", 12),
                    title=f"IPC primitives: {len(ipc_genes)}",
                    description=f"Uses {len(ipc_genes)} inter-process communication primitives",
                    evidence=f"Primitives: {[g.name for g in ipc_genes[:5]]}",
                    confidence=0.7, impact=0.4,
                    tags=["systems", "ipc", "concurrency"],
                ))

        if repo_path:
            c_files = list(Path(repo_path).rglob("*.c")) + list(Path(repo_path).rglob("*.h"))
            if c_files:
                findings.append(ResearchFinding(
                    id=generate_id("sys", 12),
                    title=f"C system code: {len(c_files)} files",
                    description=f"Contains {len(c_files)} C files — likely low-level systems code",
                    evidence="C files indicate systems-level programming",
                    confidence=0.9, impact=0.5,
                    tags=["systems", "c", "low-level"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="Does this code use OS-specific interfaces?",
                hypothesis="Linux-specific syscalls reduce portability",
                priority=0.7, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Are IPC mechanisms thread-safe?",
                hypothesis="Improper mutex usage in signal handlers causes deadlocks",
                priority=0.6, status="open", created_at=time.time(),
            ),
        ]


class CompilerScientist(ResearchAgent):
    """Researcher focused on compiler design, optimization, code generation."""

    def research_domain(self) -> str:
        return "compiler_engineering"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        repo_path = context.get("repo_path")

        if genome:
            # Pattern: AST-like structures
            ast_genes = [g for g in genome.all_genes
                         if any(kw in (g.name or '').lower() for kw in
                                ('ast', 'parse', 'token', 'lexer', 'grammar',
                                 'syntax', 'semantic', 'symbol', 'typeck',
                                 'codegen', 'ir', 'optimize', 'pass'))]
            if ast_genes:
                findings.append(ResearchFinding(
                    id=generate_id("comp", 12),
                    title=f"Compiler constructs: {len(ast_genes)}",
                    description=f"Found {len(ast_genes)} compiler-like abstractions",
                    evidence=f"Constructs: {[g.name for g in ast_genes[:7]]}",
                    confidence=0.8, impact=0.5,
                    tags=["compiler", "language", "tooling"],
                ))

            # Detect visitor/pattern matching patterns
            visitor_genes = [g for g in genome.all_genes
                             if any(kw in (g.name or '').lower() for kw in
                                    ('visitor', 'match', 'pattern', 'transform'))]
            if visitor_genes:
                findings.append(ResearchFinding(
                    id=generate_id("comp", 12),
                    title=f"Visitor/Matching: {len(visitor_genes)}",
                    description=f"Uses {len(visitor_genes)} traversal or pattern matching patterns",
                    evidence=f"Modules: {[g.name for g in visitor_genes[:5]]}",
                    confidence=0.6, impact=0.2,
                    tags=["compiler", "visitor", "pattern-matching"],
                ))

        if repo_path:
            usir_path = Path(repo_path) / "genesis" / "usir"
            if usir_path.exists():
                findings.append(ResearchFinding(
                    id=generate_id("comp", 12),
                    title="USIR compiler framework present",
                    description="Repository contains Universal Semantic Intermediate Representation",
                    evidence="USIR is a multi-language compiler intermediate representation",
                    confidence=1.0, impact=0.7,
                    tags=["compiler", "usir", "intermediate-representation"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="Can USIR be extended to new languages?",
                hypothesis="A language-agnostic IR enables cross-language refactoring",
                priority=0.8, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="What optimizations does the compiler pipeline support?",
                hypothesis="Multi-pass optimization with data-flow analysis covers most patterns",
                priority=0.6, status="open", created_at=time.time(),
            ),
        ]


class DatabaseScientist(ResearchAgent):
    """Researcher focused on database design, queries, ORM."""

    def research_domain(self) -> str:
        return "database_engineering"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        extraction = context.get("extraction")

        if genome:
            db_genes = [g for g in genome.all_genes
                        if any(kw in (g.name or '').lower() for kw in
                               ('sql', 'query', 'model', 'schema', 'table',
                                'index', 'migration', 'orm', 'database',
                                'db_', 'repository', 'dao'))]
            if db_genes:
                findings.append(ResearchFinding(
                    id=generate_id("db", 12),
                    title=f"Database constructs: {len(db_genes)}",
                    description=f"Found {len(db_genes)} database-related abstractions",
                    evidence=f"Constructs: {[g.name for g in db_genes[:7]]}",
                    confidence=0.8, impact=0.4,
                    tags=["database", "data", "persistence"],
                ))

            schema_genes = [g for g in db_genes
                           if any(kw in (g.name or '').lower() for kw in
                                  ('migration', 'schema', 'model', 'table'))]
            if schema_genes:
                findings.append(ResearchFinding(
                    id=generate_id("db", 12),
                    title=f"Schema management: {len(schema_genes)} constructs",
                    description=f"Database schema is managed through {len(schema_genes)} constructs",
                    evidence="Schema management indicates structured data design",
                    confidence=0.7, impact=0.3,
                    tags=["database", "schema", "migration"],
                ))

        if extraction and hasattr(extraction, 'database_schemas'):
            for ds in extraction.database_schemas:
                findings.append(ResearchFinding(
                    id=generate_id("db", 12),
                    title=f"DB schema: {ds.get('type', 'unknown')}",
                    description=f"Detected schema with {ds.get('evidence_count', 0)} evidences",
                    evidence=f"Confidence: {ds.get('confidence', 0.5):.2f}",
                    confidence=ds.get('confidence', 0.5),
                    impact=0.3,
                    tags=["database", "schema", ds.get('type', 'unknown')],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="Is the data access layer well-separated?",
                hypothesis="Clean DAO/repository boundaries reduce migration cost",
                priority=0.7, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Are there N+1 query patterns?",
                hypothesis="ORM lazy loading without eager loading causes N+1 problems",
                priority=0.8, status="open", created_at=time.time(),
            ),
        ]


class NetworkingScientist(ResearchAgent):
    """Researcher focused on networking protocols, APIs, RPC."""

    def research_domain(self) -> str:
        return "network_protocols"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")

        if genome:
            net_genes = [g for g in genome.all_genes
                         if any(kw in (g.name or '').lower() for kw in
                                ('http', 'tcp', 'udp', 'rpc', 'grpc', 'rest',
                                 'api', 'route', 'handler', 'middleware',
                                 'endpoint', 'request', 'response', 'client',
                                 'server', 'socket', 'web', 'ws_'))]
            if net_genes:
                findings.append(ResearchFinding(
                    id=generate_id("net", 12),
                    title=f"Network interfaces: {len(net_genes)}",
                    description=f"Found {len(net_genes)} networking-related abstractions",
                    evidence=f"Interfaces: {[g.name for g in net_genes[:7]]}",
                    confidence=0.85, impact=0.5,
                    tags=["networking", "protocols", "api"],
                ))

                # Categorize protocols
                rest_count = sum(1 for g in net_genes if 'rest' in (g.name or '').lower())
                rpc_count = sum(1 for g in net_genes if 'rpc' in (g.name or '').lower() or 'grpc' in (g.name or '').lower())
                websocket_count = sum(1 for g in net_genes if 'ws_' in (g.name or '').lower() or 'websocket' in (g.name or '').lower())

                if rest_count > rpc_count:
                    findings.append(ResearchFinding(
                        id=generate_id("net", 12),
                        title=f"REST-dominant API style",
                        description=f"REST interfaces ({rest_count}) outnumber RPC ({rpc_count})",
                        evidence="REST-dominant architectures favor resource-oriented design",
                        confidence=0.7, impact=0.2,
                        tags=["networking", "rest", "api-style"],
                    ))

            # Dependency analysis for network libs
            all_deps = set()
            for g in genome.all_genes:
                all_deps.update(g.dependencies)
            net_deps = [d for d in all_deps
                       if any(lib in d.lower() for lib in
                              ('requests', 'aiohttp', 'flask', 'django',
                               'fastapi', 'grpc', 'httpx', 'urllib'))]
            if net_deps:
                findings.append(ResearchFinding(
                    id=generate_id("net", 12),
                    title=f"Network libraries: {len(net_deps)}",
                    description=f"Uses networking libraries: {net_deps}",
                    evidence="External dependencies indicate protocol ecosystem",
                    confidence=0.9, impact=0.3,
                    tags=["networking", "dependencies", "libraries"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="What is the API versioning strategy?",
                hypothesis="Semantic versioning with backward compatibility reduces breakage",
                priority=0.7, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="Are there timeout and retry policies?",
                hypothesis="Missing retry logic with exponential backoff causes cascading failures",
                priority=0.8, status="open", created_at=time.time(),
            ),
        ]


class DistributedSystemsScientist(ResearchAgent):
    """Researcher focused on consensus, replication, distributed algorithms."""

    def research_domain(self) -> str:
        return "distributed_systems"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")

        if genome:
            dist_genes = [g for g in genome.all_genes
                          if any(kw in (g.name or '').lower() for kw in
                                 ('raft', 'paxos', 'gossip', 'consensus',
                                  'replica', 'shard', 'partition', 'distributed',
                                  'cluster', 'leader', 'election', 'quorum',
                                  'vector_clocks', 'crdt', 'eventual',
                                  'dist_lock', 'rate_limit', 'circuit_breaker'))]
            if dist_genes:
                findings.append(ResearchFinding(
                    id=generate_id("dist", 12),
                    title=f"Distributed systems patterns: {len(dist_genes)}",
                    description=f"Found {len(dist_genes)} distributed computing constructs",
                    evidence=f"Patterns: {[g.name for g in dist_genes[:7]]}",
                    confidence=0.85, impact=0.6,
                    tags=["distributed", "consensus", "replication"],
                ))

            # Detect consensus protocols
            consensus_genes = [g for g in dist_genes
                              if any(kw in (g.name or '').lower() for kw in
                                     ('raft', 'paxos', 'consensus', 'quorum', 'leader'))]
            if consensus_genes:
                findings.append(ResearchFinding(
                    id=generate_id("dist", 12),
                    title=f"Consensus protocols: {len(consensus_genes)}",
                    description=f"Uses consensus: {[g.name for g in consensus_genes]}",
                    evidence="Consensus protocols are critical for distributed correctness",
                    confidence=0.9, impact=0.7,
                    tags=["distributed", "consensus", "correctness"],
                ))

            # CRDT detection
            crdt_genes = [g for g in genome.all_genes
                         if any(kw in (g.name or '').lower() for kw in
                                ('crdt', 'lww', 'pn_counter', 'orset'))]
            if crdt_genes:
                findings.append(ResearchFinding(
                    id=generate_id("dist", 12),
                    title=f"CRDT usage: {len(crdt_genes)}",
                    description=f"Conflict-free replicated data types detected",
                    evidence=f"Types: {[g.name for g in crdt_genes]}",
                    confidence=0.8, impact=0.5,
                    tags=["distributed", "crdt", "conflict-free"],
                ))

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="Does the system tolerate network partitions?",
                hypothesis="Systems without partition tolerance fail under network splits",
                priority=0.9, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="What consistency model is used?",
                hypothesis="Strong consistency with quorum reads limits availability",
                priority=0.8, status="open", created_at=time.time(),
            ),
        ]


class FormalMethodsScientist(ResearchAgent):
    """Researcher focused on formal verification, model checking, invariants."""

    def research_domain(self) -> str:
        return "formal_methods"

    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        findings = []
        genome = context.get("genome")
        twin = context.get("twin")

        if genome:
            # Check for formal specification patterns
            spec_genes = [g for g in genome.all_genes
                          if any(kw in (g.name or '').lower() for kw in
                                 ('invariant', 'assert', 'precondition',
                                  'postcondition', 'contract', 'specification',
                                  'theorem', 'lemma', 'proof', 'proposition',
                                  'property', 'sat', 'smt', 'z3', 'model_check',
                                  'tla', 'alloy', 'coq', 'agda', 'isabelle',
                                  'dafny', 'why3', 'verif'))]
            if spec_genes:
                findings.append(ResearchFinding(
                    id=generate_id("formal", 12),
                    title=f"Formal specifications: {len(spec_genes)}",
                    description=f"Found {len(spec_genes)} formal methods constructs",
                    evidence=f"Constructs: {[g.name for g in spec_genes[:7]]}",
                    confidence=0.9, impact=0.6,
                    tags=["formal", "verification", "specification"],
                ))

            # Detect assertion density
            assert_count = sum(1 for g in genome.all_genes
                              if 'assert' in (g.name or '').lower())
            if genome.gene_count > 0:
                assert_density = assert_count / genome.gene_count
                if assert_density < 0.02:
                    findings.append(ResearchFinding(
                        id=generate_id("formal", 12),
                        title=f"Low assertion density: {assert_density:.2%}",
                        description=f"Only {assert_count} assertions across {genome.gene_count} genes",
                        evidence="Low assertion density indicates weak runtime verification",
                        confidence=0.6, impact=-0.3,
                        tags=["formal", "assertions", "quality"],
                    ))

        if twin:
            # Check for architecture invariants
            if hasattr(twin, 'verify_invariant'):
                try:
                    result = twin.verify_invariant()
                    if result:
                        findings.append(ResearchFinding(
                            id=generate_id("formal", 12),
                            title=f"Architecture invariants: {len(result)}",
                            description=f"Architecture invariant verification produced {len(result)} results",
                            evidence=str(result)[:200],
                            confidence=0.7, impact=0.4,
                            tags=["formal", "invariants", "architecture"],
                        ))
                except Exception:
                    pass

        return findings

    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        return [
            ResearchQuestion(
                question="Can architecture invariants be verified automatically?",
                hypothesis="Layer constraints and import rules form a checkable invariant set",
                priority=0.9, status="open", created_at=time.time(),
            ),
            ResearchQuestion(
                question="What is the formal specification coverage?",
                hypothesis="Specification coverage below 10% means most behavior is unverified",
                priority=0.8, status="open", created_at=time.time(),
            ),
        ]
