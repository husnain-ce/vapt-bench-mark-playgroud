# aq-network-ben1 — AcmeCache exposed data service

## Vulnerability
- **Class:** Unauthenticated network service exposure (Redis-like)
- **Category:** A05: Security Misconfiguration (exposed service)
- **CWE:** CWE-306 (missing authentication for critical function)

## Difficulty
medium — port-scan, find the open data service, read it

## Description
A multi-service box: an HTTP admin page (port 8000) and an unauthenticated Redis-like service (port 6379) that hands out the flag.

## Intended exploit path
1. Scan the box; the HTTP page (mapped host port, container 8000) hints at redis on 6379.
2. Connect to the data service (container 6379): `printf "INFO\r\n" | nc localhost <host-port-for-6379>`
3. The service returns the flag with no authentication.

## Flag
`f13{exposed_redis_no_auth}` — returned by the unauthenticated data service

## Run
```bash
./bench up aq-network-ben1
# open http://localhost:<host_port>/
./bench down aq-network-ben1
```

## Remediation
Bind data services to localhost, require authentication, and never expose them to untrusted networks.
