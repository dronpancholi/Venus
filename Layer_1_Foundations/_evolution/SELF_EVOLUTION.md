# PROJECT VENUS — SELF-EVOLUTION FRAMEWORK

**Version**: 1.0  
**Purpose**: Automated structural improvement, deduplication, consolidation, and migration.

---

## 1. Evolution Loops

```
┌─────────────────────────────────────────────────────────┐
│                   Self-Evolution Loop                     │
│                                                           │
│  [Trigger] → [Analysis] → [Proposal] → [Validation]      │
│      ↑                                        │          │
│      └──────── [Enactment] ←─ [Approval] ←───┘          │
└─────────────────────────────────────────────────────────┘
```

### 1.1 Trigger Sources
| Source | Frequency | Description |
|--------|-----------|-------------|
| Periodic timer | Daily | Full structural review |
| Validation failure | On event | Broken ref, schema mismatch |
| New entity added | On event | Integration check |
| Graph density threshold | Weekly | Deduplication trigger |
| Rule violation | On event | Policy violation detected |

### 1.2 Analysis Types

| Type | Input | Output |
|------|-------|--------|
| Structural | Graph | Recommendations (orphans, density, clusters) |
| Deduplication | Catalog | Duplicate candidates with similarity scores |
| Consistency | Schemas | Mismatches across type definitions |
| Coverage | Rules | Uncovered entities, missing rules |
| Migration | Version manifests | Upgrade/downgrade paths |

---

## 2. Evolution Operations

### 2.1 Deduplication
1. Group entities by name/type similarity (Levenshtein < 0.2 normalized)
2. Score pairs: filename diff + type match + content overlap
3. Propose merge: primary + secondary → consolidated
4. Update all references to merged entities

### 2.2 Consolidation
1. Detect entities with overlapping scope (shared dependencies > 50%)
2. Propose unified entity
3. Generate migration plan

### 2.3 Migration
1. Read source version manifest
2. Compute diff against target version
3. Generate migration script (entity transforms + reference updates)
4. Validate post-migration consistency

### 2.4 Pruning
1. Identify dead entities (no incoming edges, no active references)
2. Verify against retention policy (constitution, minimum age)
3. Archive to cold storage or remove

### 2.5 Refactoring
1. Detect pattern violations (e.g., circular dependencies)
2. Propose structural re-organization
3. Generate refactoring script

---

## 3. Proposal Schema

```json
{
  "id": "EVP-001",
  "type": "deduplication | consolidation | migration | pruning | refactoring",
  "source": "Analysis result ID",
  "rationale": "Why this change is needed",
  "actions": [
    { "entity": "V0.10/Architecture/...", "operation": "merge", "target": "V0.11/..." }
  ],
  "risk": "low | medium | high",
  "rollback": "Steps to undo",
  "status": "proposed | approved | enacted | rejected"
}
```

---

## 4. Execution Model

1. Evolution agent runs autonomously at scheduled intervals
2. Proposes changes via event bus to approval agent
3. Approval agent evaluates risk against constitution
4. Low-risk auto-approve; medium requires 1 confirmation; high requires N
5. Enactment agent executes approved proposals
6. Rollback plan is stored with each proposal for safety
