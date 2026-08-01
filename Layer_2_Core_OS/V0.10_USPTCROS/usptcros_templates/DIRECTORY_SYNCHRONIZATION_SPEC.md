# USPTCROS Directory Synchronization Specification
**Document Link:** [Directory Sync Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DIRECTORY_SYNCHRONIZATION_SPEC.md)

## 1. Synchronization Architecture
Directory synchronization bridges corporate enterprise directories (Active Directory / LDAP) and local application IAM databases using SCIM 2.0.

```
  ┌─────────────────────────┐              ┌─────────────────────────┐
  │   Enterprise LDAP/AD    │ ──[SCIM]───► │  Venus IAM Database     │
  │   (Source of Truth)     │              │     (Target Database)   │
  └─────────────────────────┘              └─────────────────────────┘
```

## 2. SCIM 2.0 User Resource Schema Mapping
| AD/LDAP Directory Attribute | SCIM Attribute Target | Data Format | Validation Requirement |
|---|---|---|---|
| `objectGUID` | `externalId` | String (Hex/UUID) | Unique constraint in database |
| `sAMAccountName` | `userName` | String | Regular expression: `^[a-z0-9._-]{3,20}$` |
| `mail` | `emails[type eq "work"].value` | String (Email) | Domain must match corporate domains |
| `memberOf` | `roles` | Array of Strings | Validated against [Role Catalog](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ROLE_DEFINITION_CATALOG.md) |

## 3. Synchronization Job Properties
* **Frequency:** Standard synchronization runs hourly. Incremental pushes run in real-time on attribute changes.
* **Failover Behavior:** In the event of connection failure to the source directory, authentication requests fallback to cached credentials for a maximum of 24 hours, after which strict locking is enforced.
