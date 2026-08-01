# Mock and Double Service Specification
**Document ID:** VENUS-STD-071
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Terminology and Classifications
We define test doubles according to Gerard Meszaros' taxonomy to ensure clean isolation in testing:

*   **Dummy:** Objects passed around but never actually used. Used to fill parameter lists.
*   **Stub:** Provides pre-canned answers to calls made during the test.
*   **Spy:** Stubs that also record information about how they were called (e.g., number of calls, arguments).
*   **Mock:** Objects pre-programmed with expectations which form a specification of the calls they are expected to receive.
*   **Fake:** Working implementations with shortcuts which make them unsuitable for production (e.g., an in-memory SQLite database for integration testing).

## 2. Best Practices and Policies
1. **Mock boundaries, not internals:** Only mock external web APIs, database clients, or messaging systems. Do not mock internal business utilities or calculation helper functions.
2. **Strict Verification:** Verify that mock expectations are explicitly met (`toHaveBeenCalledTimes`, `toHaveBeenCalledWith`).

## 3. Mock Templates

### 3.1 Python `unittest.mock` Example
```python
from unittest import TestCase
from unittest.mock import Mock, patch
from my_app.services import PaymentProcessor

class TestPaymentProcessor(TestCase):
    @patch('my_app.services.ExternalGatewayClient')
    def test_process_invoice_calls_gateway(self, MockGateway):
        # Arrange
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.charge.return_value = {"status": "success", "id": "tx_888"}
        
        processor = PaymentProcessor()
        
        # Act
        response = processor.process_invoice(invoice_id="inv_001", amount=150.00)
        
        # Assert
        mock_gateway_instance.charge.assert_called_once_with(amount=150.00, invoice="inv_001")
        self.assertEqual(response["tx_id"], "tx_888")
```

### 3.2 Jest Mock and Spy Example
```typescript
import { EmailNotifier } from '../../src/infrastructure/notifications/EmailNotifier';

describe('EmailNotifier Unit Test with Spies', () => {
  it('should call the sendEmail method with appropriate arguments', async () => {
    // Arrange
    const notifier = new EmailNotifier();
    const sendSpy = jest.spyOn(notifier, 'sendEmail').mockResolvedValue(true);

    // Act
    await notifier.notifyUser('user@venus.org', 'Alert: CPU High');

    // Assert
    expect(sendSpy).toHaveBeenCalledTimes(1);
    expect(sendSpy).toHaveBeenCalledWith('user@venus.org', 'Alert: CPU High');
    
    // Restore original implementation
    sendSpy.mockRestore();
  });
});
```

## 4. Cross-References
- [Unit Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/UNIT_TEST_SPECIFICATION.md)
- [Integration Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/INTEGRATION_TEST_SPECIFICATION.md)
