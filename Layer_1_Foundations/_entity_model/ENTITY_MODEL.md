# PROJECT VENUS — CANONICAL ENTITY MODEL

**Version**: 1.0  
**Inherits**: `_ontology/ontology.types.json`

The canonical entity model defines the required structure of every ontology type. Each entity inherits from its parent and adds domain-specific fields.

---

## Inheritance Principle

```
Entity
└── Artifact
    └── Template
        └── Certificate
            └── SecurityCertificate
                └── SLSAComplianceCertificate
```

Each level adds fields. No level removes fields. Every concrete type validates against its full ancestor chain.

---

## Base Entity Fields

All entities inherit:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | URI | Yes | Unique identifier |
| `type` | String | Yes | Ontology type name |
| `name` | String | Yes | Human-readable name |
| `description` | String | No | Semantic description |
| `metadata.created` | DateTime | Yes | Creation timestamp |
| `metadata.version` | String | Yes | Venus version |
| `metadata.layer` | Integer | Yes | Architectural layer |
| `tags` | String[] | No | Classification tags |
| `provenance.author` | String | Yes | Author identity |
| `provenance.signature` | String | No | Cryptographic signature |

---

## Type-Specific Fields

### OperatingSystem

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | String | Yes | e.g. "0.4" |
| `layer` | Integer | Yes | 1-5 |
| `inherits` | URI[] | No | Predecessor versions |
| `capabilities` | String[] | Yes | Capability list |
| `constraints` | String[] | No | Constraint list |
| `components` | {type: String, count: Integer}[] | Yes | Parts, engines, templates |
| `certification_gates` | URI[] | No | Gates to pass |

### Engine

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs` | Parameter[] | Yes | Required inputs |
| `outputs` | Parameter[] | Yes | Produced outputs |
| `validation_rules` | Rule[] | No | Validation logic |
| `produced_templates` | URI[] | No | Templates generated |
| `dependencies` | URI[] | No | Engine dependencies |
| `rollback_procedure` | String | No | How to undo |
| `metrics` | Metric[] | No | Performance metrics |

### Template

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inherits_schema` | URI | Yes | Canonical schema reference |
| `sections` | Section[] | Yes | Document sections |
| `generators` | String[] | Yes | Output formats (markdown, json, html) |
| `placeholders` | Parameter[] | No | Fillable parameters |
| `validation_rules` | Rule[] | No | Template validation |

### Certificate

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_tier` | String | Yes | tier_1/2/3 |
| `urqs_score` | Float | Yes | 0.0-1.0 |
| `gates_passed` | Gate[] | Yes | Validation gates |
| `validity_period` | Duration | Yes | How long valid |
| `signed_by` | String | Yes | Authorizing entity |

### Memory

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `memory_type` | String | Yes | semantic/procedural/decision/etc |
| `content_type` | String | Yes | text/graph/vector |
| `retention` | String | Yes | ephemeral/session/long_term |
| `index` | String[] | No | Index keys |
| `ttl` | Duration | No | Time to live |

### Agent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_type` | String | Yes | planner/executor/validator/etc |
| `capabilities` | String[] | Yes | What agent can do |
| `constraints` | String[] | No | Agent limitations |
| `prompts` | URI[] | No | Prompt definitions |
| `tools` | URI[] | No | Available tools |
| `memory_refs` | URI[] | No | Memory system refs |

### Policy

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_type` | String | Yes | security/governance/quality/compliance |
| `rules` | Rule[] | Yes | Executable rules |
| `severity` | String | Yes | critical/high/medium/low |
| `enforcement` | String | Yes | block/warn/log |
| `applies_to` | String[] | Yes | Target entity types |
