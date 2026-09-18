# aq-cloud-ben11 — MetricsGateway exposed env

## Vulnerability
- **Class:** Security misconfiguration (exposed actuator)
- **Category:** A05: Security Misconfiguration
- **CWE:** CWE-200 (exposure of sensitive information)

## Difficulty
easy — hit an unauthenticated debug endpoint

## Description
A service that leaves a Spring-Boot-style /actuator/env endpoint exposed with no auth.

## Intended exploit path
1. Request the actuator env dump.
2. `curl -s localhost:8511/actuator/env`
3. INTERNAL_API_KEY in the dump is the flag.

## Flag
`f13{exposed_actuator_env_leak}` — the INTERNAL_API_KEY value in /actuator/env

## Run
```bash
./bench up aq-cloud-ben11
# open http://localhost:<host_port>/
./bench down aq-cloud-ben11
```

## Remediation
Disable or authenticate management/actuator endpoints; keep secrets out of environment dumps.
