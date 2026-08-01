# Part 02 — Architecture Intelligence

## 1. Topological Architectural Patterns
Architecture Intelligence maps systems to their optimal structural topology: Monoliths, Modular Monoliths, Microservices, Macroservices, SOA, Clean/Hexagonal (Ports & Adapters), Cell Architecture, or Federated Systems.

---

## 2. Pattern Evaluation Matrix

| Pattern Name | Best For | Structural Boundary | Reversibility Cost |
|---|---|---|---|
| **Monolith** | Early validation, MVP | Shared process memory, single DB | Low |
| **Modular Monolith** | Medium scale, team isolation | Explicit internal package interfaces | Medium |
| **Microservices** | Hyper-scale, multi-team | Network boundaries, separate DBs | High |
| **Cell Architecture**| Large-scale blast radius control | Isolated deploy units (cells) | Critical |
| **Clean / Hexagonal** | Domain logic isolation | Ports (interfaces) & Adapters (impl) | Low |

---

## 3. Cell-Based Architecture Topology
Cell-based architectures partition users into completely self-contained deployment units (cells) to isolate failure blast radius:

```
[Inbound Router] ────► [Cell 1 (Users A-M)] ──► [Dedicated DB 1]
                 ────► [Cell 2 (Users N-Z)] ──► [Dedicated DB 2]
```

### 3.1 Cell Partitioning Rules
*   *Zero Shared Resources*: Cells must not share databases or cache instances.
*   *Fallback Routing*: Router maps requests directly based on hashed tenant IDs.

---

## 4. Architecture Intelligence Checklist
*   [ ] Selected core pattern (Monolith vs. Cell) based on scaling targets.
*   [ ] Checked database isolation boundaries.
*   [ ] Outlined hexagonal interfaces (ports) for core logic.
*   [ ] Documented cell partition hashes.
