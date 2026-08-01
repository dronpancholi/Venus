# Subsidiary Governance Charter
**Document ID:** VENUS-UEAOGOS-028
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

---

## 1. Overview & Objective
Establishes operational and legal control guidelines for subsidiary and regional companies under the parent organization.

## 2. Technical Specifications & Architecture
### Subsidiary Registry

| Entity Name | Jurisdiction | Parent Ownership Share | Managing Director | Primary Compliance Officer |
|---|---|---|---|---|
| Venus UK Ltd | United Kingdom | $100\%$ | VP UK Ops | UK Legal Officer |
| Venus EU GmbH | Germany | $100\%$ | VP EU Ops | Germany Legal Officer |

## 3. Code Fragment / Implementation Details
```yaml
subsidiary:
  name: 'Venus UK Ltd'
  jurisdiction: 'United Kingdom'
  ownership_share: 1.0
  reporting_frequency: 'Monthly'
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SubsidiarySchema",
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "ownership_share": {
      "type": "number"
    }
  },
  "required": [
    "name",
    "ownership_share"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
Entity integration level factor:
$$IL = \sum_{i=1}^{n} w_i \times Policy_{aligned\_i}$$

## 6. Institutional Verification Checklist

### 6.1 Pre-Execution Phase
* [ ] Incorporate subsidiary according to target jurisdiction laws.
* [ ] Appoint board and managing directors.

### 6.2 Execution Phase
* [ ] Implement parent company governance policies.
* [ ] Audit subsidiary operations against legal rules.

### 6.3 Post-Execution Phase
* [ ] Submit tax filings and statutory filings to regional regulators.
* [ ] Review subsidiary metrics at parent board meetings.

### 6.4 Exception & Rollback Phase
* [ ] Suspend subsidiary operations in case of compliance breach.
* [ ] Initiate local forensic review and restructure leadership.

## 7. Cross-References
- [027 Delegation Of Authority Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_027_DELEGATION_OF_AUTHORITY_MATRIX.md)
- [029 Inter Entity Service Agreement](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/TEMPLATE_029_INTER_ENTITY_SERVICE_AGREEMENT.md)
