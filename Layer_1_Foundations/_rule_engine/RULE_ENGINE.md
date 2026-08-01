# PROJECT VENUS — RULE ENGINE

**Version**: 1.0  
**Purpose**: Universal policy engine. Every rule is executable. Every artifact is validated.

---

## 1. Architecture

```
                     ┌──────────────────────────┐
                     │   Policy Definition (DSL) │
                     └──────────┬───────────────┘
                                │
                     ┌──────────▼───────────────┐
                     │   Rule Compiler            │
                     │   (DSL → Rule AST)        │
                     └──────────┬───────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
     ┌────────▼────────┐ ┌─────▼──────┐  ┌────────▼────────┐
     │ Static Rules     │ │ Dynamic    │  │ Derived Rules   │
     │ (policy.json)    │ │ Rules      │  │ (inferred)      │
     └────────┬────────┘ │ (DSL)      │  └────────┬────────┘
              │           └─────┬──────┘           │
              └─────────────────┼──────────────────┘
                                │
                     ┌──────────▼───────────────┐
                     │   Rule Engine              │
                     │                            │
                     │  evaluate(entity) → [{     │
                     │    rule: string,           │
                     │    passed: bool,           │
                     │    severity: string,       │
                     │    message: string         │
                     │  }]                        │
                     └──────────┬───────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼───────┐     ┌─────────▼────────┐
            │ Validation     │     │ Certification     │
            │ Pipeline       │     │ Gates             │
            └───────────────┘     └──────────────────┘
```

---

## 2. Rule Types

| Rule Type | Source | Evaluation | Example |
|-----------|--------|------------|---------|
| Schema Rule | JSON Schema | Static | `required: ["name", "type"]` |
| Structural Rule | `policy_rules.json` | Static | `Every engine must have inputs` |
| DSL Validation Rule | Engine DSL `validation = []` | Static | `coverage >= 0.9` |
| Policy Rule | Policy DSL | Static | `no_plaintext_secrets` |
| Derived Rule | Knowledge Graph | Dynamic | `All dependencies must exist` |
| Metric Rule | Telemetry | Dynamic | `latency_p99 < 200ms` |

---

## 3. Core Structural Rules

These rules define the fundamental structure of every Venus artifact:

| Rule ID | Rule | Target Types | Severity |
|---------|------|-------------|----------|
| `R001` | Must have valid ontology type | All | Critical |
| `R002` | Must have unique id | All | Critical |
| `R003` | Must have name | All | Critical |
| `R004` | Must have description | All | High |
| `R005` | Must declare dependencies | All | High |
| `R010` | Engine must define inputs | Engine | Critical |
| `R011` | Engine must define outputs | Engine | Critical |
| `R012` | Engine must define validation rules | Engine | High |
| `R020` | Template must reference a schema | Template | Critical |
| `R021` | Template must define generators | Template | High |
| `R022` | Template must define sections | Template | High |
| `R030` | Policy must define rules | Policy | Critical |
| `R031` | Policy must define severity | Policy | Critical |
| `R040` | Certificate must define target tier | Certificate | Critical |
| `R041` | Certificate must define urqs_score | Certificate | Critical |
| `R050` | Memory must define retention policy | Memory | High |
| `R060` | Agent must define capabilities | Agent | Critical |
| `R070` | OS must define version | OperatingSystem | Critical |
| `R071` | OS must define capabilities | OperatingSystem | Critical |
| `R080` | All cross-references must resolve | Any | High |
| `R081` | No circular dependencies | Any | Critical |
| `R100` | No placeholder patterns in templates | Template | Medium |
| `R101` | Naming convention compliance | All | Medium |
