# Module 04 — Evidence Collection

## 1. Context & Strategy

### 1.1 Purpose
The Evidence Collection module automates the retrieval of objective, external data to support technical proposals. It aggregates evidence from API docs, codebases, benchmarks, academic papers, and Git issues.

### 1.2 Philosophy
Decisions must be based on data, not opinions. We prioritize empirical benchmark results, official provider contracts, and peer-reviewed studies over marketing slides or developer preference.

---

## 2. Retrieval Parameters & Sources

### 2.1 Inputs & Outputs
*   **Inputs**: DIR and target entity names (e.g., "Postgres", "Elasticsearch", "Llama-3").
*   **Outputs**: Evidence Repository folder containing saved reference docs, links, and benchmarks.

### 2.2 Evidence Source Matrix
*   *Academic*: Google Scholar / arXiv papers.
*   *Technical*: Official documentation, GitHub issues, schema definitions.
*   *Operational*: Self-hosted benchmark metrics, load test logs.
*   *Anecdotal*: StackOverflow threads, developer forums.

---

## 3. Operational Algorithm & Retrieval Strategy

### 3.1 Automated Retrieval Protocol
When a new DEC-[UUID] is initialized, the collection agent runs the following pipeline:

```
                            [DEC-[UUID] Received]
                                      │
                         [Identify Target Entities]
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
   [Scan Local Github]       [Query Scholar/arXiv]      [Fetch Official Docs]
            │                         │                         │
            ▼                         ▼                         ▼
   [Locate Open Issues]      [Fetch Performance Papers]   [Parse Pricing & SLAs]
```

### 3.2 Evidence Verification Check
All gathered evidence must be stamped with:
*   *URL / DOI*: Clear traceability vector.
*   *Retrieved Date*: Verification timestamp to track API changes.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Evidence Register Entry
```markdown
### 1. Evidence Profile: EVD-[UUID]
*   **Source URL**: [Link]
*   **Category**: Academic / Documentation / Benchmark
*   **Relevance Rating**: [1-5]
*   **Key Extract**: "[Paste verified quote or benchmark table here]"
```

### 4.2 Collection Checklist
*   [ ] Identified all external software or vendor names.
*   [ ] Checked official provider SLAs and licensing terms.
*   [ ] Query-searched GitHub issues for known crashes.
*   [ ] Stored local markdown or PDF copies of evidence references.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Retrieve**: Execute web search spikes targeting the entity names + keywords "benchmark", "latency", "issue".
2.  **Filter**: Exclude marketing/pricing landing pages unless specifically evaluating financial parameters.

### 5.2 Common Anti-patterns
*   *The Confirmative Bias Search*: Intentionally querying only positive reviews of a preferred technology (e.g. searching "why redis is the best" instead of "redis latency spikes clustering failures").

### 5.3 Exit Criteria
*   Evidence Repository populated with at least **3 separate verified sources**.
*   Proceed to **Module 05: Evidence Quality Scoring**.
