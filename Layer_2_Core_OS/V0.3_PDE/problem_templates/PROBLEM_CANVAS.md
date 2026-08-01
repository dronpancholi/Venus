# Template: Problem Canvas

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Date Canvas Created**: [Date]
*   **Last Updated**: [Date]
*   **Lead Validator**: [Name]

---

## 2. The Canvas Layout

| **1. The Core Problem** | **3. Impacted Stakeholders** | **5. Key Constraints** | **7. Opportunities** |
|---|---|---|---|
| *Define the validated root cause (from root-cause analysis).* | *Who experiences the problem directly? Who is financially impacted?* | *What limits the space of potential solutions? (Technical, Regulatory, Time)* | *What strategic advantages or cost reductions are unlocked if solved?* |
| | | | |
| **2. Symptoms & Friction** | **4. Current Workarounds** | **6. Critical Unknowns** | **8. Success Metrics** |
| *What are the visible errors, delays, or costs?* | *How are teams currently bypassing the problem? What is the cost of these workarounds?* | *What are the high-risk, unvalidated assumptions or unknowns?* | *What quantitative KPIs define success?* |
| | | | |

---

## 3. Detail Specifications

### Section 1: The Core Problem
*   **Root Cause ID**: RC-[UUID]
*   **Description**:
    ```text
    [Provide a high-fidelity description of the underlying mechanical, structural, or systemic issue.]
    ```

### Section 2: Symptoms & Friction
*   **Observed Symptoms**:
    1.  [Symptom 1] | *Annual Cost/Delay*: [Metric, e.g., 40 engineering hours/week]
    2.  [Symptom 2] | *User Friction Index*: [e.g., 8/10 friction rating]
    3.  [Symptom 3] | *Failure Rate*: [e.g., 14.2% error rate in current pipeline]

### Section 3: Impacted Stakeholders
*   **Primary User**: [Role, e.g., SRE Engineer] | *Primary Friction*: [Description]
*   **Secondary User**: [Role, e.g., Content Editor] | *Primary Friction*: [Description]
*   **Economic Buyer**: [Role, e.g., VP Engineering] | *Primary Pain*: [Description]

### Section 4: Current Workarounds
*   **Workaround 1**: [Description] | *Efficiency Loss*: [e.g., -35% output velocity]
*   **Workaround 2**: [Description] | *Risk Level*: [e.g., High security risk due to manual CSV exports]

### Section 5: Key Constraints
*   **Technical Constraint**: [e.g., Must execute within < 50ms latency window]
*   **Regulatory Constraint**: [e.g., Zero exposure of PII outside EEA boundaries]
*   **Financial Constraint**: [e.g., Max running cost of $0.02 per transaction]

### Section 6: Critical Unknowns
*   **Unknown 1**: [Description] | *Impact*: [High/Medium/Low] | *Validation Plan*: [e.g., Execute Spike in Sprint 1]
*   **Unknown 2**: [Description] | *Impact*: [High/Medium/Low] | *Validation Plan*: [Description]

### Section 7: Opportunities
*   **IP / Moat**: [e.g., Patentable latency-optimization algorithm]
*   **Platform Potential**: [e.g., Can be generalized into a company-wide API gateway]
*   **Automation Yield**: [e.g., 90% reduction in manual review labor]

### Section 8: Success Metrics
*   **Primary Technical KPI**: [e.g., 99.99% pipeline reliability]
*   **Primary Business KPI**: [e.g., 30% reduction in customer support tickets]
*   **Primary Operational KPI**: [e.g., Time-to-resolution reduced from 4 hours to 5 minutes]
