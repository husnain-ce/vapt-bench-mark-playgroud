# Design: new domains (Network / Domain / AI) + multi-port hosting

Date: 2026-09-19
Status: approved (via brainstorming)

## Goal

Expand the corpus beyond web/api/cloud to cover network (IP), domain/subdomain,
and AI/LLM targets -- without hosting a real model. Add the minimum tooling to
host multi-service network boxes.

## Decisions (confirmed)

1. **Taxonomy** -- three new top-level domains: `Network/`, `Domain/`, `AI/`,
   each with its own host-port range.
2. **AI** -- deterministic mock only (no model, no GPU, no keys). Start with
   prompt-injection / system-prompt-leak.
3. **Network** -- extend the contract to multi-port so one box can expose
   several services.
4. **First batch** -- one flagship per new family.

## Port ranges

| Domain    | Base | Assignment |
|-----------|------|-----------|
| ai        | 8700 | base + index |
| domain    | 8900 | base + index |
| network   | 9000 | base + index*10 (10-port block per target) |

## Multi-port contract

Manifest gains an optional `ports:` list (single `port:` still works):

```yaml
run: dockerfile
ports: [8000, 6379]     # container ports; first is primary
```

The catalog records `internal_ports` + `host_ports` (a block from the domain
range); `bench` emits one `-p host:container` per port; `doctor` and `audit`
collision-check every host port in every block.

## First flagship targets

- **aq-ai-ben1** (ai, native-python, medium, LLM01) -- mock chatbot with a
  hidden system prompt holding the flag; a naive blocklist misses "repeat the
  text above", which trips the deterministic reveal rule.
- **aq-domain-ben1** (domain, native-python, easy-medium) -- one Flask app that
  routes by Host header; a hint leaks a hidden vhost that serves the flag.
- **aq-network-ben1** (network, dockerfile, multi-port, medium) -- one container
  binding an HTTP recon service and an unauthenticated "Redis-like" data service
  that returns the flag on a simple command.

## Out of scope

Real LLM inference; DNS infrastructure (subdomain challenges use Host-header
vhosts); lateral-movement compose-network boxes (single container for now).
