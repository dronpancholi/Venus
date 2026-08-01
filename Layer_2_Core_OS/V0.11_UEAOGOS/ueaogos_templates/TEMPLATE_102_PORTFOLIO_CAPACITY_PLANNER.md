# Portfolio Capacity Planner
**Document ID:** VENUS-UEAOGOS-102
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

---

## 1. Overview & Objective
Delineates standard methods for resource capacity planning, skill utilization mapping, and resource gaps tracking.

## 2. Technical Specifications & Architecture
### Capacity Planning Summary

| Resource Class | Total Capacity (FTE) | Allocated Capacity | Unallocated | Gap/Deficit | Target Hires |
|---|---|---|---|---|---|
| Backend SRE | 12.0 | 11.5 | 0.5 | 0.0 | 2 |
| QA Engineer | 8.0 | 9.0 | -1.0 | 1.0 | 1 |

## 3. Code Fragment / Implementation Details
```yaml
capacity_plan:
  resource_class: 'Backend SRE'
  capacity_fte: 12.0
  allocated_fte: 11.5
  unallocated_fte: 0.5
  gap_fte: 0.0
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CapacityPlannerSchema",
  "type": "object",
  "properties": {
    "resource_class": {
      "type": "string"
    }
  },
  "required": [
    "resource_class"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
Capacity utilization score formula:
$$\rho_{cap} = \frac{Capacity_{allocated}}{Capacity_{total}} \le 0.90$$

## 6. Institutional Verification Checklist

### 6.1 Pre-Execution Phase
* [ ] Review resource capacity requirements across active projects.
* [ ] Identify resource gaps and draft hiring plans.

### 6.2 Execution Phase
* [ ] Validate hiring plans with CFO and CPO.
* [ ] Publish capacity mapping updates monthly.

### 6.3 Post-Execution Phase
* [ ] Track hiring pipeline metrics monthly.
* [ ] Update capacity variables based on project scope changes.

### 6.4 Exception & Rollback Phase
* [ ] Halt new project approvals if unallocated capacity score reaches 0.0.
* [ ] Notify PMO Director.

## 7. Cross-References
- [101 Pmo Weekly Status Composer](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_101_PMO_WEEKLY_STATUS_COMPOSER.md)
- [103 Project Cost Variance Log](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_103_PROJECT_COST_VARIANCE_LOG.md)
