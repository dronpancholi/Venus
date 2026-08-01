# Talent Acquisition Database Schema & Metrics Blueprint
## Metadata
| Attribute | Value |
|---|---|
| Template ID | TEMPLATE_126 |
| Filename | TEMPLATE_126_TALENT_ACQUISITION_SCHEMA.md |
| Version | 1.0.0 |
| Classification | Confidential |
| Domain | Talent Acquisition |
| Owner | CPO / HR Lead |
| Strategic Framework | [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md) |

---

## 1. Executive Summary & Purpose
This template provides the strategic operational standard for the Talent Acquisition Database Schema & Metrics Blueprint. It is designed to satisfy the core constitutional governance principles of Project Venus.

---

## 2. Mathematical Formulations & Performance Models
The hiring pipeline efficiency is tracked via the Selection Ratio ($SR$) and Yield Ratio ($YR_j$) for each stage $j$:
$$SR = \frac{N_{hired}}{N_{applicants}}$$
$$YR_j = \frac{N_{passed\_stage\_j}}{N_{entered\_stage\_j}}$$
The overall recruitment velocity $RV$ is modeled as:
$$RV = \sum_{j=1}^{M} T_j$$
where $T_j$ represents the mean time in days spent in pipeline stage $j$.

---

## 3. Operational Specification & Reference Table
| Stage ID | Stage Name | Target Conversion Rate | Benchmark Duration (Days) |
|---|---|---|---|
| 1 | Application Screening | $85.0\%$ | 2.0 |
| 2 | Initial Phone Screen | $40.0\%$ | 3.0 |
| 3 | Technical Assessment | $30.0\%$ | 5.0 |
| 4 | Panel Interviews | $25.0\%$ | 4.0 |
| 5 | Background & Reference | $95.0\%$ | 3.0 |
| 6 | Executive Sign-off | $99.0\%$ | 2.0 |

---

## 4. System Configuration & Schema Definition
```sql
CREATE TABLE candidates (
    candidate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    resume_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pipeline_stages (
    stage_id INT PRIMARY KEY,
    stage_name VARCHAR(50) NOT NULL,
    sequence_order INT NOT NULL
);

CREATE TABLE candidate_pipeline (
    pipeline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(candidate_id),
    stage_id INT REFERENCES pipeline_stages(stage_id),
    status VARCHAR(50) CHECK (status IN ('ACTIVE', 'PASSED', 'REJECTED', 'WITHDRAWN')),
    entered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Institutional Execution Checklist
### 5.1 Pre-Execution Phase
- [ ] Validate that hiring budget and headcount allocation are approved in Workday. - [ ] Verify the Job Description and Compensation Grade are matched to active role profile.

### 5.2 Execution Phase
- [ ] Publish the position to Lever and LinkedIn recruiting channels. - [ ] Initiate automated candidate tracking and trigger initial screening filters.

### 5.3 Post-Execution Phase
- [ ] Update HRIS database with the selected candidate's record. - [ ] Archive the rejected profiles in the talent pool for future outreach.

### 5.4 Exception / Rollback Phase
- [ ] Remove active job listings. - [ ] Notify candidates that the role search has been cancelled or postponed.

---

## 6. Document & Template References
- Strategic Core Governance: [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md)
- Target Directory: [ueaogos_templates](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/)
