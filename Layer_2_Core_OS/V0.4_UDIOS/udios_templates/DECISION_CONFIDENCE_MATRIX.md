# Template: Decision Confidence Matrix

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Decision ID**: DEC-[UUID]
*   **Validation Date**: [Date]
*   **Evaluator**: [Name]

---

## 2. Confidence Scoring Breakdown
*This scorecard calculates the overall confidence rating by tracking the evidence quality and validation rates.*

| Indicator | Metric Description | Current Value | Weighted Score |
|---|---|---|---|
| **ECI Score** | Quality weight of evidence pool | [e.g., 85.0%] | 34.0 / 40.0 |
| **Assumption Validation** | Percent of assumptions verified | [e.g., 90.0%] | 27.0 / 30.0 |
| **Risk Mitigation** | Percent of high risks mitigated | [e.g., 100.0%] | 30.0 / 30.0 |
| **Overall Confidence** | Calculated synthesis rating | **91.0%** | **91.0 / 100.0** |

---

## 3. Critical Validation Spikes History
*Track the status of the validation tests completed to verify critical assumptions.*

*   **Spike ID**: SPK-01 (Assumption: Redis cluster throughput capacity)
    *   *Test script*: `pytest tests/spikes/test_redis_write.py`
    *   *Result*: Target met. Under load of 5,000 req/sec, Redis CPU load remained below 40%.
    *   *Status*: **VALIDATED**

*   **Spike ID**: SPK-02 (Assumption: LLM pricing models)
    *   *Status*: **VALIDATED**
