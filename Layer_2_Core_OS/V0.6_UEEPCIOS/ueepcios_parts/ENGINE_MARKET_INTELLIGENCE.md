# Engine: Market Intelligence

## 1. Context & Strategy

### 1.1 Purpose
The Market Intelligence Engine aggregates external market size datasets, technology adoption trends, and regional opportunities to calculate TAM/SAM/SOM indices.

### 1.2 Philosophy
Never guess market size. Decisions must be backed by official sector statistics, comparable SaaS earnings filings, and verified industry databases.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Sector keyword inputs, target regional profiles.
*   **Outputs**: TAM/SAM/SOM Analysis Report with assigned Market UUID.

### 2.2 Calculations Pipeline
```
                          [Sector Keyword Ingest]
                                     │
                        [Fetch Industry Benchmarks]
                                     │
                     [Calculate TAM / SAM / SOM Values]
```

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Calculated global addressable market ceiling (TAM).
*   [ ] Checked regional compliance boundaries.
*   *Exit Criteria*: Market Opportunity Dossier populated and verified.
