# ENGINE — API Versioning Engine
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Manages the complete lifecycle of API versions — from introduction to deprecation to sunset. Enforces the API evolution standards from Part 11 and ensures zero breaking changes reach consumers without adequate notice and migration support.

---

## API Change Classification

### Non-Breaking Changes (Safe to deploy without version bump)
```
ADDITIVE changes — always safe:
  ✅ Adding new optional request parameters
  ✅ Adding new response fields
  ✅ Adding new API endpoints
  ✅ Adding new values to enums (with unknown-value handling in clients)
  ✅ Relaxing validation rules (accepting more inputs)
  ✅ Adding new optional headers
  ✅ Improving error messages (format preserved)
  ✅ Performance improvements
  ✅ Bug fixes (when intended behavior documented)
```

### Breaking Changes (Require new API version)
```
BREAKING changes — always require new version:
  ❌ Removing a field from response
  ❌ Renaming a field
  ❌ Changing field type (string → number)
  ❌ Making optional field required
  ❌ Removing an endpoint
  ❌ Changing endpoint URL
  ❌ Changing HTTP method
  ❌ Tightening validation (rejecting previously-accepted inputs)
  ❌ Changing error codes/formats that clients depend on
  ❌ Removing enum values
```

---

## Versioning Strategies

### Strategy 1: URI Path Versioning (Default for Major Versions)
```
/v1/orders    ← stable v1 API
/v2/orders    ← new v2 with breaking changes

Rules:
  - Only increment on breaking changes
  - v1 and v2 run simultaneously during transition
  - v1 supported minimum 90 days after v2 GA
  - Maximum 2 simultaneous active major versions
```

### Strategy 2: Date-Based Header Versioning (Minor API Variations)
```
API-Version: 2024-01-15

Rules:
  - New date version when adding significant features
  - Clients pin to a date version for stability
  - Server supports all versions within the rolling window
  - Rolling window: last 12 months of date versions
```

---

## Deprecation Lifecycle Management

```
State Machine:
  STABLE → DEPRECATED → SUNSET → REMOVED

Transition: STABLE → DEPRECATED
  - Engineering decision documented in ADR
  - Deprecation header added to all responses:
    Deprecation: true
    Sunset: {date}
    Link: <{successor-url}>; rel="successor-version"
  - Consumer notification sent (email + in-app)
  - Migration guide published
  - 90-day minimum before sunset

Transition: DEPRECATED → SUNSET
  - Warning becomes error in responses
  - 30-day final notice sent to all consumers
  - Support team briefed

Transition: SUNSET → REMOVED
  - Endpoint returns 410 Gone with migration URL
  - 30 days on 410 before full removal from codebase
```

---

## Consumer Tracking
```
For each API version, track:
  - All registered consumers (service name, team, contact)
  - Last API call timestamp per consumer
  - Consumer migration status (not started / in progress / migrated)
  - Escalation contacts for non-responsive consumers

Dashboard shows:
  v1/orders: 12 consumers | 3 migrated | 9 remaining | Sunset: Mar 1
  Action: Escalate to 4 consumers who haven't started migration
```

---

## Automated Compatibility Testing
```
Pre-deployment gates:
  1. Consumer-driven contract tests (Pact) run against new API version
  2. All known consumer contracts must pass
  3. Backwards compatibility test against previous version response schemas
  4. Schema diff generated and reviewed in PR

Breaking change detection:
  - openapi-diff compares specs on every PR
  - Any breaking change detected → PR blocked → version bump required
```

---

## API Changelog Automation
```
Generated on every merge to main:
  - Change type (non-breaking/deprecation/new-version)
  - Affected endpoints
  - What changed
  - Migration notes

Published to:
  - docs.{domain}.com/changelog
  - API consumers via webhook notification
  - Developer newsletter (for public APIs)
```
