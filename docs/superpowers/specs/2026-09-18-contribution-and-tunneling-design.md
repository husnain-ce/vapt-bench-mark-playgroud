# Design: contribution framework, per-target Docker contract, and tunneling

Date: 2026-09-18
Status: approved (options confirmed via brainstorming)

## Goal

Let anyone contribute a "machine" (target) that is self-contained, Dockerized,
auto-discovered, and exposable through nginx + cloudflared — without weakening
the catalog-driven hosting already in place.

## Decisions (confirmed)

1. **Docker scope** — the Docker-required contract applies to all new and
   existing network targets (Web/API/Cloud). The six VulnHub OVA VMs remain a
   documented non-Docker exception.
2. **Tunneling** — cloudflared, both modes: a zero-config **quick** tunnel
   (ephemeral `trycloudflare.com` URL) as the default, and an optional
   **named** tunnel on the maintainer's own domain (persistent subdomains).
3. **Routing** — **subdomain per target** (`<id>.<base-domain>`) through nginx;
   quick tunnels give each target its own ephemeral URL.
4. **Contract** — new targets **must** ship `benchmark.yml` (validated in CI);
   existing targets keep working via scanner heuristics and are backfilled
   opportunistically.

## The target contract

Each target directory declares itself with `benchmark.yml`:

```yaml
id: aq-web-ben68           # unique; matches the folder name
domain: web                # web | api | cloud | android | ios | machine
title: "Short human title"
vuln_class: "e.g. SQL injection (CWE-89)"
difficulty: easy           # easy | medium | hard
run: dockerfile            # compose | dockerfile | image | native-python | native-node | php-static | external
port: 80                   # the container port the app serves on
host_port: 8168            # optional; auto-assigned from the domain range if omitted
compose_file: docker-compose.yml   # required when run: compose
image: ""                  # required when run: image (pinned tag)
flag: "f13{...}"           # optional
expose: true               # eligible for proxy / tunnel
author: "your-handle"      # optional
```

The scanner treats a present manifest as authoritative and fills only the
fields it omits from heuristics. Missing/invalid manifests on **new** targets
fail CI; the ~90 existing targets fall back to heuristics unchanged.

## Components

- **Scanner (`tools/catalog.py`)** — loads `benchmark.yml`, overlays it on the
  heuristic entry, and validates manifests (`--check` / `bench validate`). Adds
  an `expose` field to each catalog entry.
- **Scaffolding (`bench new`)** — creates a new target from `templates/<run>/`
  with a filled `benchmark.yml`, a Dockerfile or compose skeleton, and a README,
  choosing the next free id in the domain.
- **Proxy (`bench proxy`)** — generates nginx server blocks (one per running,
  exposed target) that reverse-proxy `<id>.<base-domain>` to the target's
  published host port via `host.docker.internal`, using the X-Forwarded pattern
  already established in `Web/.OWASP`. Runs an nginx container from `deploy/`.
- **Tunnel (`bench tunnel`)** — `bench tunnel <id>` opens a cloudflared quick
  tunnel to that target's port; `bench tunnel --named` uses
  `deploy/cloudflared/config.yml` + credentials to route subdomains through the
  proxy on the maintainer's domain.
- **CI** — GitHub Actions validates manifests, checks catalog sync, and builds
  changed targets.

## Networking model

Targets keep running with published host ports (unchanged). nginx reaches them
at `host.docker.internal:<host_port>` (Linux: `--add-host host.docker.internal:
host-gateway`), so no shared Docker network or target changes are required.
cloudflared fronts either a single target's port (quick) or the nginx proxy
(named), so exposure is always one hop in front of what already works locally.

## Out of scope

Converting VulnHub VMs to containers; changing how existing targets run; any
authentication layer in front of targets (they are intentionally vulnerable and
must only be exposed deliberately, per docs/SECURITY.md).
