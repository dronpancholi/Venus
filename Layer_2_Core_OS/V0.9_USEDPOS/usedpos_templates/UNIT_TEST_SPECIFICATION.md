# Unit Test Specification
**Document ID:** VENUS-STD-062
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Unit Testing Principles
1. **Isolation:** Unit tests must test code in isolation. No external database, filesystem, or network network dependencies.
2. **AAA Pattern:** All test cases must follow the Arrange-Act-Assert structure:
   - **Arrange:** Set up test inputs, mock dependencies, and specify expectations.
   - **Act:** Execute the target method or function.
   - **Assert:** Validate output against expected results.
3. **Speed:** Unit test suites must run in under 3 minutes for the entire repository.

## 2. Language-Specific Templates

### 2.1 TypeScript/Node (Jest / Vitest)
```typescript
import { UserService } from '../../src/domain/services/UserService';
import { UserRepository } from '../../src/infrastructure/db/UserRepository';

describe('UserService - createUser', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockUserRepository = {
      save: jest.fn(),
      findByEmail: jest.fn(),
    } as unknown as jest.Mocked<UserRepository>;

    userService = new UserService(mockUserRepository);
  });

  it('should successfully create a user when email is unique', async () => {
    // Arrange
    const userData = { email: 'test@venus.org', name: 'Test User' };
    mockUserRepository.findByEmail.mockResolvedValue(null);
    mockUserRepository.save.mockResolvedValue({ id: 'usr_100', ...userData });

    // Act
    const result = await userService.createUser(userData);

    // Assert
    expect(mockUserRepository.findByEmail).toHaveBeenCalledWith('test@venus.org');
    expect(mockUserRepository.save).toHaveBeenCalled();
    expect(result).toHaveProperty('id', 'usr_100');
  });

  it('should throw an error when email already exists', async () => {
    // Arrange
    const userData = { email: 'test@venus.org', name: 'Test User' };
    mockUserRepository.findByEmail.mockResolvedValue({ id: 'usr_99', email: 'test@venus.org', name: 'Existing User' });

    // Act & Assert
    await expect(userService.createUser(userData)).rejects.toThrow('Email already registered');
    expect(mockUserRepository.save).not.toHaveBeenCalled();
  });
});
```

### 2.2 Python (pytest)
```python
import pytest
from unittest.mock import Mock
from src.domain.services import calculate_discount

def test_calculate_discount_standard_user():
    # Arrange
    user = Mock()
    user.is_premium = False
    order_amount = 100.00
    
    # Act
    discount = calculate_discount(user, order_amount)
    
    # Assert
    assert discount == 0.00

def test_calculate_discount_premium_user():
    # Arrange
    user = Mock()
    user.is_premium = True
    order_amount = 100.00
    
    # Act
    discount = calculate_discount(user, order_amount)
    
    # Assert
    assert discount == 10.00
```

### 2.3 Go (`go test`)
```go
package services

import (
	"errors"
	"testing"
)

type MockNotifier struct {
	SendFunc func(email string, msg string) error
}

func (m *MockNotifier) Send(email string, msg string) error {
	return m.SendFunc(email, msg)
}

func TestNotifyUser(t *testing.T) {
	// Arrange
	mockNotifier := &MockNotifier{
		SendFunc: func(email string, msg string) error {
			if email == "" {
				return errors.New("empty email")
			}
			return nil
		},
	}

	// Act
	err := NotifyUser(mockNotifier, "user@venus.org", "Welcome!")

	// Assert
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
}
```

## 3. Cross-References
- [Test Plan Strategy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_PLAN_STRATEGY.md)
- [Integration Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/INTEGRATION_TEST_SPECIFICATION.md)
