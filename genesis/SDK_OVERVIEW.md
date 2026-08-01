# GENESIS-I SDK OVERVIEW

The platform provides five SDK domains for extension and integration.

---

## 1. Compiler SDK

**Location**: `genesis/compiler/`

| Component | Purpose |
|-----------|---------|
| `Compiler` | Main entry point. Compile sources to UIR. |
| `Parser` | Add new input formats via `_parse_*` methods |
| `CompilerPass` | Subclass for optimization passes |
| `CodeGenerator` | Subclass for output format generation |
| `PassRegistry` | Register and sequence compiler passes |
| `CodeGenRegistry` | Register code generators |

### Usage
```python
from genesis.compiler import Compiler
comp = Compiler()
# Register custom pass
from genesis.compiler.passes.base import CompilerPass
class MyPass(CompilerPass):
    def run(self, cu):
        cu.metadata_graph.annotate("my_pass", "processed", True)
        return cu
comp.register_pass(MyPass())
# Compile
cu = comp.compile("source.venus")
```

---

## 2. Plugin SDK

**Location**: `genesis/plugin/`

| Component | Purpose |
|-----------|---------|
| `PluginManifest` | Define plugin metadata, deps, hooks |
| `PluginManager` | Register, load, activate plugins |
| `PluginInstance` | Runtime representation of loaded plugin |
| `Sandbox` | Restricted execution environment |

### Usage
```python
from genesis.plugin import PluginManifest, PluginManager

manifest = PluginManifest(
    name="my-plugin",
    version="1.0.0",
    entry_point="plugin.py"
)
manifest.add_hook("validation", "on_validate")

manager = PluginManager()
manager.register_plugin(manifest)
manager.activate("my-plugin")
```

---

## 3. Repository SDK

**Location**: `genesis/indexer/`, `genesis/graph/`, `genesis/core/metadata.py`

| Component | Purpose |
|-----------|---------|
| `RepositoryIndexer` | Scan repo, build catalog, detect issues |
| `KnowledgeGraphEngine` | Graph operations, export, query |
| `MetadataEngine` | Automatic metadata for all artifacts |

### Usage
```python
from genesis.indexer import RepositoryIndexer
indexer = RepositoryIndexer("/path/to/repo")
summary = indexer.scan()
print(summary["total_files"], "files indexed")
```

---

## 4. Validation SDK

**Location**: `genesis/validation/`

| Component | Purpose |
|-----------|---------|
| `ValidationEngine` | Run validators, get results, summary |
| `BaseValidator` | Subclass for custom validators |
| `ValidationResult` | Single check result |

### Usage
```python
from genesis.validation import ValidationEngine
from genesis.validation.engine import BaseValidator

class SecurityValidator(BaseValidator):
    def __init__(self):
        super().__init__("security_check", "security")
    def validate(self, target):
        return self.result(True, "Security check passed")

engine = ValidationEngine()
engine.register(SecurityValidator())
results = engine.validate_path("artifact.json")
summary = engine.summary(results)
```

---

## 5. API SDK

**Location**: `genesis/api/`

| Component | Purpose |
|-----------|---------|
| `APIRouter` | Route requests to handlers |
| `Request` | Incoming API request |
| `Response` | API response with status/data/error |

### Usage
```python
from genesis.api import APIRouter

router = APIRouter()

def handle_search(req):
    return {"results": ["item1", "item2"]}

router.register_handler("GET", "/v1/search", handle_search)
```

---

## 6. Runtime SDK

**Location**: `genesis/runtime/`

| Component | Purpose |
|-----------|---------|
| `ExecutionEngine` | Execute workflows |
| `Workflow` | DAG of tasks |
| `Task` | Single executable unit |

### Usage
```python
from genesis.runtime import ExecutionEngine, Workflow, Task

engine = ExecutionEngine()
wf = engine.create_workflow("build-pipeline")
t1 = Task(name="compile", handler=lambda: "compiled")
wf.add_task(t1)
engine.execute(wf.workflow_id)
```
