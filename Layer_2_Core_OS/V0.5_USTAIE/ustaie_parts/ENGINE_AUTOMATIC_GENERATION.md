# Engine: Automatic Architecture Generation

## 1. Context & Strategy

### 1.1 Purpose
The Automatic Architecture Generation engine transforms high-level concept prompts (e.g. "Build Uber for Ambulances") into structured blueprints, context maps, schemas, and API definitions automatically.

### 1.2 Philosophy
Do not start with code. Standardize system layout generation to ensure that every generated service, database table, and queue maps back to verified domain contexts and security boundaries.

---

## 2. Ingestion Parameters & Pipeline

### 2.1 Inputs & Outputs
*   **Inputs**: High-level system prompt, target scale profile, constraints list.
*   **Outputs**: Complete System Architecture Package (Context Maps, Schemas, API specs, deployment scripts).

### 2.2 Generation Pipeline
```
                          [Ingest Prompt / Scope]
                                     │
                        [Extract Domain Contexts]
                                     │
                       [Map Database Schemas & APIs]
                                     │
                      [Generate Deployment Topology]
```

---

## 3. Standard Layout Specifications
Every generated architecture must produce:
*   **Context Map**: Diagram detailing boundaries and communication directions.
*   **API Specification**: OpenAPI 3.0 specification for all public interfaces.
*   **Database Schema**: DDL scripts specifying tables, foreign keys, and indexes.

---

## 4. Generation Checklist & Exit Criteria
*   [ ] Created Context Map.
*   [ ] Generated DDL database schema scripts.
*   [ ] Wrote OpenAPI definitions.
*   [ ] Checked configuration files for security keys.
*   *Exit Criteria*: All 3 schema files generated without placeholders.
