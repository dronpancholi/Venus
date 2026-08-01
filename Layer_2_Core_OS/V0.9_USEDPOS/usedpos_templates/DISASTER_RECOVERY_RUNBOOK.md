# Disaster Recovery Runbook
**Document ID:** VENUS-STD-099
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Objectives and Strategy
This runbook details system-wide disaster recovery procedures (multi-region database failover, DNS routing flips) to satisfy target metrics during server outages.

## 2. DR Key Performance metrics (RTO & RPO)
*   **Recovery Time Objective (RTO):** The maximum tolerable duration of system outage before restoration. **Target: RTO < 1 Hour**.
*   **Recovery Point Objective (RPO):** The maximum tolerable age of data loss from the moment of system outage. **Target: RPO < 15 Minutes**.

```text
[Service Outage] --------------> [System Restoration]
       | <------- RTO (< 1 Hour) --------> |
       |
  [Last Backup] <--- RPO (< 15 Minutes) ---|
```

## 3. Disaster Recovery Execution Plan

### 3.1 Primary Region Outage Detection
A regional outage is declared if:
1. Ping latency to primary region is 100% loss for 5 minutes.
2. Cloud monitoring console reports regional service disruption.

### 3.2 Stage 1: Database Promotion to Failover Region
Promote the secondary database instance to primary writer:
```bash
# Check postgres replication sync status
pg_controldata -D /var/lib/postgresql/data | grep "Database cluster state"

# Trigger secondary database promotion command
pg_ctl promote -D /var/lib/postgresql/data
```

### 3.3 Stage 2: Ingress DNS Redirection
Flip the Route53/CloudDNS routing policies to point to the failover load balancer IPs:
```bash
# Update cloud DNS resource record set mapping
gcloud dns record-sets transaction start --zone="venus-zone"
gcloud dns record-sets transaction remove --zone="venus-zone"   --name="api.venus.org." --type="A" --ttl="60" "104.154.0.1"
gcloud dns record-sets transaction add --zone="venus-zone"   --name="api.venus.org." --type="A" --ttl="60" "34.120.99.9"
gcloud dns record-sets transaction execute --zone="venus-zone"
```

### 3.4 Stage 3: Post-Migration Smoke Sanity Tests
Validate traffic is routing correctly to the failover region:
```bash
curl -s -o /dev/null -w "%{http_code}" https://api.venus.org/healthz
```

## 4. Cross-References
- [Backup and Snapshot Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/BACKUP_SNAPSHOT_POLICY.md)
- [Incident Response Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/INCIDENT_RESPONSE_RUNBOOK.md)
