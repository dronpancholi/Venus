# Message Broker Topic Schema
**Document ID:** VENUS-STD-042
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Topic Layout and Retention
Message brokers enforce strict partitioning keys to guarantee message ordering:

| Topic Name | Partition Count | Partition Key | Replication Factor | Retention Policy |
| :--- | :--- | :--- | :--- | :--- |
| `venus.events.accounts` | 8 | `account_id` | 3 | 7 Days (Compact) |
| `venus.events.transactions`| 16 | `transaction_id` | 3 | 14 Days (Delete) |

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that topics specify a replication factor of at least 3.
*   [ ] Verified partition keys prevent hotspot routing bottlenecks.
*   [ ] Confirmed schema registry hooks block invalid event payload formats.
