# Consensus Protocol (Raft) Specification
**Document ID:** VENUS-STD-047
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Raft Cluster Rules
To ensure data consistency in distributed state stores, clusters use the Raft consensus protocol.

- **Quorum Requirement**: A write operation is committed only after consensus is reached across a majority of nodes:
  $$Q = \lfloor N / 2 floor + 1$$
- **Cluster Configurations**:
  - $N=3 \implies Q=2$ nodes.
  - $N=5 \implies Q=3$ nodes.

## 2. Heartbeat & Election timeouts
- **Heartbeat Interval**: $150	ext{ms}$
- **Election Timeout range**: $300	ext{ms}$ to $600	ext{ms}$ (randomized to prevent split votes).

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that network configurations support cluster node auto-discovery.
*   [ ] Verified election procedures execute cleanly during partition simulations.
*   [ ] Confirmed log replication indexes match across quorum nodes.
