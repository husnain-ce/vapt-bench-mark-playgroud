# API targets

**14 targets** (`API/aq-api-ben01` … `aq-api-ben14`). Host ports: **8301–8314**.

```bash
./bench list --domain api
./bench up aq-api-ben08
```

## How they run

A mix of self-contained Flask/Node services (`app.py`, `server.js`) and larger
projects that ship their own `Dockerfile` or `docker-compose` file (for
example the Tiredful-API, VAmPI, and crAPI-style targets). `bench` picks the
right strategy from the catalog.

Each target carries a `Guide.md` and/or `Readme.md` describing the API, the
intended vulnerabilities (broken object-level authorization, injection, mass
assignment, JWT flaws, and so on), and example requests.

## Notes

- `aq-api-ben04` (a Laravel app) and `aq-api-ben14` (an Ansible-provisioned
  target) are flagged `needs_review`: they need their own setup steps, which
  their directories document. They are not auto-hosted by `bench`.
