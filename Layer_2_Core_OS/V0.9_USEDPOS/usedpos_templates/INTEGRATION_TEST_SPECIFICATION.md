# Integration Test Specification
**Document ID:** VENUS-STD-063
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Scope and Objective
Integration testing verifies the interface compatibility and interaction behaviors between software modules and external dependencies (databases, cache nodes, third-party messaging buses).

## 2. Test Environment Setup
To prevent tests from mutating local filesystems or polluting shared dev databases, integration tests must run in isolated dockerized containers using standard test containers.

```mermaid
graph LR
    Runner[Test Runner] -->|Spins Up| PG[(PostgreSQL Container)]
    Runner -->|Configures| App[Application Code]
    App -->|Reads/Writes| PG
    Runner -->|Teardown| PG
```

## 3. Database Integration Test Code Template (Node.js + pg)
```typescript
import { Client } from 'pg';
import { DatabaseUserStore } from '../../src/infrastructure/db/DatabaseUserStore';

describe('DatabaseUserStore Integration Tests', () => {
  let client: Client;
  let userStore: DatabaseUserStore;

  beforeAll(async () => {
    // Establish connection to isolated test container DB
    client = new Client({
      connectionString: process.env.TEST_DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/venus_test',
    });
    await client.connect();
    userStore = new DatabaseUserStore(client);
  });

  beforeEach(async () => {
    // Clear the schema fixtures
    await client.query('TRUNCATE TABLE users CASCADE;');
  });

  afterAll(async () => {
    await client.end();
  });

  it('should persist and retrieve a user from postgresql database', async () => {
    // Arrange
    const userPayload = { id: 'usr_idx1', email: 'integration@venus.org', name: 'Integration Test' };

    // Act
    await userStore.insert(userPayload);
    const retrieved = await userStore.find(userPayload.id);

    // Assert
    expect(retrieved).not.toBeNull();
    expect(retrieved?.email).toBe(userPayload.email);
    expect(retrieved?.name).toBe(userPayload.name);
  });
});
```

## 4. Cross-References
- [Unit Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/UNIT_TEST_SPECIFICATION.md)
- [Mock / Double Service Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/MOCK_DOUBLE_SERVICE_SPEC.md)
