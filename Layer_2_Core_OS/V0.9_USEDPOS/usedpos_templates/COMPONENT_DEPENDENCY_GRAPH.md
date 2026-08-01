# Component Dependency Graph
**Document ID:** VENUS-STD-023
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Context & Boundaries
This specification maps the dependency tree of core system components in a Hexagonal (Ports and Adapters) architecture, ensuring that domain models have zero external dependencies.

## 2. Directed Acyclic Graph of Dependencies
```mermaid
graph TD
    subgraph Primary Adapters
        REST[REST Controller]
        gRPC[gRPC Handler]
    end

    subgraph Application Ports
        IPort[Inbound Port Interface]
        OPort[Outbound Port Interface]
    end

    subgraph Domain Layer
        DS[Domain Service]
        AM[Aggregate Model]
    end

    subgraph Secondary Adapters
        DB[Database Adapter]
        MQ[Message Broker Adapter]
    end

    REST --> IPort
    gRPC --> IPort
    IPort --> DS
    DS --> AM
    DS --> OPort
    DB --> OPort
    MQ --> OPort
```

## 3. Boundary Rules & Validation
1. **Dependency Inversion**: Outer layers (Adapters) must depend on inner layers (Ports / Domain). Inner layers must never depend on outer layers.
2. **Cycle Prevention**: The dependency graph must represent a Directed Acyclic Graph (DAG). Any circular dependency detected during static analysis will abort the CI build.

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that domain models contain zero framework imports.
*   [ ] Verified that adapters only communicate with the domain via ports.
*   [ ] Confirmed dependency graphs are cyclic-dependency audited.
