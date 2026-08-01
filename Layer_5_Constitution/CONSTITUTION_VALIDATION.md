# PROJECT VENUS — CONSTITUTION: VALIDATION & ENFORCEMENT

**Version**: 1.0  
**Inherits**: UVCOS.md (Layer 5 Constitution)

---

## 1. Validation Gates

| Gate ID | Name | Tool | Scope | Phase |
|---------|------|------|-------|-------|
| G1 | Schema Validation | `validate_schemas.py` | JSON Schema files | Pre-push |
| G2 | Naming Convention | `check_naming.py` | All files | Pre-commit |
| G3 | Reference Integrity | `check_references.py` | All markdown links | Pre-merge |
| G4 | Template Quality | `check_templates.py` | Template files | Pre-release |
| G5 | Catalog Freshness | `generate_catalog.py` | Catalog vs repo | Pre-merge |
| G6 | Graph Integrity | `check_references.py` | Dependency graph | Weekly |

---

## 2. Gate Thresholds

| Gate | Required Pass Rate | Failure Action |
|------|-------------------|----------------|
| G1 | 100% (all schemas valid) | Block commit |
| G2 | 100% (all files conform) | Block commit |
| G3 | 100% (all links resolve) | Block merge |
| G4 | 95% (templates pass) | Warning on merge |
| G5 | 100% (catalog matches repo) | Block merge |
| G6 | No orphaned nodes | Weekly report |

---

## 3. Repository Validation

### 3.1 Structural Rules

1. Every OS version must have exactly one root markdown file matching `V0.X_NAME.md`
2. Every parts directory must contain only `PART_NN_*.md` and `ENGINE_*.md` files
3. Every templates directory must contain only template files
4. No file may exist outside a recognized directory structure
5. Every file must have an entry in `catalog.json`

### 3.2 Content Rules

1. No file may contain unresolved `schema://` references
2. All cross-references to other Venus files must be relative markdown links
3. Template files must not contain `[e.g. ...]` or `[insert ...]` patterns
4. Every engine file must reference at least one part or template
5. Every part must be consumed by at least one engine or template

### 3.3 Integrity Rules

1. The dependency graph must be acyclic (no circular dependencies)
2. Every node in the knowledge graph must be reachable from Layer 1
3. Layer isolation: Layer N files may reference Layer N-1 but not Layer N+1 directly

---

## 4. Enforcement Automation

```python
# Governance enforcement (conceptual)
class VenusEnforcementEngine:
    gates = [G1, G2, G3, G4, G5, G6]

    def check_pre_commit(self, changed_files):
        return all(gate.run(changed_files) for gate in self.gates if gate.phase == "pre-commit")

    def check_pre_merge(self, changed_files):
        return all(gate.run(changed_files) for gate in self.gates if gate.phase == "pre-merge")

    def weekly_audit(self):
        for gate in self.gates:
            if gate.phase == "weekly":
                gate.run()
                gate.report()
```

---

## 5. Non-Compliance Handling

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | Constitutional violation | Immediate revert, council notification |
| High | Schema violation, broken reference | Block merge, author notified |
| Medium | Naming violation, template warning | Warning, 7-day fix window |
| Low | Catalog staleness | Automated regeneration |
