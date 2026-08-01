# Data Warehouse ETL Specification
**Document ID:** VENUS-STD-040
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. ETL Pipeline Architecture
The system extracts operational transaction data periodically, formats it, and loads it into BigQuery for analytical processing:

```
[PostgreSQL Database] ──► [ETL Extractor (Throttled)] ──► [Parquet Format] ──► [BigQuery Load]
```

## 2. Data Mapping
| Source Column | Destination BigQuery Field | Transformation Applied |
| :--- | :--- | :--- |
| `id` (UUID) | `transaction_id` (STRING) | Cast to string |
| `amount` (DECIMAL) | `amount` (NUMERIC) | Map to numeric |
| `created_at` (TIMESTAMP)| `timestamp` (TIMESTAMP) | Cast to UTC |

---

## 3. Reusable Checklist & Exit Criteria
*   [ ] Checked that staging files are generated in compressed Parquet formats.
*   [ ] Verified that export schedules run during off-peak utilization hours.
*   [ ] Confirmed destination table schemas support partition pruning filters.
