# For developers: packaging a machine

You take a vulnerability (yours, or one a researcher handed you) and turn it into
a self-contained, Dockerized target the `bench` CLI can host and expose. This is
the packaging side of the [TARGET_SPEC.md](TARGET_SPEC.md) contract.

## The 5-minute path

```bash
./bench new web --template compose --author your-handle   # or: dockerfile | python
# -> creates Web/aq-web-benNN/ with benchmark.yml + a build recipe + README
```

Then:

1. Drop your app in the new directory.
2. Serve it on the `port` you set in `benchmark.yml`, bound to `0.0.0.0`.
3. Fill in `benchmark.yml` and the README.
4. Register and test:

```bash
python3 tools/catalog.py     # register in the catalog
./bench up <id> && curl http://localhost:<host_port>/
./bench down <id>
./bench validate             # manifest + catalog checks (CI runs these)
```

## Choosing a run method

| `run`           | Use when | You provide |
|-----------------|----------|-------------|
| `compose`       | multiple services (app + DB), or you want env/volumes | `docker-compose.yml` |
| `dockerfile`    | one container, custom build | `Dockerfile` |
| `image`         | a pinned upstream image is the target | `image: name:tag` |
| `native-python` | a single Flask app, no Dockerfile | `app.py` (+ `requirements.txt`) |
| `native-node`   | a single Node app, no Dockerfile | `server.js` |
| `php-static`    | self-contained PHP, no DB | PHP source |

`bench` wraps `native-*` and `php-static` with the generic images in
[`docker/`](../docker/); the Python one forces the Flask bind to `0.0.0.0` so
your app is always reachable.

## Reproducibility rules (enforced by review)

1. **Pin base images and upstream tags.** No `:latest`, no EOL distros. The
   audit ([AUDIT.md](AUDIT.md)) lists offenders — 23 targets currently fail this.
   `FROM python:3.12-slim`, not `FROM python:latest`.
2. **Build offline.** No network fetches at build time beyond package installs
   from the base image's package manager; vendor anything exotic.
3. **Declare the real port.** `port:` in the manifest must match what the app
   listens on inside the container, or `bench` maps the wrong port.
4. **One command up, one command down.** If `./bench up <id>` does not serve it
   and `./bench down <id>` does not remove it cleanly, it is not done.

## Multi-port (network) targets

A target that exposes several services declares them in the manifest:

```yaml
run: dockerfile
ports: [8000, 6379]
```

`bench` maps each container port to a host port from the target's block
(e.g. `9010->8000`, `9011->6379`). Use `run: dockerfile` or `compose` so
you control the `EXPOSE`d ports and how each service binds `0.0.0.0`.

## Ports

You do not pick a host port. `bench` assigns a collision-free one from the
domain range (Web 8101+, API 8301+, Cloud 8501+) and, for `compose` targets,
remaps your published port onto it automatically. Set `host_port` in the
manifest only if you need a fixed one.

## Exposing it

Once it hosts, it can go behind the nginx proxy and a Cloudflare tunnel with no
extra work on your part — see [TUNNELING.md](TUNNELING.md). Keep `expose: true`
(the default) in the manifest.

## Before you open the PR

```bash
./bench validate        # manifest schema + catalog in sync
./bench doctor          # no port collisions
python3 tools/audit.py  # optional: see where your target lands in the audit
```

Commit the regenerated `catalog/benchmarks.yaml` and `docs/CATALOG.md` with your
target. The PR template's checklist mirrors this list. CI runs `validate` and
builds changed targets on every PR.
