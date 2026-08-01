# PROJECT VENUS — VENUS DSL SPECIFICATION

**Version**: 1.0  
**Purpose**: Declarative language for defining Venus entities. The compiler reads DSL and generates all artifacts.

---

## 1. Philosophy

Instead of writing markdown documents manually, authors declare intent in Venus DSL:

```dsl
// Declare what exists
engine "ThreatModelingEngine" {
  description = "Automated threat modeling"
  
  inherits = ["BaseSecurityEngine"]
  
  inputs = [
    { name: "architecture_blueprint", type: "ArchitectureDocument" },
    { name: "trust_boundaries", type: "TrustBoundary[]" }
  ]
  
  outputs = [
    { name: "threat_model", type: "ThreatModel" },
    { name: "risk_register", type: "RiskRegister" }
  ]
  
  validation = [
    { rule: "all_components_covered", severity: "critical" },
    { rule: "trust_boundaries_defined", severity: "critical" },
    { rule: "mitigations_exist_for_critical", severity: "high" }
  ]
  
  produces = ["THREAT_MODEL_REPORT", "RISK_REGISTER_REPORT"]
  
  certifies = ["SECURITY_CERTIFICATE"]
}
```

The compiler generates:
- Markdown documentation
- JSON Schema validation
- Mermaid diagrams
- OpenAPI specs
- Prompt packs for AI agents
- Runtime configurations
- Validation scripts

---

## 2. Language Syntax

### 2.1 Block Types

```
operatingsystem <name> { ... }
part <name> { ... }
module <name> { ... }
engine <name> { ... }
template <name> { ... }
certificate <name> { ... }
stage <name> { ... }
workflow <name> { ... }
policy <name> { ... }
agent <name> { ... }
memory <name> { ... }
schema <name> { ... }
interface <name> { ... }
ontology <name> { ... }
```

### 2.2 Field Types

| Type | Syntax | Example |
|------|--------|---------|
| String | `"value"` | `name = "Engine"` |
| Integer | `123` | `layer = 2` |
| Float | `1.0` | `threshold = 0.85` |
| Boolean | `true` / `false` | `required = true` |
| URI | `"venus://..."` | `schema = "venus://schemas/base/v1"` |
| Array | `[a, b, c]` | `inputs = [a, b]` |
| Object | `{ k: v }` | `{ name: "x", type: "y" }` |
| Reference | `@TargetName` | `inherits = [@BaseEngine]` |

### 2.3 Built-in Attributes

| Attribute | Applies To | Description |
|-----------|-----------|-------------|
| `description` | All | Human-readable description |
| `inherits` | All | Parent references |
| `inputs` | Engine, Workflow | Required inputs |
| `outputs` | Engine, Workflow | Produced outputs |
| `validation` | Engine, Template | Validation rules |
| `produces` | Engine | Generated templates |
| `certifies` | Engine | Certificates produced |
| `dependencies` | All | Dependencies |
| `constraints` | All | Constraints |
| `capabilities` | Part, OS | Capability list |
| `metrics` | Engine | Performance metrics |
| `rollback` | Engine | Rollback procedure |
| `sections` | Template | Document sections |
| `generators` | Template | Output formats |
| `rules` | Policy | Policy rules |
| `severity` | Policy, Rule | Severity level |
| `enforcement` | Policy | Enforcement mode |
| `schema` | Template | Canonical schema ref |
| `memory_type` | Memory | Memory classification |
| `retention` | Memory | Retention policy |
| `agent_type` | Agent | Agent specialization |
| `tools` | Agent | Available tools |
| `prompts` | Agent | Prompt references |
| `tags` | All | Classification tags |

### 2.4 Validation Rules

```
validation = [
  { rule: "rule_name", severity: "critical|high|medium|low" },
  { rule: "another_rule", 
    expression: "input.coverage >= 0.9",
    message: "Coverage must be >= 90%"
  }
]
```

---

## 3. Example: Complete OS Definition

```dsl
operatingsystem "SecurityOS" {
  version = "0.10"
  layer = 2
  description = "Universal Security OS"
  inherits = ["USEDPOS"]
  
  capabilities = [
    "threat_modeling",
    "zero_trust_enforcement",
    "vulnerability_scanning",
    "compliance_auditing"
  ]
  
  constraints = [
    "all_communication_must_use_mtls",
    "no_plaintext_secrets"
  ]

  part "ThreatModeling" {
    description = "Threat modeling methodology"
    
    concepts = [
      { name: "STRIDE", type: "taxonomy" },
      { name: "AttackTree", type: "pattern" },
      { name: "TrustBoundary", type: "concept" }
    ]
  }

  engine "ThreatModelingEngine" {
    description = "Automated threat modeling"
    
    inputs = [
      { name: "architecture", type: "ArchitectureBlueprint" }
    ]
    
    outputs = [
      { name: "threat_model", type: "ThreatModelReport" }
    ]
    
    validation = [
      { rule: "trust_boundaries_identified", severity: "critical" }
    ]
    
    produces = ["THREAT_MODEL_REPORT"]
  }

  template "ThreatModelReport" {
    description = "Standard threat model output"
    schema = "venus://schemas/certificate/v1"
    
    sections = [
      { name: "Executive Summary", required: true },
      { name: "Component Inventory", required: true },
      { name: "Trust Boundaries", required: true },
      { name: "Threat Table", required: true },
      { name: "Mitigation Plan", required: true }
    ]
    
    generators = ["markdown", "pdf", "json"]
  }
}
```

---

## 4. Compilation Targets

| Target | Description | Extension |
|--------|-------------|-----------|
| `markdown` | Human-readable documentation | `.md` |
| `json_schema` | JSON Schema validation | `.json` |
| `mermaid` | Architecture diagrams | `.mmd` |
| `openapi` | REST API specifications | `.yaml` |
| `graphql` | GraphQL schemas | `.graphql` |
| `prompt` | AI agent prompt packs | `.md` |
| `agent_spec` | Agent runtime configuration | `.json` |
| `runtime_config` | Runtime deployment config | `.yaml` |
| `validation_script` | Validation scripts | `.py` |
| `compliance_report` | Compliance documentation | `.md` |

---

## 5. References

- Ontology: `Layer_1_Foundations/_ontology/ontology.types.json`
- Entity Model: `Layer_1_Foundations/_entity_model/ENTITY_MODEL.md`
- Compiler: `Layer_1_Foundations/_compiler/COMPILER_SPECIFICATION.md`
