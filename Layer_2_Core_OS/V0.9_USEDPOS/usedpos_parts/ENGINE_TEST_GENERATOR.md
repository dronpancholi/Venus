# ENGINE — Test Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates comprehensive test suites for any service. Produces unit, integration, contract, E2E, performance, and security tests. Ensures ≥ 85% code coverage and validates all critical paths, edge cases, and failure modes.

---

## Input Requirements
```
Required:
  - Source code or module specification
  - Domain entities and use cases
  - API contracts (for integration/contract tests)
  - External dependencies (databases, APIs, queues)

Optional:
  - Coverage threshold override
  - Performance targets
  - Test framework preference (Jest / Vitest / Pytest / Go test)
  - Consumer list for contract tests
```

---

## Generated Test Hierarchy

### Unit Tests
```typescript
// Example: Generated unit test for domain entity
describe('Order Entity', () => {
  describe('create()', () => {
    it('should create order with valid data', () => {
      const command = CreateOrderCommandMother.valid()
      const order = Order.create(command)

      expect(order.id).toBeDefined()
      expect(order.status).toBe(OrderStatus.PENDING)
      expect(order.domainEvents).toContainEqual(
        expect.objectContaining({ eventType: 'OrderCreated' })
      )
    })

    it('should throw when items list is empty', () => {
      const command = CreateOrderCommandMother.withEmptyItems()
      expect(() => Order.create(command)).toThrow(EmptyOrderItemsError)
    })

    it('should throw when total amount is negative', () => {
      const command = CreateOrderCommandMother.withNegativeTotal()
      expect(() => Order.create(command)).toThrow(InvalidOrderAmountError)
    })
  })

  describe('cancel()', () => {
    it('should cancel pending order', () => { ... })
    it('should throw when cancelling fulfilled order', () => { ... })
    it('should emit OrderCancelled domain event', () => { ... })
  })
})
```

### Integration Tests
```typescript
// Example: Generated integration test for use case
describe('CreateOrderUseCase (Integration)', () => {
  let useCase: CreateOrderUseCase
  let orderRepository: PostgresOrderRepository

  beforeAll(async () => {
    // Real database via testcontainers
    const pg = await new PostgreSqlContainer().start()
    orderRepository = new PostgresOrderRepository(pg.getConnectionUri())
    useCase = new CreateOrderUseCase(orderRepository)
  })

  it('should persist order to database', async () => {
    const command = CreateOrderCommandMother.valid()
    const result = await useCase.execute(command)

    const saved = await orderRepository.findById(result.orderId)
    expect(saved).toBeDefined()
    expect(saved.status).toBe(OrderStatus.PENDING)
  })
})
```

### API Contract Tests (Pact)
```typescript
// Consumer-driven contract test
describe('Orders API Contract', () => {
  const provider = new PactV3({
    consumer: 'notification-service',
    provider: 'order-service',
  })

  it('should return order by ID', async () => {
    await provider
      .addInteraction({
        given: 'Order ORD-001 exists',
        uponReceiving: 'a request for order ORD-001',
        withRequest: { method: 'GET', path: '/v1/orders/ORD-001' },
        willRespondWith: {
          status: 200,
          body: { id: 'ORD-001', status: 'pending' }
        }
      })
      .executeTest(async (mockServer) => {
        const result = await orderClient.getById('ORD-001')
        expect(result.id).toBe('ORD-001')
      })
  })
})
```

---

## Coverage Requirements
| Layer | Minimum Coverage |
|---|---|
| Domain (entities, value objects) | 95% |
| Application (use cases) | 90% |
| Infrastructure (adapters) | 80% |
| Overall | 85% |

---

## Test Data Factories
All tests use **Object Mother** pattern:
```typescript
class CreateOrderCommandMother {
  static valid(): CreateOrderCommand { ... }
  static withEmptyItems(): CreateOrderCommand { ... }
  static withInvalidCustomer(): CreateOrderCommand { ... }
  static withNegativeTotal(): CreateOrderCommand { ... }
}
```

---

## Performance Test Generation
```javascript
// k6 load test generated per API endpoint
import http from 'k6/http'
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<200', 'p(99)<500'],
    'http_req_failed': ['rate<0.01'],
  },
}
```
