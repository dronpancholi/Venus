# Template: Assumption Register

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Register ID**: ASM-[UUID]
*   **Last Updated**: [Date]
*   **Review Owner**: [Name]

---

## 2. Active Assumptions Registry

| Assumption ID | Description | Category | Evidence Level (1-5) | Impact Level (1-5) | Validation Cost (1-5) | Risk Score | Status |
|---|---|---|---|---|---|---|---|
| **ASM-MKT-01** | [e.g., Users will pay $20/mo for indexing] | Market | 2 | 5 | 1 | 2.5 | **UNVALIDATED** |
| **ASM-ENG-01** | [e.g., Target API can handle 100 req/sec] | Engineering | 4 | 4 | 2 | 1.0 | **VALIDATED** |
| **ASM-AI-01** | [e.g., LLM can parse email with 98% accuracy] | AI | 1 | 5 | 3 | 5.0 | **CRITICAL** |
| **ASM-SEC-01** | [e.g., Webhook endpoints are immune to injection] | Security | 3 | 5 | 2 | 1.67 | **UNVALIDATED** |
| **ASM-FIN-01** | [e.g., OpenAI API cost won't exceed $500/mo] | Financial | 2 | 4 | 1 | 2.0 | **UNVALIDATED** |

---

## 3. Scoring & Risk Formula
Risk score is calculated to prioritize validation efforts:

\[Risk\_Score = \frac{Impact\_Level \times Validation\_Cost}{Evidence\_Level}\]

*   **Evidence Level**: 1: No evidence (guess). 3: Verbal confirmation/industry benchmark. 5: Sandbox code proof/real user transaction log.
*   **Impact Level**: 1: Minor UI change. 5: Total project failure/abandonment.
*   **Validation Cost**: 1: 10 mins script/search. 3: Multi-day Spike implementation. 5: Complex customer trial/hardware build.

*High Risk Scores (> 3.0) require immediate mitigation prior to entering architectural engineering.*

---

## 4. Validation & Mitigation Execution Plans

### ASM-AI-01: LLM Parsing Accuracy
*   **Assumption Description**: *LLM can parse inbound email templates with 98% accuracy.*
*   **Validation Protocol**:
    1.  Collect 500 sample inbound emails from past logs.
    2.  Write a Python script to run offline tests against OpenAI/Gemini endpoints.
    3.  Measure parser output against manual ground truth labels.
*   **Exit Criteria**: Script records accuracy >= 98% across all test sets.
*   **Actual Outcome**: [Pending validation execution] | **Updated Status**: [UNVALIDATED / VALIDATED / REFUTED]

### ASM-MKT-01: User Price Sensitivity
*   **Assumption Description**: *Users will pay $20/mo for automated indexing.*
*   **Validation Protocol**:
    1.  Set up simple landing page with pricing selector.
    2.  Drive 100 targeted clicks from ad campaign.
    3.  Measure pre-order CTA click rates.
*   **Exit Criteria**: Pre-order button click rate >= 3.5%.
*   **Actual Outcome**: [Pending validation execution] | **Updated Status**: [UNVALIDATED / VALIDATED / REFUTED]

---

## 5. History of Refuted Assumptions
*Document assumptions that were proven false during validation, explaining how they altered project plans.*

*   **Refuted Assumption ID**: ASM-ENG-02
    *   *Description*: *Third-party API rate limit is 10,000 requests per minute.*
    *   *Refutation Evidence*: Real-world testing revealed a hard limit of 60 requests per minute.
    *   *Impact*: Changed architecture to implement queue-based throttling and database caching.
