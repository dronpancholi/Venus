# Stage 5 — Technology Intelligence

## 1. Governance & Rationale

### 1.1 Why It Exists
Selecting a technology stack based on hype, emotional attachment, or familiarity is the leading cause of technical debt. Stage 5 mandates a cold, objective evaluation of all technical alternatives (languages, databases, frameworks, clouds, queues, vector indexes) against standardized business and operational metrics.

### 1.2 What Questions It Answers
*   What are the viable language, framework, database, and infrastructure choices?
*   What are the trade-offs of each candidate in terms of latency, scaling limits, and operating cost?
*   How mature is the ecosystem, and how easy is it to hire engineering talent for this stack?
*   What licensing, security compliance, or vendor lock-in risks exist?

### 1.3 What Decisions Depend on It
*   **Core Tech Stack Selection**: The immutable list of languages, DB schemas, frameworks, and deployment targets.
*   **Infrastructure Architecture**: Choosing serverless vs. containerized vs. bare-metal setups.
*   **Vendors & Service Providers**: Selecting primary and secondary service providers.

### 1.4 What Happens if It Is Skipped
Skipping Stage 5 leads to **Legacy Trap and Vendor Lock-in**. The company might select a database that cannot scale past 10,000 concurrent queries, forcing a migration under high load. Or it may build on top of a proprietary cloud service that inflates infrastructure costs by 10x compared to open alternatives.

### 1.5 What Evidence Is Required Before Proceeding
*   Completed Technology Evaluation Matrix with weighted scoring.
*   Benchmark results showing database write/read throughput under simulated concurrency.
*   Verified licensing profiles for all open-source packages.

---

## 2. Operational Methodology

### 2.1 The Technology Evaluation Pipeline
Every technological candidate is processed through a strict filter:

```
[Candidate Technology] ──► [Ecosystem & Hiring Check] ──► [Licensing & Security Vetting] ──► [Decision Matrix]
                                                                                                     │
                                                                                                     ▼
                                                                                            [Selected Stack]
```

### 2.2 Standard Comparison Criteria

#### 2.2.1 Operational & Performance Metrics
*   *Latency / Throughput*: Performance under high concurrent loads.
*   *Resource footprint*: CPU/RAM requirements (affects cloud hosting economics).

#### 2.2.2 Ecosystem & Risk Metrics
*   *Maturity*: Project age, release frequency, active committers.
*   *Hiring pool*: Availability of senior developers in major regions.
*   *Licensing*: AGPL, MIT, Apache 2.0 verification. Avoid AGPL in SaaS codebases unless isolated.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   System Map and Feature Scope (from Stage 3).
*   Scale and Concurrency Targets (from Stage 2).
*   Candidate technology list.

### 3.2 Outputs
*   **Technology Decision Matrix**: Side-by-side criteria evaluations.
*   **Tech Stack Specification**: Final, approved language and architecture stack.
*   **Vendor & Licensing Audit**: Vetted compliance list of third-party code.

---

## 4. Reusable Checklists & Templates

### 4.1 Technology Research Checklist
*   [ ] Researched a minimum of 3 alternatives for each layer of the stack.
*   [ ] Checked all package licenses (MIT, Apache, BSD confirmed; AGPL flagged).
*   [ ] Evaluated hiring market availability in target engineering hubs.
*   [ ] Calculated expected cloud compute and memory overhead.
*   [ ] Documented vendor lock-in exits (e.g., how to migrate from AWS DynamoDB to Postgres).

### 4.2 Template: Side-by-Side Tech Comparison
```markdown
### 1. Layer: [e.g., Relational Database]
*   **Option A**: PostgreSQL | **Option B**: MongoDB | **Option C**: AWS DynamoDB

### 2. Decision Matrix

| Metric | Option A | Option B | Option C |
|---|---|---|---|
| Latency | Excellent | Good | Excellent |
| Licensing | Open (PG) | SSPL (Flagged) | Proprietary |
| Lock-in Risk | Low | Medium | High |
| RLS Support | Native | Extension | IAM Only |
| **Weighted Total** | **9.2** | **6.5** | **7.0** |

### 3. Architectural Verdict & Rationale
[Explain why the winning option is selected and how migration is handled if it fails.]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Technology Suitability Score (TSS)
Evaluate candidates on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Ecosystem Health** | 1: Deprecated / inactive. 5: Active, backed by major organizations. | |
| **Performance** | 1: High latency / CPU footprint. 5: Fast and memory-efficient. | |
| **Lock-in Safety** | 1: Hard locked to one cloud provider. 5: Open-source, easily portable. | |
| **Hiring Pool** | 1: Rare language / scarce talent. 5: Large, active developer market. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Selected technology must score **≥ 16 / 20** in the evaluation matrix.
*   **Pass**: Proceed to **Stage 6: AI Research Framework**.
*   **Fail**: Reject candidate and evaluate alternatives.
