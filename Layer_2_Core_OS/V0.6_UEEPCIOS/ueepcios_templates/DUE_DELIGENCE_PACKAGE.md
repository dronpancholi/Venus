# Template: Due Diligence Package

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Audit ID**: DIL-PKG-[UUID]

---

## 2. Diligence Checklist Status

| Audited Section | Requirement | Status | Document Location |
|---|---|---|---|
| **Corporate** | Vesting schedules and cap table | **COMPLETE** | `/docs/corporate/cap_table.json` |
| **Intellectual Property**| Patent assignments & open-source licenses| **COMPLETE** | `/docs/legal/ip_assignments.pdf` |
| **Security** | SOC2 Type II status & pen test reports | **COMPLETE** | `/docs/security/soc2_report.pdf` |
| **Financials** | 3-year ARR history & cost projections | **COMPLETE** | `/docs/finance/projections.xlsx` |

---

## 3. Technology Risk Log
*   *Identified Risk 1*: Single database node represents a single point of failure. *Mitigation*: Planned multi-region replication.
*   *Identified Risk 2*: Dependency on third-party APIs. *Mitigation*: Implemented fallback caches.
