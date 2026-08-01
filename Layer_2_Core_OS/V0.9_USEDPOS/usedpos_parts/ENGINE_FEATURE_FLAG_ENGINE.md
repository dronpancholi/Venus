# Engine: Feature Flag Engine

## 1. Context & Strategy

### 1.1 Purpose
The Feature Flag Engine manages the runtime state, cohort target selection, and dynamic evaluation of software flags. It supports decoupling release cycles from code deployments, enabling safe canary releases, A/B testing, and instant operational circuit-breaking.

### 1.2 Philosophy
Flags must not degrade service performance. Evaluators must resolve decisions locally in sub-millisecond times, avoiding inline remote database queries during execution.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: User context (ID, group, tenant), system state, flag key, fallback defaults, and cohort mapping models.
*   **Outputs**: Evaluation Decision (boolean or string variant value) and evaluation path metrics for analytics telemetry.

### 2.2 Evaluation Pipeline
```
[Ingest Context & Key] ──► [Lookup Cached Rule Set] ──► [Hash User ID for Canary Allocation] ──► [Evaluate Rules] ──► [Return Decision]
```

---

## 3. Algorithmic Checks & Computations

### 3.1 Consistent Hash Ring Cohort Assignment
To prevent user segment drift when evaluating percentage-based rollout rollouts, the engine hashes the user ID ($U_{id}$) combined with the flag key ($F_{key}$):

$$\text{Hash} = \text{Murmur3}(U_{id} + F_{key})$$

$$\text{Normalized Value} = \frac{\text{Hash}}{\text{MaxHash}} \times 100$$

*   If $\text{Normalized Value} \le \text{Rollout Percentage}$, return `true` (variant active); else return `false` (baseline active).
*   This guarantees that a given user consistently resolves to the same variant without requiring storage of state mappings.

### 3.2 Evaluation Performance Target
To avoid impacting request paths, the maximum execution time ($T_{eval}$) for nested flag queries must be:

$$T_{eval} = T_{lookup} + T_{hash} \le 1.0\text{ms}$$

Using local memory lookups, $T_{lookup} \approx 0.05\text{ms}$ and $T_{hash} \approx 0.02\text{ms}$.

---

## 4. Feature Flag Definition Schema
Flags must declare active configurations using this validation structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FeatureFlagDefinition",
  "type": "object",
  "properties": {
    "flagKey": { "type": "string", "pattern": "^[a-z0-9.-]+$" },
    "enabled": { "type": "boolean" },
    "rolloutPercent": { "type": "integer", "minimum": 0, "maximum": 100 },
    "targetingRules": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "attribute": { "type": "string" },
          "operator": { "type": "string", "enum": ["EQUALS", "IN", "CONTAINS"] },
          "values": { "type": "array", "items": { "type": "string" } }
        },
        "required": ["attribute", "operator", "values"]
      }
    }
  },
  "required": ["flagKey", "enabled", "rolloutPercent"]
}
```

---

## 5. Reusable Checklist & Exit Criteria
*   [ ] Checked that flag evaluation runs completely in local memory without remote lookups.
*   [ ] Verified that Murmur3 hashing guarantees uniform cohort distribution.
*   [ ] Confirmed fallback default variables are declared for every evaluation call.
*   [ ] Checked that flags older than 30 days are flagged in the clean-up registry.
*   *Exit Criteria*: Local flag evaluation resolves in $\le 1\text{ms}$ with zero runtime memory allocations.
