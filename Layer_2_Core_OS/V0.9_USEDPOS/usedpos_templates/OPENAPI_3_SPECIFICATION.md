# OpenAPI 3.0 Specification
**Document ID:** VENUS-STD-026
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

```yaml
openapi: 3.0.3
info:
  title: Project Venus Transaction API
  description: Core Transaction and Payment processing interface.
  version: 1.0.0
paths:
  /v1/transactions:
    post:
      summary: Initiate Transaction
      description: Initiates a new payment transaction across accounts.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TransactionRequest'
      responses:
        '202':
          description: Transaction accepted for processing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TransactionResponse'
        '429':
          description: Rate limit exceeded
components:
  schemas:
    TransactionRequest:
      type: object
      required:
        - sourceAccountId
        - targetAccountId
        - amount
      properties:
        sourceAccountId:
          type: string
          format: uuid
        targetAccountId:
          type: string
          format: uuid
        amount:
          type: number
          minimum: 0.01
    TransactionResponse:
      type: object
      properties:
        transactionId:
          type: string
          format: uuid
        status:
          type: string
          enum: [PENDING, COMPLETED, FAILED]
```
