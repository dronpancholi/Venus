# Part 17 — Quality Systems

## 1. Context & Strategy

### 1.1 Purpose
The Quality Systems Part defines methodologies for evaluation, scorecards, and testing protocols. It enforces objective usability audits, cognitive walkthroughs, and quality controls before features are shipped.

---

## 2. The Heuristic Evaluation Framework

We evaluate interfaces against Nielsen's 10 Usability Heuristics, assigning a Severity Rating ($0 - 4$) to each violation.

### 2.1 Severity Rating Matrix
*   **0 (No Usability Issue)**: Does not affect usage.
*   **1 (Cosmetic Problem Only)**: Fix can be deferred; does not block users.
*   **2 (Minor Usability Problem)**: Users can work around it; low priority.
*   **3 (Major Usability Problem)**: Important to fix; causes significant friction and slows tasks.
*   **4 (Usability Catastrophe)**: Imperative to fix; prevents users from completing tasks.

### 2.2 Quantitative UX Quality Score (UXQS)
To track quality across releases, we calculate the weighted UX Quality Score:

$$\text{UXQS} = 100 - \sum_{i=1}^{10} w_i \times \text{Severity}_i$$

Where:
*   $\text{Severity}_i$ is the average severity rating ($0-4$) assigned by auditors for Heuristic $i$.
*   $w_i$ is the weight multiplier assigned to Heuristic $i$ based on business impact (e.g., $w = 2.5$ for "Error Prevention" and "Help & Documentation").
*   *Exit Criteria*: Any screen targeting production release must achieve a $\text{UXQS} \ge 85$.

---

## 3. Cognitive Walkthrough Process

Auditors execute task walkthroughs from the user's perspective, answering four primary questions at each step:

```
[User Action Step] ──► [Will user try to achieve correct effect?] ──► [Will user notice action is available?]
                              │                                                  │
                             Yes                                                Yes
                              │                                                  │
                              ▼                                                  ▼
                       [Will user associate] ───────────────► [Will user understand feedback?]
                       [action with effect?]
```

### 3.1 Step Evaluation Table
For each step in a task flow, the auditor logs:

| Action Step | Target Action | 1. Intent? (Y/N) | 2. Visibility? (Y/N) | 3. Association? (Y/N) | 4. Feedback? (Y/N) | Severity |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Step 1** | Click "Export CSV" | Y | Y | Y | N | 2 (Missing progress bar) |
| **Step 2** | Select columns | Y | N | Y | Y | 3 (Filters hidden under dropdown) |

---

## 4. Usability Review Guidelines

Usability reviews must capture direct interaction data from representative cohorts.

### 4.1 Cohort Selection Metrics
*   **Audience Size**: Minimum of 5 users per persona segment (Nielsen's rule of diminishing returns states 5 users reveal $>80\%$ of usability problems).
*   **Competency Split**: Mix of $20\%$ expert power users and $80\%$ novice users to check both learnability and efficiency.

### 4.2 Key Performance Indicators (KPIs)
Reviews must report:
*   **Task Success Rate (TSR)**: Percentage of tasks completed successfully.
    $$\text{TSR} = \frac{\text{Completed Tasks}}{\text{Total Attempted Tasks}} \times 100$$
*   **Time on Task (ToT)**: Mean time taken to complete a specific task.
*   **System Usability Scale (SUS)**: Standard 10-item questionnaire score (target $\ge 80$).

---

## 5. Quality Systems Checklist
*   [ ] Performed Heuristic Evaluation using the Severity Rating system.
*   [ ] Calculated the final UXQS and confirmed it meets the gating threshold ($\ge 85$).
*   [ ] Executed Cognitive Walkthrough for primary workflows and resolved feedback gaps.
*   [ ] Completed Usability Review with a minimum cohort size of 5 participants.
*   [ ] Documented TSR, ToT, and SUS metrics for comparative evaluation.
