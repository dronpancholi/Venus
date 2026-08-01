# USPTCROS Capability Engine: RAG Poisoning Detector
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Audits document data sources, chunk definitions, and embeddings stored in Vector Databases to detect injected or poisoned content.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: RAG pipeline documents and text chunks.
- **Input Source**: Vector database embeddings and coordinates.
- **Input Source**: Similarity distribution statistics from clean corpora.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Vector Health report listing outlier document chunks.
- **Output Artifact**: List of quarantined documents to be removed from vector database index.
- **Output Artifact**: JSON-structured anomaly log listing data violations.

### 1.3 Integration & Automation Triggers
- Runs during document ingestion phases.
- Audits vector databases weekly to identify anomalies.
- Integrates with SIEM to trace sources of poisoned documents.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$P_{Poison} = \max(Dist_{Semantic}(D_i, Corpus_{Centroid}))$$

### 2.2 Variable Definitions
- $Dist_{Semantic}$: Cosine distance between document embeddings and average centroid.
- $D_i$: Embedding vector of document chunk i.
- $Corpus_{Centroid}$: Centroid vector of validated, clean document corpus.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Retrieve vector coordinates of ingested documents.
2. Calculate average corpus centroid value.
3. Compute cosine distance metrics for all nodes.
4. Flag outlier documents that fall outside distance thresholds.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RagDetectorConfig",
  "type": "object",
  "properties": {
    "outlierThreshold": {
      "type": "number"
    },
    "scanBatchSize": {
      "type": "integer"
    },
    "autoQuarantine": {
      "type": "boolean"
    }
  },
  "required": [
    "outlierThreshold",
    "scanBatchSize",
    "autoQuarantine"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify connection to vector databases.
  - [ ] Verify semantic centroid models are active.
- [ ] **Execution & Scan Verification**:
  - [ ] Scan data blocks for anomalous text structures.
  - [ ] Verify document metadata profiles match verified origins.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Remove anomalous documents from active indexes.
  - [ ] Initiate source verification workflows for quarantined data.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Restore original vector databases using verified backups.
  - [ ] Rebuild vector indexes from clean source documents.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_PROMPT_INJECTION_SCANNER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_PROMPT_INJECTION_SCANNER.md)
  - [ENGINE_MODEL_THEFT_RISK_ANALYZER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_MODEL_THEFT_RISK_ANALYZER.md)
  - [ENGINE_AI_RED_TEAM_ENGINE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_AI_RED_TEAM_ENGINE.md)
- **Output Templates**:
  - [DATA_CLASSIFICATION_MATRIX.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DATA_CLASSIFICATION_MATRIX.md)
