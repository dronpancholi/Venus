# Part 03 — Distributed Systems

## 1. Distributed Property Laws (CAP & PACELC)
When designing distributed topologies, we operate under CAP and PACELC constraints:
*   **CAP**: Consistency, Availability, Partition Tolerance.
*   **PACELC**: If there is a Partition (P), trade off Availability (A) or Consistency (C); Else (E), trade off Latency (L) or Consistency (C).

---

## 2. Distributed Algorithms Directory

### 2.1 Consensus (Raft / Paxos)
*   *Application*: Leader election, shared state replication (e.g. etcd, ZooKeeper).
*   *Requirement*: Quorum scale must satisfy \(Q = \lfloor N/2 \rfloor + 1\) nodes.

### 2.2 Replications & Conflict Resolution
*   **CRDTs (Conflict-free Replicated Data Types)**: Operation-based or state-based convergence without locking.
*   **Vector Clocks**: Logical clock tracking order of events in distributed environments.

---

## 3. Sharding & Partition Mapping
Map data sharding partitions to target key spaces to prevent hot-spot nodes:

```
[Write Event] ──► [Consistent Hashing Ring] ──► [Shard Node A (Keys 0-99)]
                                            ──► [Shard Node B (Keys 100-199)]
```

### 3.1 Distributed Locking
*   *Mechanism*: Redlock / etcd leases.
*   *Warning*: Never run distributed locks with infinite lease TTLs; always enforce heartbeats and lock expirations to prevent permanent system deadlocks.

---

## 4. Distributed Systems Checklist
*   [ ] Classified system under CAP/PACELC (e.g., PC/EC).
*   [ ] Configured quorum counts for databases.
*   [ ] Checked sharding key definitions for hot-spot safety.
*   [ ] Configured TTL bounds on all distributed lock leases.
