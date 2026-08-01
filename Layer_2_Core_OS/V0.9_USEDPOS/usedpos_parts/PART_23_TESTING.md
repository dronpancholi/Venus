# Part 23: Testing

## 1. Context & Strategy
Testing under Project Venus guarantees code correctness, regression prevention, and behavioral integrity. We enforce a multi-tiered validation model that separates concern levels, standardizes mocking practices, and measures effectiveness using rigorous statistical and coverage standards. No code changes are merged without fulfilling strict execution criteria.

---

## 2. Test Mathematical Efficacy & Coverage

### 2.1 Mutation Testing Score
Code coverage metrics can be misleading. To evaluate test assertion quality, we employ mutation testing, which introduces syntax faults (mutants) and checks if the test suite fails (kills the mutant). The mutation score ($MS$) is defined as:

$$MS = \frac{M_k}{M_t} \times 100$$

Where:
*   $M_k$: Number of killed mutants.
*   $M_t$: Total number of generated mutants.
*   *Requirement*: Core modules must maintain a mutation testing score of $MS \ge 85\%$.

### 2.2 Test Suite Execution Time (Amdahl's Law Application)
To keep developer feedback loops tight, test executions must be highly parallelized. If $90\%$ of our test suite ($p = 0.9$) can be run in parallel, and we run them across $s = 8$ concurrent worker threads, the theoretical speedup ($S$) is calculated as:

$$S = \frac{1}{(1 - p) + \frac{p}{s}} = \frac{1}{0.1 + \frac{0.9}{8}} = \frac{1}{0.2125} \approx 4.7 \times$$

---

## 3. Testing Paradigms & Integration

### 3.1 Consumer-Driven Contract Testing (Pact Contract)
Microservices must define and verify interaction contracts using Pact to prevent breaking changes at API boundaries.

```json
{
  "consumer": {
    "name": "VenusFrontendService"
  },
  "provider": {
    "name": "VenusOrderService"
  },
  "interactions": [
    {
      "description": "A request for order details",
      "request": {
        "method": "GET",
        "path": "/orders/ORD-88219"
      },
      "response": {
        "status": 200,
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "orderId": "ORD-88219",
          "status": "COMPLETED",
          "amount": 149.99
        },
        "matchingRules": {
          "$.body.orderId": { "match": "type" },
          "$.body.status": { "match": "regex", "regex": "COMPLETED|PENDING|FAILED" },
          "$.body.amount": { "match": "type" }
        }
      }
    }
  ]
}
```

### 3.2 Integration Testing Isolation (Docker Compose Setup)
Integration tests must execute in isolated environments with spun-up database and cache containers.

```yaml
# docker-compose.test.yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: venus_test
      POSTGRES_PASSWORD: testpassword
    ports:
      - "5432"
  redis:
    image: redis:7-alpine
    ports:
      - "6379"
  app-test:
    build:
      context: ..
      dockerfile: Dockerfile.test
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgres://postgres:testpassword@db:5432/venus_test
      REDIS_URL: redis://redis:6379/0
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that unit test coverage exceeds $80\%$ for lines, functions, and branches.
*   [ ] Confirmed contract tests pass against Pact brokers prior to deployment.
*   [ ] Verified that external API calls are mocked using standard adapters rather than actual network requests.
*   [ ] Checked that integration tests clean up their database state before and after each run.
*   [ ] Confirmed the mutation testing tool runs successfully and returns $MS \ge 85\%$.
