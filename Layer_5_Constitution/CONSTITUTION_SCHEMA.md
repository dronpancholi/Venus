# PROJECT VENUS — CONSTITUTION: SCHEMA REGISTRY SPECIFICATION

**Version**: 1.0  
**Inherits**: UVCOS.md (Layer 5 Constitution)  
**Location**: `Layer_1_Foundations/_schemas/`

---

## 1. Schema Registry

The canonical schema registry lives at `Layer_1_Foundations/_schemas/` and contains all shared type definitions.

### Registry Structure

```
_schemas/
├── SCHEMA_REGISTRY.md         Human-readable index
├── BASE_ENTITY_SCHEMA.json    Base entity (all schemas inherit)
├── DECISION_RECORD_SCHEMA.json
├── ADR_SCHEMA.json
├── RISK_REGISTER_SCHEMA.json
├── CERTIFICATE_SCHEMA.json
├── SCORING_SCHEMA.json
└── (future schemas)
```

### URI Convention

All schemas are addressed by the URI scheme `venus://schemas/<domain>/<name>/v<version>`.

Examples:
- `venus://schemas/base/entity/v1`
- `venus://schemas/decision/record/v1`
- `venus://schemas/adr/v1`

---

## 2. Schema Requirements

Every canonical schema MUST:

1. Be valid JSON Schema Draft 07.
2. Contain an `$id` property with a resolvable venus URI.
3. Contain a `title` and `description`.
4. Inherit from `BASE_ENTITY_SCHEMA` via `allOf` unless it IS the base schema.
5. Define `required` fields explicitly.
6. Include `enum` constraints where values are finite.
7. Reference other schemas via `$ref` rather than duplicating definitions.

---

## 3. Schema Consumption Rules

1. **No inline equivalents**: Every OS must reference canonical schemas rather than defining equivalent structures inline.
2. **Extension**: OS-specific variants extend canonical schemas using `allOf` + additional properties, never by modifying the canonical version.
3. **Validation**: Every artifact must validate against its declared schema before certification.
4. **Discovery**: The `SCHEMA_REGISTRY.md` index is the authoritative list of all schemas.

---

## 4. Schema Lifecycle

```
[Draft] → [Review] → [Published] → [Deprecated] → [Removed]
```

| Phase | Criteria | Action |
|-------|----------|--------|
| Draft | Proposed schema | Stored with -draft suffix |
| Review | Impact analysis complete | Schema frozen for changes |
| Published | Council approved | Active for consumption |
| Deprecated | Successor exists | Warning on validation, still valid |
| Removed | Migration window expired | Validation fails |
