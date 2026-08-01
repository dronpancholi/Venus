# Template: Disaster Recovery Strategy

## 1. Recovery Objectives
*   **Recovery Point Objective (RPO)**: [e.g., 1 hour (Maximum data loss window)]
*   **Recovery Time Objective (RTO)**: [e.g., 4 hours (Maximum system restoration window)]

---

## 2. Backup Schedules & Configurations

| Target Data Resource | Backup Frequency | Storage Type | Retention Policy | Encryption |
|---|---|---|---|---|
| **Production PostgreSQL**| Hourly incremental | AWS S3 Glaciers | 30 days retention | AES-256 enabled |
| **Object Assets Storage** | Daily snapshots | Cross-region S3 | 90 days retention | AES-256 enabled |
| **Secrets configuration**| Version controlled | Cloud KMS | Infinite | KMS Key wrapped |

---

## 3. Disaster Scenarios & Playbooks

### Scenario A: Complete Primary Cloud Region Outage
*   **Action Plan**:
    1.  Divert traffic to secondary backup region using DNS latency routing rules.
    2.  Promote secondary regional database replica to master.
    3.  Launch worker containers in secondary region autoscaling groups.
    4.  Verify network health and check connection logs.

---

## 4. Verification Schedule
*   *Disaster Recovery Drills*: Enforced bi-annual simulation test run.
*   *Verification Script*: `scripts/dr_sim_failover.sh`
