# Jobs-To-Be-Done (JTBD) Workflow Map

## 1. Document Overview
This document breaks down a user's core struggle into functional, emotional, and social "jobs." By decoupling the user's underlying goal from current solutions, we design workflows that target unmet needs and drive market adoption.

---

## 2. Job Statement Formulation
A well-defined Job Statement avoids solutions and focuses on the objective.

```
 [ VERB ] + [ OBJECT OF THE ACTION ] + [ CLARIFYING CONTEXT ]
  (e.g., Organize)   (e.g., tax records)       (e.g., without manual data entry)
```

*   **Core Functional Job:** [Insert Job Statement]
*   **Emotional Job (How user wants to feel):** [e.g., Feel organized and confident during audits]
*   **Social Job (How user wants to be perceived):** [e.g., Look professional to their accountant and stakeholders]

---

## 3. Job Execution Map (Workflow Stages)
Break down the job into the standard stages of execution.

| Stage | What the User is Doing | Current Tools/Methods | Pain Points / Friction | Opportunities |
| :--- | :--- | :--- | :--- | :--- |
| **1. Define / Plan** | Determining objectives and resources. | | | |
| **2. Locate / Gather** | Accessing inputs or info needed to start. | | | |
| **3. Prepare** | Organizing inputs or configuring the environment. | | | |
| **4. Confirm** | Validating inputs/readiness before action. | | | |
| **5. Execute** | Performing the core job step. | | | |
| **6. Monitor** | Assessing status and execution success. | | | |
| **7. Modify / Adjust** | Tweaking execution parameters based on feedback. | | | |
| **8. Conclude** | Finishing the execution and storing output. | | | |

---

## 4. Outcome Statements (Desired Outcomes)
Desired outcomes are metrics that customers use to measure success when executing the job. Format:

```
 [ DIRECTION ] + [ METRIC ] + [ OBJECT OF CONTROL ]
  (e.g., Minimize)  (e.g., the time it takes to) (e.g., resolve database lag)
```

List the key Desired Outcomes for this job:
1.  **Outcome 1:** `________________________________________`
2.  **Outcome 2:** `________________________________________`
3.  **Outcome 3:** `________________________________________`

---

## 5. Opportunity Score Calculation
To prioritize these desired outcomes, run customer surveys to evaluate **Importance** and **Satisfaction** (on a scale of 1 to 10). Use Tony Ulwick's Opportunity Score formula:

$$\text{Opportunity Score} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0)$$

*Note: Opportunities with a score $> 10$ are prime areas for innovation (underserved). Scores $< 5$ are overserved or unimportant.*

| Outcome Statement | Importance ($I$) | Satisfaction ($S$) | Opportunity Score | Strategic Priority |
| :--- | :---: | :---: | :---: | :--- |
| *Example: Minimize the time to compile compliance logs* | *9.2* | *3.1* | *15.3* | **Critical Path (Underserved)** |
| *Example: Maximize the portability of output files* | *4.0* | *8.0* | *4.0* | **Ignore (Overserved)** |
| | | | | |
| | | | | |

---

## 6. Actionable Product Requirements
Translating the highest opportunity jobs/outcomes into product focus areas:

*   **Opportunity Focus 1:** [Outcome Statement] $\rightarrow$ [Feature Concept]
*   **Opportunity Focus 2:** [Outcome Statement] $\rightarrow$ [Feature Concept]

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Created comprehensive JTBD Workflow Map and Opportunity Scoring model.
