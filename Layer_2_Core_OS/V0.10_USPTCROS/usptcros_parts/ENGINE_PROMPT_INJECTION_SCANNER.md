# USPTCROS Capability Engine: Prompt Injection Scanner
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Detects direct and indirect prompt injection vectors, system prompt overrides, and escape codes in inputs to LLM models.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Inbound user prompts and query variables.
- **Input Source**: System prompt configurations and guardrails.
- **Input Source**: Vector databases of known jailbreak patterns.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: Prompt Safety audit report detailing injection indicators.
- **Output Artifact**: Filtered prompt payload for LLM consumption.
- **Output Artifact**: Alert telemetry for prompt override attempts.

### 1.3 Integration & Automation Triggers
- Runs inline inside API Gateways before LLM model calls.
- Funnels prompt outputs to moderation systems.
- Blocks queries containing high-risk injection keywords.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$PI_{Score} = \max(Similarity_{Heuristic}, Prob_{Model})$$

### 2.2 Variable Definitions
- $Similarity_{Heuristic}$: Similarity rating (0.0 to 1.0) compared to known jailbreak databases.
- $Prob_{Model}$: Probability score (0.0 to 1.0) of injection intent classification.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Clean and tokenize input prompt text.
2. Calculate similarity scores against database of jailbreak templates.
3. Run local classification model to evaluate intent of prompt.
4. Sum findings to compute the final prompt safety score. Block if score exceeds 0.7.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PromptScanConfig",
  "type": "object",
  "properties": {
    "maxPromptLength": {
      "type": "integer"
    },
    "similarityThreshold": {
      "type": "number"
    },
    "blocklistPatterns": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "maxPromptLength",
    "similarityThreshold",
    "blocklistPatterns"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Update the vector database of jailbreak strings.
  - [ ] Verify API connection to safety classification models.
- [ ] **Execution & Scan Verification**:
  - [ ] Compare incoming prompts to pattern lists.
  - [ ] Analyze input structure for escape characters and special tokens.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Filter out injection keywords before forwarding to LLM models.
  - [ ] Send alerts to the safety dashboard when injection attempts are detected.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Reject user requests if safety scores exceed block thresholds.
  - [ ] Restore default system prompts to protect system configurations.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_RAG_POISONING_DETECTOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_RAG_POISONING_DETECTOR.md)
  - [ENGINE_JAILBREAK_SIMULATOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_JAILBREAK_SIMULATOR.md)
  - [ENGINE_AI_RED_TEAM_ENGINE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_AI_RED_TEAM_ENGINE.md)
- **Output Templates**:
  - [SECURITY_BOUNDARY_VERIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURITY_BOUNDARY_VERIFICATION.md)
