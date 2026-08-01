# Annual Performance Appraisal Form & Calibration Guide
## Metadata
| Attribute | Value |
|---|---|
| Template ID | TEMPLATE_139 |
| Filename | TEMPLATE_139_ANNUAL_PERFORMANCE_REVIEW_FORM.md |
| Version | 2.1.0 |
| Classification | Confidential |
| Domain | Performance Evaluation |
| Owner | Talent Operations |
| Strategic Framework | [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md) |

---

## 1. Executive Summary & Purpose
This template provides the strategic operational standard for the Annual Performance Appraisal Form & Calibration Guide. It is designed to satisfy the core constitutional governance principles of Project Venus.

---

## 2. Mathematical Formulations & Performance Models
Overall Performance Rating ($OPR$) is calculated as follows:
$$OPR = w_{okr} \times OKR_{completion} + w_{comp} \times Competency_{score} + w_{peer} \times Peer_{feedback}$$
where weights must sum to 1.0:
$$w_{okr} = 0.50,\ w_{comp} = 0.30,\ w_{peer} = 0.20$$
Normalized performance score ($Z_{perf}$) is defined as:
$$Z_{perf} = \frac{OPR - \mu_{dept}}{\sigma_{dept}}$$

---

## 3. Operational Specification & Reference Table
| Evaluation Domain | Rating ($1 - 5$) | Weighted Score | Evaluator comments | Verification Status |
|---|---|---|---|---|
| OKR Completion | 4.2 | 2.10 | Reached all key project targets | Verified |
| Competency Profile | 3.8 | 1.14 | Strong engineering skills demonstrated | Verified |
| Peer Feedback | 4.5 | 0.90 | High feedback scores received | Verified |
| **Cumulative Score** | **4.14** | **4.14** | **Exceeds Expectations grade** | **Approved** |

---

## 4. System Configuration & Schema Definition
```json
{
  "performance_appraisal": {
    "rating_scale": {
      "1": "Unsatisfactory",
      "2": "Needs Improvement",
      "3": "Meets Expectations",
      "4": "Exceeds Expectations",
      "5": "Outstanding"
    },
    "scoring_weights": {
      "okr_completion": 0.50,
      "competency_score": 0.30,
      "peer_feedback": 0.20
    },
    "calibration_tolerance": 0.15
  }
}
```

---

## 5. Institutional Execution Checklist
### 5.1 Pre-Execution Phase
- [ ] Retrieve self-appraisals and peer evaluations from feedback database. - [ ] Generate performance calibration reports for department heads.

### 5.2 Execution Phase
- [ ] Conduct calibration review to align ratings across teams. - [ ] Facilitate performance discussion between manager and employee.

### 5.3 Post-Execution Phase
- [ ] Publish final calibrated rating to Employee Record. - [ ] Initialize the upcoming annual OKR planning cycle.

### 5.4 Exception / Rollback Phase
- [ ] Flag ratings for re-calibration if team scoring distributions deviate from normal distributions. - [ ] Recalculate average performance rating.

---

## 6. Document & Template References
- Strategic Core Governance: [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md)
- Target Directory: [ueaogos_templates](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/)
