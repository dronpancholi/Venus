# Stage 1 — Problem Discovery

## 1. Governance & Rationale

### 1.1 Why It Exists
Most technology failures are not caused by incorrect code, but by building a correct solution to the wrong problem. Stage 1 forces the organization to dissect the initial concept, separate superficial symptoms from systemic causes, and verify that the target problem is real, painful, and economically worth solving.

### 1.2 What Questions It Answers
*   What is the observed pain point, and who experiences it?
*   Is the observed issue a symptom, a direct cause, a root cause, or a systemic loop?
*   What are the underlying physical, economic, or behavioral constraints that prevent a simple solution?
*   What job is the user trying to hire a product to do, and why do current workarounds fail?

### 1.3 What Decisions Depend on It
*   **Go/No-Go**: Should we initiate market and technological research, or abandon the concept immediately?
*   **Scope Definition**: What are the boundaries of the problem space that our system must address?

### 1.4 What Happens if It Is Skipped
Skipping Stage 1 leads to **Solution-in-Search-of-a-Problem (SSOP) Syndrome**. The engineering organization will build high-performance, scalable software that users ignore because it does not resolve their primary operational bottlenecks or align with their workflows.

### 1.5 What Evidence Is Required Before Proceeding
*   Direct observation logs or transcripts of stakeholder interviews (minimum of 10 primary targets).
*   A mapped sequence of the current failure loop.
*   A completed Jobs-to-be-Done (JTBD) profile.

---

## 2. Operational Methodology

### 2.1 The Symptom-to-System Decomposition Framework
To identify the real problem, we classify findings into four layers:

```
┌────────────────────────────────────────────────────────┐
│  SYMPTOM: The visible manifestation of pain            │
│  (e.g., "Our outreach emails are converting poorly")   │
└───────────────────────────┬────────────────────────────┘
                            │ (Ask: Why?)
                            ▼
┌────────────────────────────────────────────────────────┐
│  DIRECT CAUSE: The immediate technical trigger         │
│  (e.g., "The emails contain generic placeholder text") │
└───────────────────────────┬────────────────────────────┘
                            │ (Ask: Why?)
                            ▼
┌────────────────────────────────────────────────────────┐
│  ROOT CAUSE: The underlying operational block          │
│  (e.g., "Scraping pipeline doesn't extract USP context")│
└───────────────────────────┬────────────────────────────┘
                            │ (Ask: Why?)
                            ▼
┌────────────────────────────────────────────────────────┐
│  SYSTEMIC CAUSE: Feedback loops, incentives, limits    │
│  (e.g., "Engineering optimized for scraping speed      │
│   over semantic relevance; no feedback loop from CRM") │
└────────────────────────────────────────────────────────┘
```

### 2.2 Core Tools & Techniques

#### 2.2.1 Five Whys Analysis
For every observed symptom, execute a recursive "Why" tree. Do not stop at the first technical explanation; continue until you uncover organizational, systemic, or behavioral causes.

#### 2.2.2 First-Principles Decomposition
Break down the problem into its fundamental truths:
*   Physical limits (e.g., bandwidth, latency, compute thresholds).
*   Economic limits (e.g., cost per API call, user lifetime value constraints).
*   Logical limits (e.g., computability, NP-hard constraints).

#### 2.2.3 Jobs-to-be-Done (JTBD) Framing
Define the problem through the lens of progress:
*   *When* [Situation], *I want to* [Motivation], *so I can* [Expected Outcome].
*   Analyze the forces: **Push** of the current situation vs. **Pull** of the new solution; **Anxiety** of the new vs. **Habit** of the old.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Initial project concept brief (1-sentence description).
*   Target user segment definitions.
*   Raw operational artifacts (emails, spreadsheets, database logs of current workarounds).

### 3.2 Outputs
*   **The Verified Problem Statement**: A single sentence defining the root cause.
*   **Stakeholder Interview Logs**: Mapped user frustrations and workflow logs.
*   **Systemic Failure Loop Diagram**: Mermaid diagram of the existing feedback loop.

---

## 4. Reusable Checklists & Templates

### 4.1 Problem Discovery Checklist
*   [ ] Conducted at least 10 stakeholder interviews.
*   [ ] Executed 5 Whys analysis on all primary symptoms.
*   [ ] Mapped the current workflow, highlighting all manual friction points.
*   [ ] Identified and documented physical or economic constraints.
*   [ ] Mapped the systemic feedback loop causing the symptom.

### 4.2 Template: The 5 Whys & Systemic Mapping
```markdown
### 1. The Symptom
*Observed visible pain*: [State the symptom]

### 2. The Five Whys Chain
* Why 1: [Immediate technical trigger]
* Why 2: [Operational blocker]
* Why 3: [Architecture or process limitation]
* Why 4: [Incentive or resource constraint]
* Why 5: [Root cause / fundamental truth]

### 3. Systemic Loop Description
[Explain how the incentives, tools, and processes interact to lock this problem in place.]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Problem Maturity Index (PMI)
Evaluate the problem on a 1-5 scale across four vectors:

| Vector | Description | Score (1-5) |
|---|---|---|
| **Pain Level** | 1: Minor annoyance. 5: Business-critical operational blocker. | |
| **Solve Value** | 1: Low willingness-to-pay. 5: High economic return on resolution. | |
| **Clarity** | 1: Diffuse symptoms. 5: Root cause is clearly isolated and targetable. | |
| **Feasibility** | 1: Violates physical/economic limits. 5: Solvable within constraints. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Problem Maturity Index score **≥ 16 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 2: Market Intelligence**.
*   **Fail**: Return to user discovery or abort.
