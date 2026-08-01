# UEAOGOS Core Engine: Six Sigma Defect Detector
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Calculates defect metrics, sigma levels, and process capabilities ($C_{pk}$) to optimize product and operations quality.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Quality assurance audit logs and product rejection databases.
- **Input Source**: Process telemetry measurements and engineering test files.
- **Input Source**: Specifications containing Upper (USL) and Lower (LSL) specification limits.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Six Sigma Quality and Process Capability Scorecard.
- **Output Artifact**: DPMO and Sigma Level tracking metrics.
- **Output Artifact**: Statistical Process Control (SPC) chart data.

### 1.3 Integration & Automation Triggers
- Run daily on manufacturing and software release defect registries.
- Invoked during sprint retrospectives or manufacturing quality gates.
- Triggered automatically when defect rates exceed defined control boundaries.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$DPMO = \frac{\text{Total Defects}}{\text{Total Units} \times \text{Opportunities/Unit}} \times 1,000,000$$

$$C_{pk} = \min\left( \frac{\text{USL} - \mu}{3\sigma}, \frac{\mu - \text{LSL}}{3\sigma} \right)$$

### 2.2 Variable Definitions
- $DPMO$: Defects Per Million Opportunities.
- $C_{pk}$: Process Capability Index (a values $> 1.33$ indicates adequate process capability).
- $USL$: Upper Specification Limit.
- $LSL$: Lower Specification Limit.
- $\mu$: Process average (mean).
- $\sigma$: Standard deviation of the process measurements.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Extract measurement samples and count the total occurrences of defects.
2. Calculate the mean and standard deviation of the measured characteristic.
3. Compute the DPMO and map it to the corresponding process Sigma Level.
4. Calculate $C_{pk}$ to determine if the process is capable and centered.
5. Alert process control teams if $C_{pk} < 1.0$ or Sigma Level $< 4.0$.

---

## 3. Configuration & Output Validation Schema
```json
{
  "process_parameters": {
    "lsl": 9.5,
    "usl": 10.5,
    "opportunities_per_unit": 3
  },
  "control_limits": {
    "target_sigma_level": 4.5,
    "critical_c_pk": 1.33
  }
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify that sample datasets contain at least 30 observations for valid statistical computation.
  - [ ] Confirm specification boundaries (USL, LSL) are set in the configuration.
- [ ] **Execution & Scan Verification**:
  - [ ] Calculate mean, standard deviation, DPMO, and capability index.
  - [ ] Detect out-of-control conditions using Western Electric Rules.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Publish quality metrics to the operations dashboard.
  - [ ] Flag violating processes for immediate engineering review.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] If standard deviation is 0 (due to lack of variance in small sample), skip capability calculation and flag warning.
  - [ ] Handle null values in specifications by defaulting to unilateral capability limits ($C_{pu}$ or $C_{pl}$).

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
- [ENGINE_LEAN_BOTTLENECK_ANALYZER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_LEAN_BOTTLENECK_ANALYZER.md)
- [ENGINE_COO_OPERATIONAL_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_COO_OPERATIONAL_AUDITOR.md)
- **Output Templates**:
- [SIX_SIGMA_QUALITY_REPORT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/SIX_SIGMA_QUALITY_REPORT.md)
- [SPC_CONTROL_CHART.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/SPC_CONTROL_CHART.md)
