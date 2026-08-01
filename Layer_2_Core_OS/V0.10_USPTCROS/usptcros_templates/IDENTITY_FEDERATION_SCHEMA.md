# USPTCROS Identity Federation Schema
**Document Link:** [Identity Federation Schema](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/IDENTITY_FEDERATION_SCHEMA.md)

## 1. Federation Metadata Interchange Spec
This schema defines metadata structures exchanged between trusted domains.

## 2. SAML Attribute Mapping Configuration Schema
```xml
<IdentityFederationConfig xmlns="urn:usptcros:iam:federation:v1">
  <IdentityProvider issuer="https://corp-identity.venus.local">
    <SigningCertificate Fingerprint="DE:AD:BE:EF:00:11:22:33:44:55:66:77:88:99:AA:BB" />
    <AttributeMapping>
      <Map Source="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress" Target="email" />
      <Map Source="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname" Target="firstName" />
      <Map Source="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname" Target="lastName" />
      <Map Source="http://schemas.microsoft.com/ws/2008/06/identity/claims/groups" Target="groups" />
    </AttributeMapping>
  </IdentityProvider>
</IdentityFederationConfig>
```

## 3. Mapping Assertions
All federated identities must be transformed to match internal group definitions:
* Enterprise Group `Venus-SecOps-Admins` maps to Local Role `SecurityAdmin`.
* Enterprise Group `Venus-Developers` maps to Local Role `Operator`.
