# UEAOGOS Core Engine: Program Dependency Mapper
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Maps cross-project and cross-program dependencies, identifies critical paths, and flags dependency bottlenecks.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Project timelines, task schedules, and milestone linkages.
- **Input Source**: Shared resource models and cross-team dependencies.
- **Input Source**: Technical system integration plans.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Program Dependency Map (Network Graph).
- **Output Artifact**: Critical Path Dependency Report.
- **Output Artifact**: Risk Alert Matrix of out-of-order execution paths.

### 1.3 Integration & Automation Triggers
- Run during program kick-offs and planning phases.
- Executed weekly within PMO monitoring cycles.
- Triggered by changes to the scheduling baseline of critical milestones.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$\text{Length}(P_{critical}) = \max_{P} \sum_{v \in P} d(v)$$

$$C_D(v) = \text{in-degree}(v) + \text{out-degree}(v)$$

### 2.2 Variable Definitions
- $P_{critical}$: The critical path of the program dependency network.
- $d(v)$: Duration of activity/node $v$.
- $C_D(v)$: Degree centrality of node $v$, signaling the count of dependencies linked to it.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Import all project tasks, milestones, and links from scheduling databases.
2. Construct the program dependency Directed Acyclic Graph (DAG) $G = (V, E)$.
3. Calculate earliest/latest start and finish dates using the forward/backward pass algorithm.
4. Identify the critical path ($P_{critical}$) where total slack time is zero.
5. Flag high-centrality nodes ($C_D(v) > 5$) as potential systemic failure points.

---

## 3. Configuration & Output Validation Schema
```yaml
graph_rules:
  prohibit_cyclic_dependencies: true
  max_dependency_depth: 10
  centrality_warning_threshold: 6
output_formats:
  - mermaid_graph
  - adjacency_list

```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify that all scheduling data contains valid activity linkages and dates.
  - [ ] Confirm no cyclic dependencies exist before running path calculations.
- [ ] **Execution & Scan Verification**:
  - [ ] Construct the graph representation of the project portfolio.
  - [ ] Solve for critical paths and compute degree centrality values.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Export the graphical dependency chart to PMO wiki locations.
  - [ ] Send warnings to owners of tasks that sit on the critical path.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Terminate execution and output cycle paths if a cyclic loop is detected during DAG validation.
  - [ ] Apply default duration buffers if task duration parameters are missing.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
- [ENGINE_PMO_PROJECT_HEALTH_ASSESSOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_PMO_PROJECT_HEALTH_ASSESSOR.md)
- [ENGINE_PROJECT_GOVERNANCE_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_PROJECT_GOVERNANCE_AUDITOR.md)
- **Output Templates**:
- [CRITICAL_PATH_REPORT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/CRITICAL_PATH_REPORT.md)
- [DEPENDENCY_RISK_MATRIX.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/DEPENDENCY_RISK_MATRIX.md)
