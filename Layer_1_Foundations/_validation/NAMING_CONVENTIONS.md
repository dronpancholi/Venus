# PROJECT VENUS — NAMING CONVENTIONS

**Version**: 1.0  
**Enforcement**: `check_naming.py` validates these rules

---

## File Naming Rules

### OS Root Files
```
Pattern: V<MAJOR>.<MINOR>_<SYSTEM_NAME>.md
Example: V0.4_UDIOS.md
Rule:    System name in ALL CAPS, no hyphens
```

### Parts and Modules
```
Pattern: (PART|MODULE)_<NN>_<DESCRIPTIVE_NAME>.md
Example: PART_01_SYSTEMS_THINKING.md
Rule:    Two-digit sequence number, descriptive name in UPPER_SNAKE_CASE
```

### Engines
```
Pattern: ENGINE_<DESCRIPTIVE_NAME>.md
Example: ENGINE_THREAT_MODELING_ENGINE.md
Rule:    Descriptive name in UPPER_SNAKE_CASE, no sequence number
```

### Templates
```
Pattern: TEMPLATE_<NNN>_<DESCRIPTIVE_NAME>.md  (for numbered)
         <DESCRIPTIVE_NAME>.md                   (for unnumbered)
Example: TEMPLATE_001_ORG_CHART_METRIC_STANDARD.md
         RISK_DECISION_REGISTER.md
Rule:    Three-digit sequence for numbered templates
```

### Stages
```
Pattern: STAGE_<NN>_<DESCRIPTIVE_NAME>.md
Example: STAGE_1_PROBLEM_DISCOVERY.md
Rule:    Two-digit sequence number (no leading zero)
```

### Schemas
```
Pattern: <UPPER_SNAKE_NAME>_SCHEMA.json
Example: BASE_ENTITY_SCHEMA.json
```

### Scripts
```
Pattern: <snake_case_name>.py
Example: generate_catalog.py
```

---

## Directory Naming Rules

| Level | Pattern | Example |
|-------|---------|---------|
| Layer | `Layer_<N>_<Name>/` | `Layer_2_Core_OS/` |
| OS Version | `V<X>.<Y>_<CODE>/` | `V0.4_UDIOS/` |
| Subdirectory | `<snake_case_name>/` | `_schemas/`, `udios_modules/` |

---

## Prohibited Patterns

1. **No spaces** in filenames (use underscores)
2. **No hyphens** in filenames (use underscores)
3. **No special characters** except underscore and dot
4. **No mixed case** in snake_case names
5. **No TODO, FIXME, or [placeholder]** in template files
6. **No duplicate names** across different directories

## Common Typos to Avoid

| Wrong | Correct |
|-------|---------|
| `Docker` (as abbreviation) | `DOCKER` |
| `DEI` (wrong expansion) | `DEI` |
| `onboarding` | `ONBOARDING` |
| `offboarding` | `OFFBOARDING` |
