# UEAOGOS Core Engine: PMO Project Health Assessor
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Conducts objective quantitative health evaluations of all active projects, tracking schedule and budget compliance using Earned Value Management (EVM).

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Project timelines, task statuses, and completion dates.
- **Input Source**: Actual project expense receipts and resource timecards.
- **Input Source**: Planned budget and scheduling forecasts.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: PMO Project Health Index Dashboard.
- **Output Artifact**: Earned Value Management (EVM) Variance Report.
- **Output Artifact**: Priority Escalation Flag Matrix.

### 1.3 Integration & Automation Triggers
- Scheduled weekly to assess portfolio health status.
- Triggered automatically when task slippage exceeds 10 business days.
- Executed during project phase-gate review milestones.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$\text{CPI} = \frac{\text{EV}}{\text{AC}}, \quad \text{SPI} = \frac{\text{EV}}{\text{PV}}$$

$$\text{TCPI} = \frac{\text{BAC} - \text{EV}}{\text{BAC} - \text{AC}}$$

### 2.2 Variable Definitions
- $CPI$: Cost Performance Index ($CPI < 1.0$ indicates over budget).
- $SPI$: Schedule Performance Index ($SPI < 1.0$ indicates behind schedule).
- $EV$: Earned Value (monetary worth of work actually performed).
- $AC$: Actual Cost (money spent to date).
- $PV$: Planned Value (monetary budget of work scheduled).
- $TCPI$: To-Complete Performance Index (required efficiency to meet target).
- $BAC$: Budget at Completion.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Extract project task status and actual spend figures from source repositories.
2. Calculate Planned Value ($PV$) and Earned Value ($EV$) for the review date.
3. Calculate performance index values ($CPI$, $SPI$, $TCPI$).
4. Classify project status into color codes (Green $\ge 0.95$, Yellow $[0.85, 0.95)$, Red $< 0.85$).
5. Flag projects with $TCPI > 1.2$ for immediate structural intervention.

---

## 3. Configuration & Output Validation Schema
```json
{
  "thresholds": {
    "yellow_cpi": 0.95,
    "red_cpi": 0.85,
    "yellow_spi": 0.95,
    "red_spi": 0.85
  },
  "min_project_budget_for_audit": 50000
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify that project schedule and expense reporting modules are locked for the audit period.
  - [ ] Validate baseline budget numbers ($BAC$) are approved.
- [ ] **Execution & Scan Verification**:
  - [ ] Calculate EVM metrics and health flags.
  - [ ] Detect trend variances over the last three periods.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Distribute the Project Health Summary to the PMO and executive committees.
  - [ ] Initiate project reviews for all flagged Red items.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Use milestones as progress indicator if task-level progress is not accurately logged.
  - [ ] Stop automated flags during active project replanning phases.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
- [ENGINE_CPO_PRODUCT_BACKLOG_BALANCER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_CPO_PRODUCT_BACKLOG_BALANCER.md)
- [ENGINE_PROGRAM_DEPENDENCY_MAPPER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_PROGRAM_DEPENDENCY_MAPPER.md)
- **Output Templates**:
- [PROJECT_HEALTH_DASHBOARD.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/PROJECT_HEALTH_DASHBOARD.md)
- [EVM_VARIANCE_REPORT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/EVM_VARIANCE_REPORT.md)
