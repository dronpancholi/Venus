# PROJECT VENUS — LAYER 1: METADATA REGISTRY

**Purpose**: Machine-readable index of every Venus artifact. Enables discovery, dependency tracking, validation, and knowledge graph construction.

---

## Registry Files

| File | Format | Purpose |
|------|--------|---------|
| `catalog.json` | JSON | Index of all files with venus_id, type, layer, version, schema_ref |
| `dependency_graph.json` | JSON | Cross-file dependency edges |
| `manifest_v0.2.json` .. `manifest_v0.11.json` | JSON | Per-OS version manifest declaring capabilities, constraints, and deltas |

---

## Entity Lifecycle

1. **Registration**: Every new file must add an entry to `catalog.json`.
2. **Validation**: Registration validates against `BASE_ENTITY_SCHEMA.json`.
3. **Linking**: Dependencies are declared in the `dependencies` array.
4. **Audit**: Provenance tracks creation, modification, and certification.
