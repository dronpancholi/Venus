# Module 07 — Alternative Generation

## 1. Context & Strategy

### 1.1 Purpose
The Alternative Generation Engine prevents default-bias or single-solution fixation. When a specific tool or architecture is proposed, the engine expands the choice vector to explore alternatives, detailing the rationale behind each.

### 1.2 Philosophy
Defaulting to a familiar stack is a primary source of architectural mismatch. If a team proposes "Postgres", we explore standard relational, document, column-family, and memory alternatives to verify PostgreSQL is indeed the optimal choice.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Proposed action/technology target (from DIR).
*   **Outputs**: Expanded Alternative Vectors Directory listing candidate solutions.

### 2.2 Category Taxonomies
Alternatives are generated across three tiers:
1.  **Direct Competitors**: Swappable tools (e.g. Postgres vs. MySQL).
2.  **Structural Variants**: Different database models (e.g. Postgres vs. MongoDB).
3.  **Paradigm Shifts**: Alternative process design (e.g. Database storage vs. local file system storage).

---

## 3. Operational Algorithm & Selection Matrix

### 3.1 Alternative Generation Algorithm
The engine scans a pre-loaded ontology to match proposed technologies to their family tree:

```
                            [Target Entity: Postgres]
                                       │
                              [Query Stack Map]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
  [Direct Competitors]       [Structural Variants]        [Paradigm Shifts]
   - MySQL                    - MongoDB                    - S3 Storage
   - SQLite                   - Cassandra                  - Flat Files
```

### 3.2 Required Evidence
For every generated alternative, the engine must fetch:
*   *License Type*: Open source (MIT/Apache) vs. Proprietary.
*   *Operational Cost*: Average cloud compute cost comparison.

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Alternative Matrix
```markdown
### 1. Alternative Vectors for [Proposed Entity]
*   **Decision ID**: DEC-[UUID]

| Target Option | Category | Primary Strength | Primary Weakness |
|---|---|---|---|
| Postgres (Proposed)| Relational DB | Strong ACID, SQL support | Scalability limits |
| MongoDB | Document DB | Schema flexibility | Weak ACID joints |
| SQLite | Embedded DB | Zero config, zero latency | Concurrency limits |
```

### 4.2 Checklist
*   [ ] Checked target option against direct competitors.
*   [ ] Checked database model variants.
*   [ ] Evaluated structural changes.
*   [ ] Saved alternative matrix to the repository.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Scan**: Match target technology to its parent class in the stack database.
2.  **Generate**: Enforce generation of at least 3 distinct candidates. If fewer, flag to search the web for related packages.

### 5.2 Common Anti-patterns
*   *The Strawman Alternative*: Generating weak, unusable options (e.g. comparing Postgres to an Excel sheet) to make the preferred solution look superior.

### 5.3 Exit Criteria
*   Alternative Vectors Directory populated with **3 valid candidate solutions**.
*   Proceed to **Module 08: Trade-off Analysis**.
