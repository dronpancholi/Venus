# API Contract Test Cases
**Document ID:** VENUS-STD-070
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
API Contract testing guarantees that API providers and consumers remain aligned with the documented API specifications (OpenAPI 3.0), preventing interface regressions.

## 2. API Contract Schema Specification
All API endpoints must match the following OpenAPI specification schema outline:

```yaml
openapi: 3.0.3
info:
  title: Project Venus Core Order Service
  version: 1.0.0
paths:
  /v1/orders:
    post:
      summary: Create a new order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderRequest'
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
components:
  schemas:
    OrderRequest:
      type: object
      required:
        - productId
        - quantity
      properties:
        productId:
          type: string
        quantity:
          type: integer
          minimum: 1
    OrderResponse:
      type: object
      required:
        - id
        - status
      properties:
        id:
          type: string
        status:
          type: string
```

## 3. Pact Consumer Test Script Template
```typescript
import { Pact } from '@pact-foundation/pact';
import path from 'path';

const provider = new Pact({
  consumer: 'OrderConsumerWeb',
  provider: 'OrderServiceProvider',
  port: 8081,
  log: path.resolve(process.cwd(), 'logs', 'pact.log'),
  dir: path.resolve(process.cwd(), 'pacts'),
  spec: 2,
});

describe('API Contract - Order Creation', () => {
  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  it('should receive a 201 Created response from the order service provider', async () => {
    // Arrange
    await provider.addInteraction({
      state: 'provider is ready to receive orders',
      uponReceiving: 'a valid order creation request',
      withRequest: {
        method: 'POST',
        path: '/v1/orders',
        headers: { 'Content-Type': 'application/json' },
        body: { productId: 'prod_9091', quantity: 2 },
      },
      willRespondWith: {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: { id: 'ord_12345', status: 'Pending' },
      },
    });

    // Act (Client code execution)
    const client = new OrderClient('http://localhost:8081');
    const response = await client.createOrder('prod_9091', 2);

    // Assert
    expect(response.status).toBe('Pending');
    expect(response.id).toBe('ord_12345');
  });
});
```

## 4. Cross-References
- [Integration Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/INTEGRATION_TEST_SPECIFICATION.md)
- [Mock Service Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/MOCK_DOUBLE_SERVICE_SPEC.md)
