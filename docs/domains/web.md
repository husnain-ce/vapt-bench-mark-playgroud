# Web targets

**67 targets** (`Web/aq-web-ben01` … `aq-web-ben67`) plus the **flagship OWASP
suite** under `Web/.OWASP`.

All are hosted through the [`bench`](../HOSTING.md) CLI. Host ports: **8101–8167**
for the numbered targets, **5200–5205** for the OWASP suite.

## Running

```bash
./bench list --domain web
./bench up aq-web-ben01
./bench down aq-web-ben01
```

## How they run

The web corpus is the most heterogeneous. `bench` handles each shape:

- Most ship their own `docker-compose` file (started under an isolated project
  with a port override).
- Some ship a `Dockerfile` only.
- A few are static PHP or single-file Flask/Node apps, wrapped by the generic
  templates in [`docker/`](../../docker/).

## Flagship OWASP suite

A single curated compose stack (`Web/.OWASP/docker-compose.host.yml`) bundling
the classic OWASP training apps behind nginx portals, on its own port range:

```bash
./bench up aq-web-owasp-suite      # brings the whole stack up on 5200-5205
```

| App | URL |
|-----|-----|
| Portal (index) | http://localhost:5200 |
| DVWA           | http://localhost:5201 |
| Juice Shop     | http://localhost:5202 |
| WebGoat (via proxy) | http://localhost:5203 |
| BodgeIt        | http://localhost:5204 |
| WebWolf        | http://localhost:5205 |

This target runs on its own native ports (it is not remapped), so it never
collides with the numbered web targets.

## Notes

- A handful of upstream targets pin end-of-life base images or need a database
  their README documents. Targets `bench` could not fully classify are marked
  `needs_review` in the catalog and ⚠ in `./bench list`.
- The vulnerability class for each target comes from its own README; open the
  target directory for the full brief and intended exploit path.
