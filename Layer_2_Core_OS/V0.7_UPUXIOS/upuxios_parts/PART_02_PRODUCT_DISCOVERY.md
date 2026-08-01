# Part 02: Product Discovery & Opportunity Validation

## 1. Context & Strategy
Product Discovery under Project Venus is the mechanism by which customer pain, market demand, and technology feasibility are translated into validated product capabilities. This manual structures how we define user problems, prioritize product opportunities, and establish metric-driven validation gates before moving ideas into the active product strategy pipeline.

---

## 2. Jobs-to-Be-Done (JTBD) Mapping
We structure product discovery around user progress rather than product features. A job spec maps:
1.  **Core Job**: The fundamental progress the user wants to make (e.g., "Ensure all transaction logs are compliant for the quarterly audit").
2.  **Job Executor**: The persona responsible for executing the job (e.g., Compliance Manager).
3.  **Context**: The environmental, emotional, and social factors surrounding execution.
4.  **Job Steps**:
    *   *Define*: Plan resources and compliance scope.
    *   *Locate*: Access raw transaction repositories.
    *   *Prepare*: Format and tag transaction attributes.
    *   *Confirm*: Validate records against regulatory rules.
    *   *Resolve*: Address failures or compliance gaps.
    *   *Modify*: Save rules for subsequent cycles.

---

## 3. Opportunity Scoring Model
To identify under-served and over-served user jobs, we measure customer perception of **Importance** and **Satisfaction** across specific job outcomes using the Tony Ulwick Opportunity Landscape model.

### 3.1 The Opportunity Formula
For each target outcome, collect user survey ratings on a scale of $1$ to $10$ for Importance ($I$) and Current Satisfaction ($S$). The Opportunity Score ($OS$) is calculated as follows:

$$OS = I + \max(I - S, 0)$$

Where:
*   $I$: Importance rating (average score from $1$ to $10$).
*   $S$: Satisfaction rating of current solutions (average score from $1$ to $10$).

#### Interpretation:
*   $OS > 15$: **Under-served Opportunity**. High priority for development.
*   $OS < 10$: **Over-served/Low-priority Opportunity**. Candidate for cost reduction or ignoring.
*   $10 \le OS \le 15$: **Appropriately Served**. Monitor for incremental improvements.

---

## 4. North Star Metric Framework
Every product initiative must align with a single core metric that measures the real value delivered to users.

```
                      +-----------------------------+
                      |      NORTH STAR METRIC      |
                      | (e.g., Auto-Validated Logs) |
                      +-----------------------------+
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼                                                 ▼
  [Input Metric 1: Reach]                           [Input Metric 2: Efficiency]
  (e.g., Weekly Active Org Units)                   (e.g., Avg Time to Audit Close)
```

### 4.1 North Star Metric Specifications
1.  **Value Metric**: Must measure actual product value realized by the user, not a proxy metric like registrations or page views.
2.  **Breadth**: How many organizations or users are realizing this value?
3.  **Depth**: What is the volume/intensity of value delivery (e.g., number of compliance checks executed successfully)?
4.  **Frequency**: How often does the user experience this value?

---

## 5. Discovery Validation Gates
Before an opportunity enters the engineering queue, it must pass three checks:
*   **Feasibility Check**: Can engineering construct it within resource boundaries?
*   **Viability Check**: Does the solution conform to unit economics, regulatory compliance, and business model targets (from V0.6)?
*   **Usability Check**: Can the ICP persona complete the workflow within acceptable cognitive limits (from Part 01)?

---

## 6. Product Discovery Checklist
*   [ ] Structured opportunity using the Job-to-Be-Done syntax.
*   [ ] Calculated the Opportunity Score ($OS$) using customer survey datasets.
*   [ ] Defined the North Star Metric and at least two distinct Input Metrics.
*   [ ] Obtained Feasibility sign-off from Engineering Lead.
*   [ ] Obtained Viability sign-off from Product Operations Lead.
