# Severity Level Triage Runbook
**Document ID:** VENUS-USPTCROS-122
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Establishes a standardized triage matrix to classify security incidents based on severity, urgency, and operational impact.

## 2. Technical Specifications & Architecture
### Triage Level Mapping

| Severity Class | Criteria | System Availability Impact | Target Containment SLA |
| --- | --- | --- | --- |
| P1 | Potential data breach / service outage | Critical outage | 30 Minutes |
| P2 | Degraded operations / potential system compromise | Partially degraded | 2 Hours |
| P3 | Non-critical component compromise | Fully operational | 12 Hours |
| P4 | Minor warnings or scan alerts | No degradation | 48 Hours |

## 3. Code Fragment / Implementation Details
```python
def evaluate_severity(impact_score, urgency_score):
    # Calculate matrix score [1 to 16]
    matrix_value = impact_score * urgency_score
    if matrix_value >= 12:
        return "P1"
    elif matrix_value >= 8:
        return "P2"
    elif matrix_value >= 4:
        return "P3"
    else:
        return "P4"

if __name__ == "__main__":
    # Test high impact, high urgency triage
    print("Severity Rating:", evaluate_severity(4, 3))
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TriageAssessment",
  "type": "object",
  "properties": {
    "impact_score": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4
    },
    "urgency_score": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4
    },
    "severity_result": {
      "type": "string",
      "enum": [
        "P1",
        "P2",
        "P3",
        "P4"
      ]
    }
  },
  "required": [
    "impact_score",
    "urgency_score",
    "severity_result"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$SeverityLevel = \lceil Impact \times Urgency \rceil$$

## 6. Institutional Verification Checklist
* [ ] Identify the systems and components impacted by the incident.
* [ ] Assess the potential exposure of personal data or credentials.
* [ ] Trigger escalation protocols based on the severity level.
* [ ] Verify backup system status in case failover is required.

## 7. Cross-References
- [Incident Response Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INCIDENT_RESPONSE_PLAN.md)
- [Incident Timeline Scribe Log](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INCIDENT_TIMELINE_SCRIBE_LOG.md)
- [Crisis Management Command Structure](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CRISIS_MANAGEMENT_COMMAND_STRUCTURE.md)
