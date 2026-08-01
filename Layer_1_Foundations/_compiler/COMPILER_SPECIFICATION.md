# PROJECT VENUS — COMPILER SPECIFICATION

**Version**: 1.0  
**Purpose**: Takes Venus DSL definitions, ontology, schemas, and knowledge graph as input; generates all artifacts.

---

## 1. Architecture

```
                           ┌─────────────────────┐
                           │    DSL Source Files   │
                           │  (*.venus, *.dsl)    │
                           └─────────┬───────────┘
                                     │
                           ┌─────────▼───────────┐
                           │    PARSER            │
                           │  (Lark grammar)      │
                           └─────────┬───────────┘
                                     │
                           ┌─────────▼───────────┐
                           │    AST               │
                           │  (Abstract Syntax    │
                           │   Tree)              │
                           └─────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
     │ TYPE CHECKER     │   │ REFERENCE        │   │ ONTOLOGY         │
     │ (validate types, │   │ RESOLVER         │   │ LOADER           │
     │  inheritance)    │   │ (resolve @refs)  │   │ (load type system)│
     └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
                           ┌─────────▼───────────┐
                           │    SEMANTIC MODEL    │
                           │  (Resolved, typed,   │
                           │   validated AST)     │
                           └─────────┬───────────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
     ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
     │ MARKDOWN GENERATOR │ │ JSON SCHEMA        │ │ MERMAID GENERATOR │
     │ (.md)              │ │ GENERATOR (.json)  │ │ (.mmd)            │
     └───────────────────┘ └───────────────────┘ └───────────────────┘

     ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
     │ PROMPT GENERATOR   │ │ VALIDATION         │ │ AGENT SPEC        │
     │ (prompt packs)     │ │ GENERATOR (.py)    │ │ GENERATOR (.json) │
     └───────────────────┘ └───────────────────┘ └───────────────────┘
```

---

## 2. Compiler Pipeline

### Stage 1: Parse
- Read `.venus` or `.dsl` files
- Parse into AST using Lark grammar
- Report syntax errors

### Stage 2: Load
- Load ontology types (`ontology.types.json`)
- Load canonical schemas (`_schemas/*.json`)
- Load existing knowledge graph
- Load entity model definitions

### Stage 3: Resolve
- Resolve all `@Reference` identifiers
- Build dependency graph
- Detect circular dependencies
- Validate inheritance chains

### Stage 4: Type Check
- Verify every entity has a valid ontology type
- Verify all required fields are present
- Verify field types match schema definitions
- Verify inheritance chains are valid

### Stage 5: Generate
- Generate markdown documentation
- Generate JSON Schema validation files
- Generate Mermaid diagrams
- Generate prompt packs
- Generate validation scripts
- Generate agent specifications
- Update catalog.json
- Update knowledge graph

### Stage 6: Validate
- Run generated validation scripts
- Verify all cross-references resolve
- Check naming conventions
- Report compilation results

---

## 3. Output Mapping

| DSL Construct | Markdown Output | Schema Output | Diagram Output |
|--------------|----------------|---------------|----------------|
| `operatingsystem` | OS root doc | OS manifest | Layer diagram |
| `part` | Part documentation | Part schema | Concept map |
| `engine` | Engine documentation | Engine schema | Flow diagram |
| `template` | Template document | JSON Schema | Template structure |
| `workflow` | Workflow doc | Workflow schema | Sequence diagram |
| `policy` | Policy document | Policy schema | Decision tree |
| `certificate` | Certificate doc | Certificate schema | Gate diagram |
| `agent` | Agent specification | Agent schema | Agent topology |
| `memory` | Memory specification | Memory schema | Memory hierarchy |

---

## 4. Compiler Configuration

```json
{
  "compiler": {
    "version": "1.0",
    "output_dir": "./_generated/",
    "generators": ["markdown", "json_schema", "mermaid", "prompt", "validation"],
    "strict_mode": true,
    "validate_references": true,
    "validate_schemas": true,
    "update_catalog": true,
    "update_graph": true
  }
}
```

---

## 5. Error Handling

| Error Type | Severity | Action |
|-----------|----------|--------|
| Syntax error | Block | Report line/column |
| Type error | Block | Report expected vs actual |
| Reference resolution failure | Block | Report unresolved ref |
| Circular dependency | Block | Report cycle path |
| Inheritance violation | Block | Report invalid chain |
| Missing required field | Warning | Report field name |
| Naming violation | Warning | Report convention issue |
