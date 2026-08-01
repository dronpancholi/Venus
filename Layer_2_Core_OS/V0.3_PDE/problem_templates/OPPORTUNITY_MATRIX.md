# Template: Opportunity Matrix

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Matrix ID**: OPP-[UUID]
*   **Last Updated**: [Date]
*   **Verification Owner**: [Name]

---

## 2. Identified Opportunities & Impact Matrix
*Map identified opportunities hidden within the validated problem space.*

| Opportunity ID | Type | Description | Target Benefit | Feasibility (1-5) | Strategic Value (1-5) | Priority | Status |
|---|---|---|---|---|---|---|---|
| **OPP-AUTO-01**| Automation | [e.g., Automate email review queues] | 90% manual labor reduction | 4 | 5 | **High** | **Under Evaluation**|
| **OPP-AI-01**  | AI Integration | [e.g., LLM categorization of web pages] | Better classification accuracy| 3 | 4 | **Medium** | **Planned Spike** |
| **OPP-COST-01**| Cost Reduction | [e.g., Cache API requests locally] | Save $4,000/mo API cost | 5 | 5 | **Critical**| **Approved** |
| **OPP-PLAT-01**| Platformization| [e.g., Build internal rate limiter API] | Reusable across 3 other apps | 2 | 4 | **Low** | **Deferred** |
| **OPP-IP-01**  | IP Creation | [e.g., Unique crawling scheduling model] | Patentable scheduling tech | 2 | 5 | **Medium** | **Under Evaluation**|

---

## 3. Priority Scoring Model
Priority is calculated by evaluating complexity vs. strategic yield:

\[Priority\_Score = \frac{Feasibility \times Strategic\_Value}{2.0}\]

*   **Feasibility (1-5)**: 1: Extremely complex (months of engineering). 5: Trivial (completed in a day).
*   **Strategic Value (1-5)**: 1: Nice-to-have optimization. 5: Core differentiator / high revenue driver.

*Priority Classifications:*
*   **Score >= 8.0**: Immediate Win (Approve for next phase).
*   **Score 4.0 - 7.9**: Evaluate (Run design spike / run cost analysis).
*   **Score < 4.0**: Defer or Reject.

---

## 4. Opportunity Deep-Dives & Feasibility Studies

### OPP-COST-01: Local Caching of API Requests
*   **Opportunity Description**: *Implement a local Redis key-value cache to store external API data payload response for up to 24 hours, reducing duplicate paid requests.*
*   **Target Metrics**:
    *   *External Requests Reduced*: From 50,000 requests/day to < 10,000 requests/day (-80% reduction).
    *   *API Budget Saving*: ~$4,000 / month.
*   **Technical Implementation Cost**: ~3 engineering days (Redis setup + cache invalidation logic).
*   **Decision**: **Approved** (Priority Score = 12.5)

### OPP-AUTO-01: Automated Email Review Queue
*   **Opportunity Description**: *Create an automated filter that uses lightweight heuristic scoring to auto-approve outreach requests, alerting operators only for anomalous emails.*
*   **Target Metrics**:
    *   *Operator Time Savings*: 15 hours / week.
    *   *Error Rate*: Must remain < 1.0% false approvals.
*   **Technical Implementation Cost**: ~5 engineering days (regex parser + Sentry notification rules).
*   **Decision**: **Approved** (Priority Score = 10.0)

---

## 5. Opportunity Realization Log
*Track realized opportunities, documenting actual metrics compared to projections.*

*   **Opportunity ID**: OPP- realized-01
    *   *Description*: [Description]
    *   *Actual Savings/Benefit*: [e.g., Reduced monthly API bills by $3,800]
    *   *Engineering Time Invested*: [e.g., 2.5 working days]
    *   *Lessons Learned*: [e.g., Cache keys require standard schema mapping to prevent stale results]
