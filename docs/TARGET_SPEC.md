# Target specification (the contribution contract)

Every target is a self-contained, Dockerized directory that declares itself
with a `benchmark.yml` manifest. New targets **must** ship a valid manifest;
it is checked in CI. The ~90 pre-existing targets are still supported through
scanner heuristics and are backfilled opportunistically.

## Directory layout

```
<Domain>/aq-<domain>-ben<NN>/
├── benchmark.yml        # required: the manifest (schema below)
├── Dockerfile           # or docker-compose.yml (one way to run it)
├── README.md            # vuln class, difficulty, intended exploit path
└── <your app files>
```

Domain folders: `Web/`, `API/`, `Cloud/`, `AI/`, `Domain/`, `Network/`
(hostable). `android/`, `ios/`, and `Machines/` are out-of-band (source / VM)
and are not containerised.

## `benchmark.yml` schema

| Field         | Required | Notes |
|---------------|----------|-------|
| `id`          | yes      | Must equal the folder name (`aq-<domain>-ben<NN>`). |
| `domain`      | yes      | `web` \| `api` \| `cloud` \| `ai` \| `domain` \| `network` \| `android` \| `ios` \| `machine`. |
| `title`       | yes      | One-line human title. |
| `vuln_class`  | yes      | Vulnerability class + CWE if known. |
| `difficulty`  | yes      | `easy` \| `medium` \| `hard`. |
| `run`         | yes      | `compose` \| `dockerfile` \| `image` \| `native-python` \| `native-node` \| `php-static`. |
| `port`        | yes*     | The container port the app serves on (*or `ports` for multi-port). |
| `ports`       | no       | A list of container ports for multi-service targets, e.g. `[8000, 6379]`; bench maps a host-port block. |
| `host_port`   | no       | Fixed host port; otherwise auto-assigned from the domain range. |
| `compose_file`| if compose | Path to the compose file, relative to the target dir. |
| `image`       | if image | Pinned upstream image (`name:tag`). |
| `flag`        | no       | The target's flag, if it uses one. |
| `expose`      | no       | Eligible for proxy/tunnel (default `true`). |
| `author`      | no       | Your handle. |

Example (`Cloud/aq-cloud-ben01/benchmark.yml`):

```yaml
id: aq-cloud-ben01
domain: cloud
title: "AWS S3 Public Loot"
vuln_class: "Public S3 bucket read/write; sensitive data exposure"
difficulty: easy
run: native-python
port: 9131
expose: true
author: aqsec
```

## Rules

1. **Self-contained & deterministic.** It must build and run offline with no
   external accounts. Pin base images and upstream tags.
2. **One clear way to run.** A `Dockerfile`, a `compose` file, a pinned
   `image`, or source that a generic template wraps (`native-python`,
   `native-node`, `php-static`).
3. **Bind `0.0.0.0`.** Serve on all interfaces inside the container (the
   `native-python` template forces this for you).
4. **Fake secrets only.** Flags and sample credentials must be obviously fake.
   Never commit a real secret, key, or `.env`.
5. **Document it.** The `README.md` states the vulnerability, difficulty, and
   intended exploit path.

## Validate before you push

```bash
python3 tools/catalog.py        # register your target
./bench validate                # manifest schema + catalog sync
./bench up <id> && curl ...      # prove it hosts
./bench down <id>
```
