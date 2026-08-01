# GENESIS-I DEVELOPER HANDBOOK

**Version**: 1.0.0

---

## 1. Getting Started

```bash
# Run the platform
cd venus
python3 -m genesis info

# Compile a source file
python3 -m genesis compile Layer_1_Foundations/_schemas/BASE_ENTITY_SCHEMA.json

# Validate artifacts
python3 -m genesis validate path/to/file

# Run diagnostics
python3 -m genesis diagnose

# Index repository
python3 -m genesis index

# Explore the knowledge graph
python3 -m genesis graph stats
```

## 2. Platform Concepts

### Entity → UIR → Artifact

Every entity (OS, part, template, capability) is defined as a `BaseEntity` subclass.
When compiled, entities are parsed into an AST, then built into UIR graphs.
Code generators produce final artifacts (markdown, schemas, graph exports).

### Capability → Plugin → Extension

Capabilities are registered in the `CapabilityRegistry`. Plugins implement capabilities.
The plugin manager loads them, resolves dependencies, and activates hooks.

### Workflow → Task → Execution

Workflows are DAGs of tasks. The execution engine plans (topological sort),
schedules, and executes tasks. Each task has dependencies, inputs, and outputs.

## 3. Adding a New Feature

### New Capability
```python
from genesis.capability.registry import CapabilityDefinition, capability_registry

my_cap = CapabilityDefinition("analytics", "Data analytics engine", "1.0.0")
my_cap.add_interface("query", "POST", "/v1/analytics/query")
capability_registry.register(my_cap)
```

### New Validator
```python
from genesis.validation.engine import BaseValidator, ValidationEngine

engine = ValidationEngine()

@engine.register_func("my_check", "quality")
def my_check(target):
    return ValidationResult("my_check", "quality", True, "OK")
```

### New Compiler Pass
```python
from genesis.compiler.passes.base import CompilerPass

class LoggingPass(CompilerPass):
    def run(self, cu):
        print(f"Processing {len(cu.ast.nodes)} nodes")
        return cu

from genesis.compiler import Compiler
comp = Compiler()
comp.register_pass(LoggingPass())
```

## 4. Best Practices

1. **Always extend, never modify core** — Use plugins, passes, and validators
2. **Validate early** — Register validators for every new artifact type
3. **UIR is the contract** — All subsystems communicate through UIR
4. **Write tests** — Each validator, pass, and generator should have unit tests
5. **Use the type system** — Always set `semantic_type` on entities
6. **Keep graphs healthy** — Run diagnostics regularly to catch orphan nodes and cycles

## 5. Debugging

```python
# Inspect compilation
from genesis.compiler import Compiler
comp = Compiler()
cu = comp.compile("source.json")
print(f"AST nodes: {len(cu.ast.nodes)}")
print(f"Dependencies: {len(cu.dependencies.edges)}")

# Validate any file
from genesis.validation import ValidationEngine
engine = ValidationEngine()
for r in engine.validate_path("file.json"):
    print(f"  [{r.severity}] {r.validator_name}: {r.message}")

# Graph exploration
from genesis.graph import KnowledgeGraphEngine
kg = KnowledgeGraphEngine()
print(kg.summary())
print(kg.export_cypher())
```
