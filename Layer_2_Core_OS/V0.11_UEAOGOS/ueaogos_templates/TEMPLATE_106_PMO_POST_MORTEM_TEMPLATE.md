# PMO Post-Mortem Template
**Document ID:** VENUS-UEAOGOS-106
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

---

## 1. Overview & Objective
Defines standard layout and review processes for post-project reviews.

## 2. Technical Specifications & Architecture
### Post-Mortem Summary

| Project Name | Actual Cost (USD) | Actual Timeline | Key Issues Identified | Root Cause Analysis | Action Items |
|---|---|---|---|---|---|
| Auth Decoupling | 320,000 | 120 Days | IAM roles misalignment | Lack of automation | Implement automation templates |
| Analytics Launch | 475,000 | 150 Days | Database capacity limits | High read load | Implement replication clusters |

## 3. Code Fragment / Implementation Details
```yaml
post_mortem:
  project_name: 'Auth Decoupling'
  budget_variance_usd: 30000
  schedule_variance_days: 10
  key_learning: 'Automated roles validation is mandatory'
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PostMortemSchema",
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string"
    }
  },
  "required": [
    "project_name"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
Project success efficiency score:
$$SE_{project} = \frac{Value_{realized}}{Cost_{actual}} \times \frac{Time_{target}}{Time_{actual}} \ge 1.0$$

## 6. Institutional Verification Checklist

### 6.1 Pre-Execution Phase
* [ ] Collect performance reports and incident logs post-project.
* [ ] Convene post-mortem committee sync and draft root cause analysis.

### 6.2 Execution Phase
* [ ] Formulate action plans and assign owners.
* [ ] Submit post-mortem package to C-suite committee for review.

### 6.3 Post-Execution Phase
* [ ] Track action items implementation progress monthly.
* [ ] Update project templates based on findings.

### 6.4 Exception & Rollback Phase
* [ ] Halt new project initiations in affected domain if action items are neglected.
* [ ] Notify PMO Director.

## 7. Cross-References
- [105 Dependency Impact Assessment](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_105_DEPENDENCY_IMPACT_ASSESSMENT.md)
- [107 Portfolio Rebalancing Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_107_PORTFOLIO_REBALANCING_SPEC.md)
