# aq-domain-ben1 — AcmeCorp hidden vhost

## Vulnerability
- **Class:** Information disclosure via undocumented virtual host
- **Category:** A05: Security Misconfiguration
- **CWE:** CWE-200 (exposure of sensitive information)

## Difficulty
easy — enumerate subdomains, set the Host header

## Description
One app serving several virtual hosts by Host header. An undocumented "internal" vhost serves the flag; the public site leaks a hint.

## Intended exploit path
1. Read the hint: `curl -s localhost:8901/robots.txt` and the HTML comment on /.
2. Enumerate subdomains and set the Host header: `curl -s localhost:8901/ -H "Host: internal.acme.local"`
3. The internal vhost returns the flag.

## Flag
`f13{hidden_vhost_internal}` — served by the internal vhost

## Run
```bash
./bench up aq-domain-ben1
# open http://localhost:<host_port>/
./bench down aq-domain-ben1
```

## Remediation
Do not serve internal environments from public-facing infrastructure; require auth on non-public vhosts.
