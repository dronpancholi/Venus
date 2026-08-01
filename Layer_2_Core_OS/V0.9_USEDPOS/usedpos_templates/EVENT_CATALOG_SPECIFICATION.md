# Event Catalog Specification
**Document ID:** VENUS-STD-041
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. CloudEvents 1.0 JSON Wrapper Schema
All domain events published to the message broker must conform to the CloudEvents standard:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CloudEventWrapper",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string", "format": "uri" },
    "specversion": { "type": "string", "const": "1.0" },
    "type": { "type": "string" },
    "time": { "type": "string", "format": "date-time" },
    "data": { "type": "object" }
  },
  "required": ["id", "source", "specversion", "type", "time", "data"]
}
```

---

## 2. Reusable Checklist & Exit Criteria
*   [ ] Checked that event identifiers are generated using UUIDv4 for de-duplication.
*   [ ] Verified event timestamps are formatted as ISO 8601 UTC values.
*   [ ] Confirmed schemas contain standard header metadata fields.
