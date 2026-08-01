# Hexagonal Ports & Adapters Specification
**Document ID:** VENUS-STD-025
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Core Architecture
This specification maps how interfaces (ports) decouple core domain models from external adapters (databases, APIs, UI).

## 2. Inbound and Outbound Port Structure
```python
# domain/ports.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

# Inbound Port (Driving Interface)
class PaymentUseCase(ABC):
    @abstractmethod
    def execute_payment(self, src: UUID, dest: UUID, amount: float) -> dict:
        pass

# Outbound Port (Driven Interface)
class AccountRepository(ABC):
    @abstractmethod
    def find_by_id(self, account_id: UUID) -> Optional[dict]:
        pass

    @abstractmethod
    def save(self, account_data: dict) -> None:
        pass
```

## 3. Secondary Adapter (Database Implementation)
```python
# adapters/database.py
from domain.ports import AccountRepository
from uuid import UUID

class PostgresAccountAdapter(AccountRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def find_by_id(self, account_id: UUID) -> Optional[dict]:
        return self.db.execute("SELECT * FROM accounts WHERE id = %s", (str(account_id),)).fetchone()

    def save(self, account_data: dict) -> None:
        self.db.execute("UPDATE accounts SET balance = %s WHERE id = %s", (account_data['balance'], account_data['id']))
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that domain code imports no framework or adapter libraries.
*   [ ] Verified that all adapters implement their designated port interface.
*   [ ] Confirmed port interfaces utilize standard native typing constructs.
