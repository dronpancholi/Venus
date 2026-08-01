# UEAOGOS Core Engine: Performance Appraisal Audit Engine
## Version: 0.11 | Classification: Institutional Governance Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Audits annual performance reviews and rating calibrations to identify cognitive biases, team rating skew, and evaluation discrepancies.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Employee review scores and feedback texts.
- **Input Source**: Team structure data and budget allocations.
- **Input Source**: Competency matrices.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Performance Review Calibration Scorecard.
- **Output Artifact**: Rating Skew and Anomaly Reports.
- **Output Artifact**: Recommended adjustment plans.

### 1.3 Integration & Automation Triggers
- Run prior to finalizing employee ratings during performance calibration.
- Triggered automatically by rating distributions that vary from normal profiles.
- Run during post-cycle equity reviews.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$\text{BU Skew} = \frac{\mu_{BU} - \mu_{Global}}{\sigma_{Global}}$$

$$H(X) = -\sum_{i=1}^k P(x_i) \log_2 P(x_i)$$

### 2.2 Variable Definitions
- $\text{BU Skew}$: Z-score shift in performance ratings for a specific business unit.
- $\mu_{BU}$: Mean rating score in the target business unit.
- $\mu_{Global}$: Overall corporate mean rating score.
- $\sigma_{Global}$: Standard deviation of overall ratings.
- $H(X)$: Entropy score of the rating distribution (target $H(X) \ge 2.0$ to ensure ratings are not overly compressed).

### 2.3 Calculation Steps & Evaluation Thresholds
1. Gather performance evaluation scores across teams.
2. Compute average scores, standard deviations, and distributions.
3. Calculate Skew and Entropy parameters for each department.
4. Match rating metrics with demographic profiles to detect systemic bias.
5. Flag departments where rating skew values fall outside the $[-1.0, 1.0]$ interval.

---

## 3. Configuration & Output Validation Schema
```python
def analyze_rating_distribution(ratings: list, global_mean: float, global_std: float) -> float:
    if len(ratings) == 0 or global_std == 0:
        return 0.0
    local_mean = sum(ratings) / len(ratings)
    return (local_mean - global_mean) / global_std

```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Gather clean, normalized performance evaluation datasets.
  - [ ] Verify that baseline rating scale ranges are consistent.
- [ ] **Execution & Scan Verification**:
  - [ ] Compute performance metrics and distributions.
  - [ ] Detect departments with compressed or highly skewed distributions.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Deliver the calibration scorecard to Compensation and HR Committees.
  - [ ] Update tracking profiles for calibration targets.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Skip analysis for departments with fewer than 5 members to ensure confidentiality.
  - [ ] Apply adjustment values if team structure mappings are updated mid-cycle.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
- [ENGINE_CAREER_PROGRESSION_VALIDATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_CAREER_PROGRESSION_VALIDATOR.md)
- [ENGINE_LD_TRAINING_ROI_CALCULATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_parts/ENGINE_LD_TRAINING_ROI_CALCULATOR.md)
- **Output Templates**:
- [CALIBRATION_SUMMARY_REPORT.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/CALIBRATION_SUMMARY_REPORT.md)
- [BIAS_MITIGATION_GUIDELINES.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/BIAS_MITIGATION_GUIDELINES.md)
