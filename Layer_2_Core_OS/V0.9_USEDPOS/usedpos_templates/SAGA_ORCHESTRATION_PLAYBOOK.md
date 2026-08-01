# SAGA Orchestration Playbook
**Document ID:** VENUS-STD-046
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Saga Execution Steps
The Saga orchestrator coordinates distributed microservice actions. If a step fails, the orchestrator triggers compensating actions:

```
[Step 1: Lock Funds] ──(Success)──► [Step 2: Debit Ledger] ──(Failure)──► [Trigger Compensations]
                                                                                │
                                                                                ▼
                                                                        [Unlock Funds Account]
```

## 2. Saga Matrix definition
- **Forward Action**: `ReserveFunds(sender_id, amount)`
- **Compensating Action**: `ReleaseFunds(sender_id, amount)`

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that compensating actions are designed to be idempotent.
*   [ ] Verified Saga state is logged continuously to prevent orchestration losses on restart.
*   [ ] Confirmed timeout metrics abort active transactions gracefully.
