# Architecture Decision Record (ADR)
**Document ID:** VENUS-STD-024
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## ADR-001: Standardization of PostgreSQL JSONB for Audit Logging

### Status
Accepted

### Context & Problem
We require a high-throughput audit logging mechanism to record all user and service modifications. The schema must be flexible to support arbitrary resource changes, but require query capability to support audits.

### Decision
We will use PostgreSQL `JSONB` columns in a dedicated `audit_logs` table for storing unstructured audit payloads, while using structured columns for common indexing keys (e.g., `user_id`, `resource_type`, `timestamp`).

### Rationale
- **Flexibility**: `JSONB` allows schema-less data structures.
- **Performance**: PostgreSQL supports GIN (Generalized Inverted Index) on `JSONB` fields.
- **Simplicity**: Avoids the need to operate a separate NoSQL database for logging.

### Alternatives Considered
- **Elasticsearch**: Rejected due to high operational cost for early-stage deployments.
- **MongoDB**: Rejected to keep our database stack unified on PostgreSQL.

---

## 5. Reusable Checklist & Exit Criteria
*   [ ] Checked that the ADR is numbered and logged in the decisions index.
*   [ ] Verified that alternatives were analyzed against cost and operational complexity.
*   [ ] Confirmed team consensus on trade-offs.
