# aq-web-ben68 — QuickCart checkout

## Vulnerability
- **Class:** Business logic / insecure design
- **Category:** A04: Insecure Design
- **CWE:** CWE-840 (business logic errors)

## Difficulty
medium — requires spotting that quantity is unvalidated

## Description
A checkout API. The total is sum(price*qty) minus coupons; quantity is never validated.

## Intended exploit path
1. POST an item with a negative quantity so the total goes <= 0.
2. `curl -s localhost:8168/checkout -H "Content-Type: application/json" -d '{"items":[{"price":100,"qty":-5}]}'`
3. The response includes the flag.

## Flag
`f13{business_logic_negative_total}` — returned by /checkout on a non-positive total

## Run
```bash
./bench up aq-web-ben68
# open http://localhost:<host_port>/
./bench down aq-web-ben68
```

## Remediation
Validate quantity as a positive integer; reject non-positive totals server-side; never trust client-supplied prices.
