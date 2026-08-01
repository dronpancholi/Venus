# Template: Integration Map

## 1. Third-Party Integrations Directory
*Track all external API dependencies, webhook configs, and SDK dependencies.*

| Provider Name | API Purpose | Webhook Endpoint | SDK / Library Version | SLA target |
|---|---|---|---|---|
| **Stripe** | Credit card processing | `/v1/webhooks/stripe` | `stripe==8.0.0` (Python) | 99.99% |
| **OpenAI** | Context categorization | None | `openai==1.0.0` (Python) | 99.0% |
| **Postmark** | Transaction email routing| `/v1/webhooks/postmark`| REST API / raw request | 99.9% |

---

## 2. Integration Boundary Configuration
*   **Stripe Webhook Authentication**: Stripe signature validation configured at the gateway boundary.
*   **API Timeout Limits**: Enforced 5000ms HTTP connection timeout on all outbound requests to prevent worker thread hangs.
*   **Retries**: Exponential backoff (max 3 retries).
