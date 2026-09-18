# AQSEC Benchmarks

A collection of intentionally vulnerable, purpose-built targets for security testing and benchmarking — covering web, API, cloud, mobile (Android/iOS), IoT, and Active Directory-style machines. Each target lives in its own directory with its own Dockerfile, so it can be built and run in isolation.

## Overview

This repository is used for benchmarking and comparative analysis of security tools and manual testing methodology against the **OWASP Top 10**, the **OWASP API Security Top 10**, and other common vulnerability classes across multiple domains. It follows the same general idea as `xbow-engineering/validation-benchmarks`, but extends coverage beyond web to API, cloud, mobile, IoT, and dedicated pentest machines.

## Repository Structure

```
Benchmrks/
├── android/    aq-android-ben1 ... aq-android-ben19
├── API/        aq-api-ben1 ... aq-api-ben14
├── Cloud/      aq-cloud-ben1 ... aq-cloud-ben10
├── iOS/        aq-ios-ben1 ... aq-ios-ben11
├── IOT/        aq-iot-ben1 ... aq-iot-ben4
├── Machines/   Chronos, DoubleTrouble, Evilbox, Hacksudo, Metasploitable2, Momentum
├── mobile/     aq-mobile-ben1
└── Web/        aq-web-ben1 ... aq-web-ben67
```

## Prerequisites

- Docker
- (Optional) [cloudflared](https://github.com/cloudflare/cloudflared) — for exposing targets via Cloudflare Tunnel without opening inbound ports

## Quick Start

Build and run a single target:

```bash
cd Web/aq-web-ben1
docker build -t aq-web-ben1 .
docker run -d -p 8080:80 aq-web-ben1
```

Build and run every target in a category:

```bash
for dir in Web/*/; do
  name=$(basename "$dir")
  (cd "$dir" && docker build -t "$name" . && docker run -d --name "$name" -P "$name")
done
```

Adjust port mapping per target as needed to avoid collisions when running many containers at once.

### Exposing a target publicly (optional)

```bash
cloudflared tunnel --url http://localhost:<port>
```

For running many targets at once, a named tunnel on your own domain scales further than the free `trycloudflare.com` URLs, which are rate-limited.

## Purpose / Use Cases

- Benchmarking security scanners and automated tools against a consistent, reproducible target set
- Comparative analysis of findings across the OWASP Top 10 and OWASP API Security Top 10
- Practicing initial access, privilege escalation, and lateral movement against the `Machines` targets
- Regression-testing custom tooling or detection rules as targets are added

## Contributing

When adding a new target:
1. Create a new directory under the appropriate category, following the `aq-<category>-ben<N>` naming pattern (or a descriptive name for `Machines/`).
2. Include a self-contained `Dockerfile` in that directory.
3. Document the vulnerability class and intended entry point in a short `README.md` inside the target's own directory.

## Legal & Ethical Use

**Warning:** These targets are intentionally vulnerable by design. Do not deploy them on a public or production network, or expose them without proper isolation and access control. Intended for authorized security research, benchmarking, and educational use only.
