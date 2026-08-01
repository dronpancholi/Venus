# Engine: Monorepo Generator

## 1. Context & Strategy

### 1.1 Purpose
The Monorepo Generator Engine automates the creation, scaffolding, and validation of standardized workspace repositories containing multiple applications and shared libraries. It establishes dependency boundaries, configures building toolchains (e.g., Turborepo, Nx), and enforces structure formats.

### 1.2 Philosophy
Monorepos must optimize build pipelines by using dependency analysis. Changed modules should trigger test executions only for their direct and transitive dependents.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Target workspaces list, dependency configuration maps, library template targets, build tool targets.
*   **Outputs**: Scaffolded Monorepo directory structure, Turborepo pipeline configuration files, package maps, and dependency graph reports.

### 2.2 Processing Pipeline
```
[Ingest Workspace Configuration] ──► [Build Dependency Graph (DAG)] ──► [Run Topological Sort] ──► [Generate Configs & Packages]
```

---

## 3. Algorithmic Checks & Computations

### 3.1 Topological Sorting & Dependency Ordering
The engine builds a Directed Acyclic Graph (DAG) representing packages ($V$) and dependency relationships ($E$). It executes Kahn's Algorithm to determine the compilation sequence and detect cyclic dependencies.

1.  **Calculate In-Degrees**: For each node, count incoming edges (dependencies).
2.  **Queue Sources**: Enqueue all nodes with in-degree $= 0$.
3.  **Process Queue**:
    *   Dequeue node $u$, append to compilation order.
    *   For each neighbor $v$ of $u$, decrement its in-degree.
    *   If in-degree of $v$ becomes $0$, enqueue $v$.
4.  **Cycle Check**: If the final compilation list length $< |V|$, a cyclic dependency exists, and the monorepo build is aborted.

### 3.2 Build Time Reduction Factor
The expected build acceleration ($R_{build}$) using cache restoration and parallel execution is modeled as:

$$R_{build} = \frac{T_{full\_serial}}{\sum_{k=1}^{D} \max(T_{stage\_k})}$$

Where $D$ is the depth of the sorted dependency graph, and stages are run in parallel.

---

## 4. Monorepo Package Definition Schema
Workspace definitions must pass check audits against this structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MonorepoWorkspaceManifest",
  "type": "object",
  "properties": {
    "workspaces": {
      "type": "array",
      "items": { "type": "string" }
    },
    "pipeline": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "dependsOn": {
            "type": "array",
            "items": { "type": "string" }
          },
          "outputs": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  },
  "required": ["workspaces", "pipeline"]
}
```

---

## 5. Reusable Checklist & Exit Criteria
*   [ ] Checked that dependency graphs contain no cycles (Kahn's Algorithm validation).
*   [ ] Confirmed build configurations cache build outputs correctly to prevent rebuilding unchanged packages.
*   [ ] Verified package dependency scopes are declared explicitly (avoiding global node modules inheritance).
*   [ ] Checked that formatting and linter scripts can target changed workspaces selectively.
*   *Exit Criteria*: Monorepo structures pass topological sorting validation, outputting a zero-cycle build graph.
