# AQSEC Benchmarks

A catalog of **intentionally vulnerable**, purpose-built targets for security
testing and benchmarking — across web, API, cloud, and mobile (Android/iOS),
plus dedicated VulnHub-style pentest machines. Each target lives in its own
directory; a single command-line tool (`bench`) hosts any network target as a
container on a stable, collision-free port.

This repository supports benchmarking and comparative analysis of security
tools and manual methodology against the **OWASP Top 10**, the **OWASP API
Security Top 10**, and other common vulnerability classes. It follows the same
general idea as `xbow-engineering/validation-benchmarks`, but extends coverage
beyond web to API, cloud, mobile, and dedicated pentest machines.

> ⚠️ **These targets are deliberately insecure.** Run them only on an isolated
> host or network segment. Never expose them to the public internet. See
> [`docs/SECURITY.md`](docs/SECURITY.md).

---

## What's inside

| Domain      | Targets | Runs as | Hosting |
|-------------|:-------:|---------|---------|
| `Web`       | 67 + 4 OWASP | Docker (compose / Dockerfile / image / source) | `bench` CLI |
| `API`       | 14      | Docker (mixed) | `bench` CLI |
| `Cloud`     | 10      | Docker (native Python services) | `bench` CLI |
| `android`   | 19      | Android Studio / Gradle source | emulator (out-of-band) |
| `ios`       | 11      | Xcode source | simulator / device (out-of-band) |
| `Machines`  | 6       | VulnHub OVA VMs | VirtualBox (out-of-band) |

**90 network targets** (Web + API + Cloud + the four flagship OWASP apps) are
containerised and started through the `bench` CLI. The mobile and VM domains
ship source or disk images and are built and run out-of-band; the CLI lists
them and points at each one's build steps.

The authoritative inventory lives in [`catalog/benchmarks.yaml`](catalog/benchmarks.yaml),
rendered for humans in [`docs/CATALOG.md`](docs/CATALOG.md).

## Quick start

```bash
# 1. Prerequisites: Docker + Docker Compose v2, Python 3.8+, PyYAML
python3 -m pip install --user pyyaml

# 2. See what's available and where it will be served
./bench list
./bench ports

# 3. Start a target -- it comes up on its assigned host port
./bench up aq-cloud-ben01
curl http://localhost:8501/

# 4. Check what's running, then tear it down
./bench status
./bench down aq-cloud-ben01

# Bring up / tear down a whole domain
./bench up --domain cloud
./bench down --domain cloud
```

Run `./bench doctor` first if anything looks off — it checks Docker and the
catalog for you.

### Running a single target by hand

Every target still builds and runs on its own, without the CLI:

```bash
cd Web/aq-web-ben01
docker build -t aq-web-ben01 .
docker run -d -p 8080:80 aq-web-ben01
```

The `bench` CLI simply automates this across the whole corpus and assigns
non-colliding ports so you can run many at once.

### Exposing a target publicly (optional)

```bash
cloudflared tunnel --url http://localhost:<port>
```

For running many targets at once, a named tunnel on your own domain scales
further than the free `trycloudflare.com` URLs, which are rate-limited. Only do
this deliberately and with access control — see [`docs/SECURITY.md`](docs/SECURITY.md).

## How hosting works

Each target keeps working exactly as its author intended; `bench` is a thin,
catalog-driven layer on top:

- **Targets with their own `compose` file** are started under an isolated
  Compose project, with an auto-generated override that remaps their published
  ports onto the target's assigned host port. No collisions between targets.
- **Targets with their own `Dockerfile`** are built and run with the assigned
  port mapping.
- **Targets that are just source** (native Python/Flask, Node, or static PHP)
  are wrapped by a generic template from [`docker/`](docker/).
- **Flagship OWASP apps** (DVWA, Juice Shop, WebGoat, BodgeIt) run from pinned
  upstream images.

The full design is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md); the
hosting workflow and troubleshooting are in [`docs/HOSTING.md`](docs/HOSTING.md).

## Repository layout

```
.
├── bench                     # unified control CLI (Python, stdlib + PyYAML)
├── catalog/
│   └── benchmarks.yaml       # source of truth: every target, port, run method
├── docker/                   # generic Dockerfile templates for source-only targets
├── tools/
│   └── catalog.py            # scanner that (re)generates the catalog + CATALOG.md
├── docs/                     # documentation set (start at docs/README.md)
├── Web/  API/  Cloud/        # hostable network targets (per-target folders)
└── android/  ios/  Machines/ # out-of-band targets (source / VM images)
```

## Purpose / use cases

- Benchmarking security scanners and automated tools against a consistent,
  reproducible target set
- Comparative analysis of findings across the OWASP Top 10 and OWASP API
  Security Top 10
- Practicing initial access, privilege escalation, and lateral movement against
  the `Machines` targets
- Regression-testing custom tooling or detection rules as targets are added

## Documentation

- [`docs/README.md`](docs/README.md) — documentation index
- [`docs/HOSTING.md`](docs/HOSTING.md) — running targets with `bench`, troubleshooting
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the catalog + CLI fit together
- [`docs/CATALOG.md`](docs/CATALOG.md) — the full target inventory (generated)
- [`docs/SECURITY.md`](docs/SECURITY.md) — isolation and safe-use guidance
- [`docs/domains/`](docs/domains/) — per-domain notes (web, api, cloud, android, ios, machines)
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — adding a new target

## Disclaimer

These targets are intentionally vulnerable by design. Do not deploy them on a
public or production network, or expose them without proper isolation and
access control. Intended for authorised security research, benchmarking, and
educational use only. You are responsible for using them lawfully.
