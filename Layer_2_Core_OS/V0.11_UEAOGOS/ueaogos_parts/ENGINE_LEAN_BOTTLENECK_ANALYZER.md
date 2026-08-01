# UEAOGOS Core Engine: Lean Bottleneck Analyzer
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Analyzes value streams and workflow nodes to isolate queues, bottlenecks, and optimization targets in operational pipelines.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Workflow management system logs (Jira, ServiceNow, ERP).
- **Input Source**: Process duration metrics and work-in-progress (WIP) counts.
- **Input Source**: Resource capacity profiles and utilization charts.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Value Stream Map and Queue Analysis Report.
- **Output Artifact**: Bottleneck Priority Index.
- **Output Artifact**: WIP Limit restructuring guidelines.

### 1.3 Integration & Automation Triggers
- Scheduled bi-weekly to analyze development and operational queue health.
- Triggered when target process lead time exceeds SLA commitments by 20%.
- Executed during business process re-engineering projects.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$PEI = \frac{\sum T_{va}}{T_{lead}} \times 100$$

$$WIP = \lambda \cdot T_{lead}$$

### 2.2 Variable Definitions
- $PEI$: Process Efficiency Index (percentage).
- $T_{va}$: Value-add processing time (actual execution time).
- $T_{lead}$: Lead time (total time spent in the system, including queue wait times).
- $WIP$: Average Work-in-Progress count.
- $\lambda$: Average throughput rate of the process.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Reconstruct process execution paths from activity event log databases.
2. Calculate value-add time vs. non-value-add queue time for each process stage.
3. Compute stage-level WIP values and process capacity constraints.
4. Identify the bottleneck stage as the step with the highest queue buildup and lowest capacity.
5. Recommend specific WIP limits to align system throughput with bottleneck capacity.

---

## 3. Configuration & Output Validation Schema
```python
def analyze_bottlenecks(stages: list) -> dict:
    # stages is a list of dicts with: name, arrival_rate, service_rate, current_wip
    bottleneck = max(stages, key=lambda s: s["current_wip"] / s["service_rate"])
    results = {
        "bottleneck_node": bottleneck["name"],
        "utilization": bottleneck["arrival_rate"] / bottleneck["service_rate"],
        "recommended_wip_limit": max(1, int(bottleneck["service_rate"] * 2.0))
    }
    return results

```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Extract workflow timestamp logs from Jira or corporate database.
  - [ ] Validate that stage transitions are mapped sequentially without loops.
- [ ] **Execution & Scan Verification**:
  - [ ] Map lead times, WIP, and throughput for each process stage.
  - [ ] Calculate process efficiency indices and locate queue constraints.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Deliver value stream profiles to process owners and PMO teams.
  - [ ] Update WIP limit configurations in execution tools.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Fall back to historical averages if logs contain missing timestamps.
  - [ ] Trigger manual validation if calculated process efficiency is $<1\%$ (potential logging failure).

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
- [ENGINE_KPI_TELEMETRY_ENGINE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_KPI_TELEMETRY_ENGINE.md)
- [ENGINE_SIX_SIGMA_DEFECT_DETECTOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_SIX_SIGMA_DEFECT_DETECTOR.md)
- **Output Templates**:
- [VALUE_STREAM_MAP.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/VALUE_STREAM_MAP.md)
- [PROCESS_OPTIMIZATION_STATEMENT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/PROCESS_OPTIMIZATION_STATEMENT.md)
