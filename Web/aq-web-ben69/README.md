# aq-web-ben69 — AcmePortal JWT forgery

## Vulnerability
- **Class:** Broken authentication (JWT alg:none)
- **Category:** A02: Cryptographic Failures / A07: Auth Failures
- **CWE:** CWE-347 (improper signature verification)

## Difficulty
medium — needs forging an unsigned JWT

## Description
A portal issuing JWT session tokens. /admin decodes tokens with signature verification disabled.

## Intended exploit path
1. Craft a JWT with header {"alg":"none"} and payload {"role":"admin"}, empty signature.
2. `curl -s localhost:8169/admin -H "Authorization: Bearer <forged-token>"`
3. The response contains the flag.

## Flag
`f13{jwt_alg_none_forgery}` — returned by /admin for a role=admin token

## Run
```bash
./bench up aq-web-ben69
# open http://localhost:<host_port>/
./bench down aq-web-ben69
```

## Remediation
Verify the signature with a fixed allowlist of algorithms (never "none"); reject unsigned tokens.
