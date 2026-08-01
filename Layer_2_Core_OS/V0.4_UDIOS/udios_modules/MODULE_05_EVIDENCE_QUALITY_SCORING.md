# Module 05 — Evidence Quality Scoring

## 1. Context & Strategy

### 1.1 Purpose
The Evidence Quality Scoring module evaluates the credibility of aggregated data. It mathematically discounts bias, marketing hype, and unsubstantiated developer opinions.

### 1.2 Philosophy
Not all data is created equal. A peer-reviewed ACM paper or a local Docker benchmark run carries more validity than a vendor's blog post or a GitHub stars count. We weight evidence to establish objective truth.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Compiled evidence profiles (from Module 04).
*   **Outputs**: Weighted Evidence Scorecard and overall Evidence Credibility Index (ECI).

### 2.2 Quality Source Weights
Every source type is assigned a base value:
*   **Academic Paper (95)**: Peer-reviewed, verified methodologies.
*   **Official Documentation (90)**: Provider contracts, API definitions.
*   **Production Benchmark (88)**: Local, reproducible load testing results.
*   **GitHub Issues (72)**: Real-world developer error traces and bugs.
*   **StackOverflow (55)**: Community consensus, code examples.
*   **Marketing Material (20)**: Pricing pages, landing claims.
*   **Individual Opinion (5)**: Personal preferences, unbacked comments.

---

## 3. Operational Algorithm & Scoring

### 3.1 Evidence Credibility Index (ECI) Formula
The ECI represents the weighted average quality of the evidence pool:

\[ECI = \frac{\sum_{i=1}^{n} (Source\_Weight_i \times Relevance\_Score_i)}{\sum_{i=1}^{n} Relevance\_Score_i}\]

Where:
*   **Source Weight (5-95)**: Based on the source type taxonomy.
*   **Relevance Score (1-5)**: Assesses how closely the evidence matches the target system's use case (1: General topic. 5: Identical database engine and workload profile).

### 3.2 Threshold Gates
*   **ECI >= 75**: High-quality evidence. Proceed directly to trade-off analysis.
*   **ECI < 75**: Weak evidence base. Flags a process exception requiring new benchmarks or additional spikes.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Evidence Quality Matrix
```markdown
### 1. Quality Summary
*   **Decision ID**: DEC-[UUID]
*   **ECI Score**: [0.0 - 100.0]

### 2. Quality Breakdown
| Evidence ID | Source Type | Base Weight | Relevance (1-5) | Weighted Score |
|---|---|---|---|---|
| EVD-01 | Academic | 95 | 4 | 380 |
| EVD-02 | Marketing| 20 | 5 | 100 |
```

### 4.2 Checklist
*   [ ] Categorized every evidence entry.
*   [ ] Checked relevance ratings against local workloads.
*   [ ] Calculated ECI score.
*   [ ] Flagged low-evidence items.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read source URLs and headers, identifying source types.
2.  **Evaluate**: Assign relevance ratings. If relevance > 3, ensure a direct excerpt is saved in the record.

### 5.2 Common Anti-patterns
*   *The Hype Trap*: Accepting a vendor's "5x faster than postgres" marketing slide as valid benchmark evidence.

### 5.3 Exit Criteria
*   ECI score calculated and **ECI >= 75 gate verified**.
*   Proceed to **Module 06: Assumption Validation**.
