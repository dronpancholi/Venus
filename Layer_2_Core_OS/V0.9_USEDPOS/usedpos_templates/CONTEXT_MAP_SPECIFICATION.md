# Context Map Specification

## Document Control
| Version | Date | Author | Description | Reviewer |
| :--- | :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-06-26 | Lead Enterprise Architect | Bounded Context maps & relationship model | Tech Board |

## 1. Context Map Topology
This document traces the boundaries and upstream/downstream integrations between the core domain contexts. Individual boundary rules are detailed in [BOUNDED_CONTEXT_DEFINITION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/BOUNDED_CONTEXT_DEFINITION.md).

```mermaid
graph TD
    subgraph Core Domain
        Acc[Accounts Bounded Context] -->|Upstream [OHS, PL]| Pay[Payments Bounded Context]
    end
    subgraph External Systems
        Legacy[Legacy Billing System] -.->|Upstream| ACL[Anti-Corruption Layer]
        ACL -->|Downstream [Conformist]| Acc
    end

    style ACL fill:#f9f,stroke:#333,stroke-width:2px
```

---

## 2. Interaction Matrix & Integration Patterns
| Source Context | Target Context | Integration Relationship | Translation Protocol |
| :--- | :--- | :--- | :--- |
| Accounts | Payments | Customer / Supplier (Accounts is Supplier) | Open Host Service (gRPC endpoints) |
| Payments | Notifications | Publish / Subscribe | Published Language (JSON Event Schemas) |
| Legacy Billing | Accounts | Upstream / Downstream (Legacy is Upstream) | Anti-Corruption Layer (ACL Adapter) |

---

## 3. Anti-Corruption Layer (ACL) Implementation Pattern
The ACL prevents legacy models from polluting the clean domain schema defined in [DOMAIN_MODEL_SPECIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DOMAIN_MODEL_SPECIFICATION.md).

### 3.1 Translation Interface Pattern
```python
# python/acl/adapter.py

class LegacyBillingACLAdapter:
    def __init__(self, legacy_client, domain_account_repository):
        self.legacy_client = legacy_client
        self.repo = domain_account_repository

    def sync_legacy_balance(self, legacy_user_id: str) -> None:
        # Fetch data representing legacy structural formats
        legacy_data = self.legacy_client.get_balance(legacy_user_id)
        
        # Translate from legacy raw float model to strict value object
        translated_amount = MonetaryAmount(
            value=Decimal(str(legacy_data["RAW_VAL"])),
            currency=Currency(legacy_data["CURR_CODE"])
        )
        
        # Save validated model downstream
        domain_account = self.repo.find_by_id(legacy_user_id)
        domain_account.deposit(translated_amount)
        self.repo.save(domain_account)
```
- For details on event serialization and schema mappings, review [MESSAGE_BROKER_TOPIC_SCHEMA.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/MESSAGE_BROKER_TOPIC_SCHEMA.md).
