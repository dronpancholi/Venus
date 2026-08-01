# Project Venus UEAOGOS — Part 09: PMO Governance
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Operational Core

---

## 1. Operational Purpose & Scope
This standard details the governance framework, stage-gate criteria, and tracking rules for the Project Management Office (PMO). It ensures that all projects are initiated, executed, and closed with rigorous operational control.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Project charters and business cases.
- **Input Source**: Sprint reports, JIRA velocity charts, and resource timetables.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Project Status Reports and gate review approvals.
- **Output Artifact**: Master project dependency maps.

---

## 2. Core Pillars of PMO Governance
1. **Stage-Gate Authorization**: Projects must satisfy criteria at defined gates (Initiation, Planning, Execution, Closure) to proceed.
2. **Standardized Telemetry**: Project metrics are measured uniformly across all divisions.
3. **Dependency Mapping**: Proactive resolution of cross-project resource conflicts.
4. **Retrospective Continuous Improvement**: Mandatory post-mortems for every project closure.

---

## 3. Mathematical Model of Project Health Index
We define the Project Health Index ($PHI$) to measure performance based on Schedule and Cost performance indicators.

$$PHI = w_1 \cdot SPI + w_2 \cdot CPI$$

Where:
- $SPI$ is the Schedule Performance Index:

$$SPI = \frac{BCWP}{BCWS}$$

- $CPI$ is the Cost Performance Index:

$$CPI = \frac{BCWP}{ACWP}$$

- $BCWP$ is the Budgeted Cost of Work Performed (Earned Value).
- $BCWS$ is the Budgeted Cost of Work Scheduled (Planned Value).
- $ACWP$ is the Actual Cost of Work Performed (Actual Cost).
- $w_1, w_2$ are priority weights ($w_1 + w_2 = 1.0$; baseline: $w_1 = 0.5$, $w_2 = 0.5$).

### 3.1 Calculation Steps & Evaluation Thresholds
1. Calculate the Budgeted Cost of Work Scheduled ($BCWS$).
2. Retrieve the Earned Value ($BCWP$) and Actual Cost ($ACWP$) from tracking tables.
3. Compute $SPI$ and $CPI$.
4. Compute the composite index $PHI$.
5. **Evaluation Thresholds**:
   - $PHI \ge 1.0$: Project is ahead of schedule or under budget.
   - $0.85 \le PHI < 1.0$: Project is within tolerable limits; monitor closely.
   - $PHI < 0.85$: Project is critically off track; triggers mandatory review.

---

## 4. Technical Configuration Specification (PMO Gate Policy YAML)
```yaml
pmo_governance_policy:
  version: "0.11"
  system: "UEAOGOS"
  stage_gates:
    gate_1_initiation:
      requirements:
        - "Project Charter Completed"
        - "Executive Sponsor Assigned"
      approvers:
        - "PMO Director"
    gate_2_planning:
      requirements:
        - "WBS Defined"
        - "Dependencies Mapped"
        - "Budget Approved"
      approvers:
        - "PMO Director"
        - "COO"
    gate_3_execution:
      requirements:
        - "Schedule Performance Index >= 0.85"
        - "Cost Performance Index >= 0.85"
      approvers:
        - "Lead Program Manager"
```

---

## 5. Operational Verification Checklist

### 5.1 Pre-Execution Checks
- [ ] Confirm that the project budget codes are registered in the ledger.
- [ ] Establish JIRA templates and tracking workflows for the project.

### 5.2 Execution & Operation Verification
- [ ] Track weekly actuals against planned schedules.
- [ ] Calculate the Schedule and Cost performance indexes ($SPI$ and $CPI$).

### 5.3 Post-Execution & Review Gates
- [ ] Conduct the project retro review and archive project files.
- [ ] Log actual costs vs budgeted targets in the PMO database.

### 5.4 Exception Handling & Emergency Rollback
- [ ] If a project fails to clear Gate 3 due to a schedule delay of more than 30 days, halt new task creation and host a project scope reduction session.

---

## 6. Absolute System Links
- **Previous Chapter**: [Part 08: CPO Operating System](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/PART_08_CPO_OPERATING_SYSTEM.md)
- **Next Chapter**: [Part 10: Portfolio Management](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/PART_10_PORTFOLIO_MANAGEMENT.md)
