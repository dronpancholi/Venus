"""
GENESIS-I — VENUS CORE PLATFORM

The executable heart of Project Venus.
Every future OS, Domain Pack, Runtime, Agent, Compiler, Studio,
Marketplace, and Project executes on this platform.

Core modules:
  core          — Universal Object Model, UIR, Type System, Metadata
  compiler      — Multi-source parser, LLVM-style passes, code generation
  plugin        — Plugin architecture with lifecycle management
  capability    — Capability registry with interfaces and contracts
  validation    — Universal validation engine
  graph         — Knowledge graph engine (Neo4j compatible)
  indexer       — Repository scanner and indexer
  runtime       — DAG-based execution engine
  api           — REST + GraphQL API router
  cli           — Venus CLI and Package Manager
  studio        — Studio backend APIs
  diagnostics   — Self-diagnostics engine
  integration   — Project 31A integration layer
"""

__version__ = "1.0.0"
__name__ = "genesis"
