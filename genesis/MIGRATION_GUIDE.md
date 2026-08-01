# GENESIS-I MIGRATION GUIDE

**Migrating from Venus Repository → Genesis-I Platform**

---

## Overview

This guide covers migrating from the Venus knowledge repository 
(documentation-based) to the Genesis-I executable platform (compiler-based).

## Step 1: Prerequisites

```bash
# Verify Python 3.10+
python3 --version

# Install dependencies (optional)
pip install pyyaml  # for YAML parsing
```

## Step 2: Initialize the Platform

```bash
# From the Venus repository root
cd /path/to/Venus

# Verify platform readiness
python3 -m genesis info

# Index the repository
python3 -m genesis index --path . --output _catalog.json

# Run diagnostics
python3 -m genesis diagnose --mode full
```

## Step 3: Compile Existing Artifacts

```bash
# Compile a single schema
python3 -m genesis compile Layer_1_Foundations/_schemas/BASE_ENTITY_SCHEMA.json

# Compile a DSL file (if .venus files exist)
python3 -m genesis compile path/to/file.venus

# Validate after compilation
python3 -m genesis validate path/to/generated/artifact
```

## Step 4: Build the Knowledge Graph

```python
from genesis.graph import KnowledgeGraphEngine
from genesis.indexer import RepositoryIndexer

# Index the repository
indexer = RepositoryIndexer("/path/to/Venus")
indexer.scan()

# Build knowledge graph
kg = KnowledgeGraphEngine()
kg.add_node("venus:root", "Project Venus", "project")
# ... add more nodes and edges from indexed catalog

# Export for Neo4j
cypher = kg.export_cypher()
with open("_graph/import.cypher", "w") as f:
    f.write(cypher)
```

## Step 5: Configure Plugins

```yaml
# _plugins/my-validator/plugin.yaml
name: my-validator
version: 1.0.0
entry_point: validator.py
capabilities:
  - validation
hooks:
  validation:
    - on_validate
```

## Step 6: Create Workflows

```python
from genesis.runtime import ExecutionEngine, Workflow, Task

engine = ExecutionEngine()
wf = engine.create_workflow("daily-validate")

t1 = Task(name="index-repo", handler=lambda: "indexed")
t2 = Task(name="validate-all", handler=lambda: "validated")
t3 = Task(name="generate-report", handler=lambda: "report generated")

wf.add_task(t1)
wf.add_task(t2)
wf.add_task(t3)
wf.add_sequence("index-repo", "validate-all", "generate-report")

engine.execute(wf.workflow_id)
```

## Rollback

```python
# If migration fails:
compiler = Compiler()
compiler.invalidate_cache()  # Clear all cached compilations
```

## Verification

```python
from genesis.diagnostics import Diagnostics
diag = Diagnostics()
results = diag.run("full")
summary = diag.summary()
print(f"Health score: {summary['health_score']}%")
```
