# PART 20 — Authorization
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Authorization defines what authenticated entities can do. While authentication answers "Who are you?", authorization answers "What are you permitted to do?" This part defines the access control models, policy enforcement patterns, permission inheritance strategies, and audit requirements for all VENUS systems.

---

## 2. Access Control Models

### 2.1 Role-Based Access Control (RBAC)
Users are assigned roles; roles have permissions.

```
User → Role(s) → Permissions

Example:
  User Alice → roles: [billing-admin, read-only-reports]
  billing-admin permissions:
    - billing.invoices.create
    - billing.invoices.read
    - billing.invoices.update
    - billing.payments.read
  read-only-reports permissions:
    - reports.dashboard.read
    - reports.export.read

Best for: Clear organizational hierarchies, enterprise SaaS
```

### 2.2 Attribute-Based Access Control (ABAC)
Access decisions based on attributes of the subject, resource, action, and environment.

```
Policy:
  ALLOW billing:invoice:read
  IF user.department == 'Finance'
  AND resource.tenant_id == user.tenant_id
  AND environment.time_of_day is BUSINESS_HOURS

Best for: Fine-grained multi-tenant access, complex conditions
```

### 2.3 Relationship-Based Access Control (ReBAC) — Google Zanzibar Model
Access based on relationships between users and objects.

```
document:report-q4 viewer: user:alice
document:report-q4 editor: group:finance-team
group:finance-team member: user:bob

Alice can view report-q4 (directly)
Bob can view report-q4 (via group membership)

Best for: Social graphs, collaborative documents, hierarchical resources
Tools: OpenFGA, Google Zanzibar, Ory Keto
```

**VENUS Default**: RBAC for most systems. ABAC for multi-tenant SaaS with complex policies. ReBAC for collaborative platforms.

---

## 3. Permission Design Standards

### 3.1 Permission Naming Convention
```
Format: {service}.{resource}.{action}

Actions:
  create, read, update, delete     — CRUD operations
  list                             — Collection read
  export                           — Data export
  publish                          — Publish/broadcast
  impersonate                      — Act as another user (dangerous)
  manage                           — All operations (admin shorthand)

Examples:
  orders.order.create
  orders.order.read
  orders.order.list
  billing.invoice.manage
  users.user.impersonate
  reports.dashboard.export
```

### 3.2 Principle of Least Privilege
- Users receive the minimum permissions necessary to perform their role
- No wildcard permissions in production (billing.*.*)
- Permissions granted explicitly; denied by default
- Admin permissions require approval workflow
- Time-limited elevated access for break-glass scenarios

---

## 4. Multi-Tenant Authorization

### 4.1 Tenant Isolation Requirements
```
Every permission check must validate:
  1. The resource belongs to the requesting user's tenant
  2. The user has the required permission within that tenant
  3. The tenant's subscription tier allows the operation

Forbidden:
  SELECT * FROM orders WHERE id = $1     -- No tenant check!

Required:
  SELECT * FROM orders WHERE id = $1 AND tenant_id = $2
```

### 4.2 Row-Level Security (PostgreSQL RLS)
```sql
-- Enforce tenant isolation at database level
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY orders_tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Application sets the tenant context before queries
SET app.current_tenant_id = 'tenant-uuid-here';
```

---

## 5. Policy Enforcement Points

```
Authorization checks happen at multiple layers:

API Gateway:           Validate JWT, check scope, rate limit
Controller Layer:      Authenticate user, extract roles
Application Layer:     Check permission for specific action
Domain Layer:          Enforce business-level invariants
Database Layer:        Row-Level Security as last line of defense

"Defense in depth" — multiple independent checks.
```

---

## 6. Permission Enforcement Code Pattern

```typescript
// Application Service pattern — authorize before executing
class CreateOrderService implements CreateOrderUseCase {
  constructor(
    private readonly authzService: AuthorizationService,
    private readonly orderRepository: OrderRepository
  ) {}

  async execute(command: CreateOrderCommand, actor: AuthenticatedUser): Promise<void> {
    // Authorization check — always before domain logic
    await this.authzService.authorize(actor, 'orders.order.create', {
      tenantId: command.tenantId
    })

    // Domain logic only executes if authorized
    const order = Order.create(command)
    await this.orderRepository.save(order)
  }
}
```

---

## 7. Delegated Access (Impersonation / Acting As)

```
Rules for impersonation:
  1. Only super-admin or support role can impersonate
  2. Impersonation requires MFA confirmation per session
  3. Impersonation is time-limited (max 4 hours)
  4. Every action taken while impersonating is attributed to BOTH the actor and the target
  5. User being impersonated receives notification
  6. Audit log entry for impersonation start/end with reason

Audit log format:
  {
    type: "impersonation.action",
    actorId: "support-agent-uuid",
    targetUserId: "customer-uuid",
    action: "order.read",
    resourceId: "ORD-001",
    timestamp: "ISO-8601",
    reason: "CS-TICKET-1234"
  }
```

---

## 8. Authorization Audit Requirements

All authorization decisions must be logged:

```
Events:
  authorization.granted  — userId, permission, resourceId, timestamp
  authorization.denied   — userId, permission, resourceId, reason, timestamp
  role.assigned          — userId, role, assignedBy, timestamp
  role.revoked           — userId, role, revokedBy, reason, timestamp
  permission.granted     — roleId, permission, grantedBy, timestamp
  permission.revoked     — roleId, permission, revokedBy, timestamp

Retention: 7 years (compliance requirement)
Storage: Append-only, tamper-evident audit log
Alert: Any privilege escalation events → Security team notification
```
