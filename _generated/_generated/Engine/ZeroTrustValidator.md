# ZeroTrustValidator

**Type**: Engine
**ID**: `VENUS-ENGI-2d9626017b90`

Validates zero trust boundaries across all system interfaces

## Inputs

- `network_topology`: `NetworkMap`
- `identity_providers`: `IdentityProvider[]`

## Outputs

- `trust_report`: `ZeroTrustReport`
- `violations`: `PolicyViolation[]`

## Validation

- `no_implicit_trust` (severity: critical)
- `all_traffic_encrypted` (severity: critical)

## Produces

- ZERO_TRUST_REPORT
