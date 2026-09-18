# Cloud targets

**10 targets** (`Cloud/aq-cloud-ben01` … `aq-cloud-ben10`). Host ports: **8501–8510**.

```bash
./bench list --domain cloud
./bench up aq-cloud-ben01
curl http://localhost:8501/
```

## How they run

These are self-contained Flask services that **faithfully emulate** a cloud
service or attack surface locally — no cloud account, no credentials, no real
provider calls. Examples:

- `aq-cloud-ben01` — a minimal S3 API with public read/write buckets
- `aq-cloud-ben04` / `ben8` / `ben9` — SSRF against a metadata service
- `aq-cloud-ben07` — an unauthenticated kubelet API
- `aq-cloud-ben10` — a CI/CD pipeline secret-leak lab (a runner, not a service)

`bench` wraps them with `docker/python.Dockerfile`; the baked-in launcher
forces the Flask bind to `0.0.0.0` so each is reachable on its host port.

Every target ships a `Guide.md`/`Readme.md` with a verified exploit walk-through
(usually plain `curl`) and remediation notes.

## Notes

- `aq-cloud-ben10` runs a pipeline exploit locally (`python3 runner.py ...`)
  rather than serving HTTP; it is flagged `needs_review` and run from its own
  directory per its README, not via `bench up`.
