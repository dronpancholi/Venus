# GraphQL Schema Specification
**Document ID:** VENUS-STD-027
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

```graphql
type Account {
  id: ID!
  ownerId: String!
  balance: Float!
  currency: String!
  status: AccountStatus!
}

enum AccountStatus {
  ACTIVE
  SUSPENDED
  CLOSED
}

type Transaction {
  id: ID!
  sourceAccountId: ID!
  targetAccountId: ID!
  amount: Float!
  status: String!
  timestamp: String!
}

type Query {
  getAccount(id: ID!): Account
  listTransactions(accountId: ID!, limit: Int): [Transaction!]!
}

type Mutation {
  createTransaction(sourceAccountId: ID!, targetAccountId: ID!, amount: Float!): Transaction!
}
```
