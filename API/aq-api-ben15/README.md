# aq-api-ben15 — OrderService BOLA/IDOR

## Vulnerability
- **Class:** Broken Object Level Authorization (IDOR)
- **Category:** API1 / A01: Broken Access Control
- **CWE:** CWE-639 (authorization bypass via user-controlled key)

## Difficulty
easy — change the id in the path

## Description
An order API. /api/users/<id>/orders returns any user's orders with no ownership check.

## Intended exploit path
1. You are user 1. Request another user's orders.
2. `curl -s localhost:8315/api/users/2/orders`
3. User 2's order note contains the flag.

## Flag
`f13{bola_idor_other_user}` — inside user 2's order

## Run
```bash
./bench up aq-api-ben15
# open http://localhost:<host_port>/
./bench down aq-api-ben15
```

## Remediation
Enforce that the authenticated caller owns the requested object id before returning it.
