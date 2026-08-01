# gRPC Proto Contract
**Document ID:** VENUS-STD-028
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

```protobuf
syntax = "proto3";

package venus.transactions.v1;

option go_package = "github.com/venus/transactions/v1;txv1";

service TransactionService {
  rpc InitiateTransaction (InitiateTransactionRequest) returns (InitiateTransactionResponse);
  rpc GetTransactionStatus (GetTransactionStatusRequest) returns (GetTransactionStatusResponse);
}

message InitiateTransactionRequest {
  string source_account_id = 1;
  string target_account_id = 2;
  double amount = 3;
}

message InitiateTransactionResponse {
  string transaction_id = 1;
  string status = 2;
}

message GetTransactionStatusRequest {
  string transaction_id = 1;
}

message GetTransactionStatusResponse {
  string transaction_id = 1;
  string status = 2;
  string error_message = 3;
}
```
