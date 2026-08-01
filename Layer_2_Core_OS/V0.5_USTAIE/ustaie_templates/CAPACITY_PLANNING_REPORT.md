# Template: Capacity Planning Report

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Report ID**: CAP-[UUID]
*   **Target Time Horizon**: 12 Months

---

## 2. Workload Data Projections
*Estimate storage and memory capacity needs over a 12-month timeline based on target growth.*

*   **Initial Database Size**: [e.g., 5 GB]
*   **Projected Weekly Write Rate**: [e.g., 250 MB / week]
*   **Target 12-Month Storage Requirement**: **18 GB** (including indexes and database temp spaces).

---

## 3. Infrastructure Capacity Specifications

| Resource Type | Current Allocated Capacity | 12-Month Target Capacity | Scaling Strategy |
|---|---|---|---|
| **Database Storage** | 20 GB SSD | 100 GB SSD | Auto-expanding disk rules enabled |
| **Worker RAM** | 4 GB | 16 GB | Horizontal scaling auto-groups |
| **Network Egress Bandwidth**| 100 GB / month | 1 TB / month | CDN caching optimization |

---

## 4. Verification Check
*   [ ] Checked database space warning alerts.
*   [ ] Checked cloud provider billing thresholds.
