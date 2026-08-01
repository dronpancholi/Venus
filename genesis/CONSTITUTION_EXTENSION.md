# PLATFORM CONSTITUTION EXTENSIONS

**Extensions to UVCOS for Genesis-I platform governance.**

---

## Article I: Compilation Integrity

All artifacts must be produced through the compiler pipeline.
Manual edits to generated artifacts require a `source_override` metadata flag.

**Rule**: `ART-001 — Every artifact must declare its source_path and generator_version.`

---

## Article II: Plugin Governance

Plugins must declare all capabilities, hooks, and dependencies.
No plugin may access capabilities outside its declared permissions.

**Rule**: `PLG-001 — Plugin manifests are validated before loading.`
**Rule**: `PLG-002 — Capabilities not declared in manifest are denied.`

---

## Article III: Graph Integrity

Every graph node must have at least one edge.
Orphan nodes are flagged and auto-archived after 30 days.

**Rule**: `GRF-001 — Nodes with zero edges are reported by diagnostics.`
**Rule**: `GRF-002 — Circular dependencies are blocked at compilation.`

---

## Article IV: Certification

Artifacts pass through stages: `unvalidated → validated → certified`.
Only certified artifacts may be deployed to production.

**Rule**: `CRT-001 — Certification requires passing all applicable validators.`
**Rule**: `CRT-002 — Certification expires after version change.`

---

## Article V: Memory Governance

Memory entries are immutable after commit.
Corrections create new entries with `supersedes` pointers.

**Rule**: `MEM-001 — Memory entries cannot be deleted, only superseded.`
**Rule**: `MEM-002 — Semantic search uses cosine distance on embeddings.`
