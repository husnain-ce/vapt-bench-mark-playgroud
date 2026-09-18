# Hosting targets with `bench`

`bench` is the single entry point for running the network targets (Web, API,
Cloud). It reads [`catalog/benchmarks.yaml`](../catalog/benchmarks.yaml) and
starts each target as a container on its assigned, collision-free host port.

## Prerequisites

- **Docker** 20.10+ and the **Docker Compose v2** plugin (`docker compose`)
- **Python** 3.8+ with **PyYAML** (`python3 -m pip install --user pyyaml`)
- A Docker daemon you can reach without `sudo` (or run `bench` with `sudo`)

Verify everything with:

```bash
./bench doctor
```

It reports the Docker version, whether the daemon is reachable, how many
targets are flagged for review, and confirms there are no host-port collisions.

## Everyday commands

```bash
./bench list                 # every hostable target, grouped by domain, with ports
./bench list --domain web    # one domain
./bench list --all           # include the out-of-band (mobile / VM) targets
./bench ports                # the full host -> container port map
./bench info aq-cloud-ben01   # one target's details and its URL

./bench up aq-cloud-ben01     # build/pull and start a target
./bench up aq-web-ben01 aq-api-ben08   # several at once
./bench up --domain cloud    # a whole domain
./bench up --all             # everything (heavy -- see the warning below)

./bench status               # running bench containers and compose projects
./bench logs aq-cloud-ben01   # last 80 log lines (add -f to follow)
./bench down aq-cloud-ben01   # stop and remove one target
./bench down --domain cloud  # a whole domain
./bench down --all           # stop and remove everything bench started
```

Target ids can be abbreviated to any unique suffix, so `./bench up ben1` works
when only one target ends in `ben1`.

## What happens on `up`

`bench` chooses a strategy from each target's `run_method` in the catalog:

| `run_method`     | Strategy |
|------------------|----------|
| `compose`        | Starts the target's own compose file under an isolated project `bench-<id>`, plus an auto-generated override (`.bench/<id>.override.yml`) that republishes its ports on the assigned host port. |
| `dockerfile`     | Builds the target's own `Dockerfile` (tagged `bench/<id>`) and runs it with `-p <host>:<container>`. |
| `image`          | Runs a pinned upstream image. |
| `native-python`  | Builds with `docker/python.Dockerfile`; a baked-in launcher forces Flask to bind `0.0.0.0`. |
| `native-node`    | Builds with `docker/node.Dockerfile`. |
| `php-static`     | Builds with `docker/php.Dockerfile` (Apache + mod_php on port 80). |
| `manual`         | Not auto-hostable; `bench` points you at the target's own directory. |

Containers `bench` creates are labelled `bench=1` and named `bench-<id>`, so
`./bench down --all` and `./bench status` can find them reliably.

## Ports

Host ports are assigned by domain so they never collide **with each other**:

| Domain | Host-port range |
|--------|-----------------|
| Web    | 8101–8167 (plus the OWASP suite on 5200–5205) |
| API    | 8301–8314 |
| Cloud  | 8501–8510 |

The container-internal port is whatever the target actually listens on; `bench`
maps `host_port -> internal_port`. See `./bench ports` for the exact map.

### If an assigned port is already used on your machine

`bench` guarantees no collisions among the benchmark targets, but it cannot
know about unrelated services already running on your host. If `up` fails with
`port is already allocated`, edit that target's `host_port` in
`catalog/benchmarks.yaml` and re-run `up`. To move a whole range, change the
`port_base` values in `tools/catalog.py` and regenerate:

```bash
python3 tools/catalog.py
```

## Troubleshooting

- **`port is already allocated`** — another process holds that host port. Change
  the target's `host_port` in the catalog (see above), or stop the other service.
- **A target's build fails** — some upstream targets ship Dockerfiles pinned to
  end-of-life base images or with broken build steps. `bench` surfaces the build
  error verbatim. Targets whose run method or port could not be determined
  automatically are flagged `needs_review: true` in the catalog and marked ⚠ in
  `./bench list`; treat those as "verify before relying on it."
- **Container starts but nothing answers** — check `./bench logs <id>`. A few
  targets need a database or environment file that their own README documents;
  read the target's directory for specifics.
- **`unknown target`** — run `./bench list` for exact ids.

## Bringing up everything at once

`./bench up --all` will build and pull up to ~90 images. That is a large amount
of disk, network, and CPU, and some upstream builds will fail (see above).
Prefer bringing up one target or one domain at a time. When you are done:

```bash
./bench down --all
```
