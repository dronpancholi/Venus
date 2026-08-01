# Template: Architecture Review Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Review ID**: REV-ARC-[UUID]
*   **Audit Date**: [Date]
*   **Lead Reviewer**: [Name]

---

## 2. Review Verdict Summary
*Provide a concise summary of the architectural audit findings.*

---

## 3. Systems Design Compliance Scorecard

| Audited Dimension | Audit Metric / Criteria | Score (1-5) | Status |
|---|---|---|---|
| **Scalability** | Support for concurrent connections > 5,000 | 4 | **PASS** |
| **Security** | Zero trust subnet isolation verified | 5 | **PASS** |
| **Maintainability** | Logical complexity index <= 15.0 | 4 | **PASS** |
| **Redundancy** | Multi-AZ database failover configured | 5 | **PASS** |

*   **Calculated Score**: **4.5 / 5.0**
*   **Status**: **APPROVED FOR CODING**

---

## 4. Required Action Items
*List modifications required prior to launching production servers.*

*   *Action Item 1*: Configure auto-scaling rules on AWS Fargate nodes.
*   *Action Item 2*: Enforce database table isolation rules between Auth and Billing services.
