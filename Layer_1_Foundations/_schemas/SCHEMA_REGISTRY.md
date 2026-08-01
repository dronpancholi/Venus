# PROJECT VENUS — LAYER 1: CANONICAL SCHEMA REGISTRY

**Purpose**: Central registry of all canonical schemas. Every OS layer inherits from these definitions rather than defining inline equivalents.

**Version**: 1.0  
**Location**: `Layer_1_Foundations/_schemas/`  
**Validation Engine**: JSON Schema Draft 07

---

## Schema Index

| Schema ID | File | Purpose | Consumed By |
|-----------|------|---------|-------------|
| `venus://schemas/base/entity/v1` | `BASE_ENTITY_SCHEMA.json` | Base entity with venus_id, metadata, provenance | All schemas inherit via allOf |
| `venus://schemas/decision/record/v1` | `DECISION_RECORD_SCHEMA.json` | Structured decision record | V0.4 UDIOS, V0.5 USTAIE |
| `venus://schemas/adr/v1` | `ADR_SCHEMA.json` | Architecture Decision Record | V0.4 (Module 12), V0.5, V0.9 USEDPOS |
| `venus://schemas/risk/register/v1` | `RISK_REGISTER_SCHEMA.json` | Risk register entry | V0.2, V0.3, V0.4, V0.5, V0.6, V0.10 |
| `venus://schemas/certificate/v1` | `CERTIFICATE_SCHEMA.json` | Certification and attestation | V0.5-V0.11 all certification templates |
| `venus://schemas/scoring/v1` | `SCORING_SCHEMA.json` | URQS, confidence, quality scores | Constitution UVCOS, all OS scorecards |

---

## Schema Inheritance Hierarchy

```
BASE_ENTITY_SCHEMA
├── DECISION_RECORD_SCHEMA
│   └── ADR_SCHEMA
├── RISK_REGISTER_SCHEMA
├── CERTIFICATE_SCHEMA
└── SCORING_SCHEMA
```

---

## Usage Rules

1. **No inline schema duplication**: All OS layers must reference canonical schemas via `$ref` rather than defining equivalent structures.
2. **Extension via composition**: OS-specific variants extend canonical schemas using `allOf` + additional properties.
3. **Validation**: All artifacts must pass schema validation before certification.
4. **Versioning**: Schema breaking changes require constitution amendment (see Layer 5 governance).

---

## Schema Evolution Process

1. Proposal: Draft new schema version in `_schemas/` with incremented URI.
2. Review: Cross-layer impact analysis across all consuming OS versions.
3. Migration: Update consuming files to reference new schema URI.
4. Deprecation: Old schema URI remains valid for 2 OS versions before removal.
