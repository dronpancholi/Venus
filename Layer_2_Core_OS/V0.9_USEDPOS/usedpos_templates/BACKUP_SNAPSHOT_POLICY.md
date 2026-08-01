# Backup and Snapshot Policy
**Document ID:** VENUS-STD-089
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Policy Statement
All operational databases and storage buckets hosting customer transaction histories or configuration assets must enforce automated backup and snapshot schedules to prevent data loss.

## 2. Schedule and Retention Matrix

| Data Classification | Backup Type | Frequency | Execution Window | Retention Period |
| :--- | :--- | :--- | :--- | :--- |
| **Transactional DB** | Incremental Transaction Logs | Every 15 Minutes | Continuous | 35 Days |
| **Transactional DB** | Full Database Export | Daily | 01:00 UTC | 90 Days |
| **Static Assets** | Folder Snapshot | Weekly | Sunday 02:00 UTC | 180 Days |
| **Audit Logs** | Immutable Archive | Monthly | 1st of month | 7 Years (Compliance) |

## 3. Verification and Restoration Runbook
An untested backup is invalid. Once every 30 days, the SRE team must execute a backup restoration drill:
1. Spin up an isolated PostgreSQL instance inside a test namespace.
2. Download the database snapshot file from the backup storage bucket:
   ```bash
   aws s3 cp s3://venus-production-backups/db/daily-20260626.sql.gz ./backup.sql.gz
   ```
3. Extract and load the backup contents into the test container:
   ```bash
   gunzip -c backup.sql.gz | psql -h localhost -U postgres -d test_verify_db
   ```
4. Run validation queries to confirm record count matching.

## 4. Cross-References
- [Disaster Recovery Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DISASTER_RECOVERY_RUNBOOK.md)
