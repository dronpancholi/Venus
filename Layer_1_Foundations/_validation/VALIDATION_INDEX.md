# PROJECT VENUS — LAYER 1: VALIDATION INFRASTRUCTURE

**Purpose**: Automated validation of repository structure, schema conformance, cross-reference integrity, and naming conventions.

---

## Validation Scripts

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `generate_catalog.py` | Scans repo, generates catalog.json + dependency graph | On change |
| `validate_schemas.py` | Validates all JSON against canonical schemas | On change |
| `check_naming.py` | Verifies naming conventions across all files | CI gate |
| `check_references.py` | Checks all cross-references resolve correctly | CI gate |
| `check_templates.py` | Checks templates have no placeholder patterns | CI gate |

---

## Validation Gates

| Gate | Rule | Failure Action |
|------|------|---------------|
| G1 | Every file must have an entry in catalog.json | Block commit |
| G2 | Every file must match naming convention | Block commit |
| G3 | Every cross-reference must resolve | Block commit |
| G4 | Every template must pass placeholder scan | Block merge |
| G5 | Every schema reference must resolve to `_schemas/` | Block merge |
| G6 | Every dependency graph cycle is reported | Warning |

---

## Current Status

- [ ] `generate_catalog.py` — Not yet implemented
- [ ] `validate_schemas.py` — Not yet implemented
- [ ] `check_naming.py` — Not yet implemented
- [ ] `check_references.py` — Not yet implemented
- [ ] `check_templates.py` — Not yet implemented
