# Contributing a target ("machine")

Anyone can add a target. Every target is a **self-contained, Dockerized**
directory that declares itself with a `benchmark.yml` manifest. The full
contract is in [docs/TARGET_SPEC.md](docs/TARGET_SPEC.md).

## 1. Scaffold it

```bash
./bench new web --template dockerfile --author your-handle
# templates: dockerfile (default) | compose | python
# creates Web/aq-web-benNN/ with benchmark.yml + a Dockerfile + README skeleton
```

Use `--domain web|api|cloud`. The next free id in that domain is chosen for you.

## 2. Build the target

- Put your intentionally vulnerable app in the new directory.
- Serve it on the `port` you declared in `benchmark.yml`, bound to `0.0.0.0`.
- Fill in `benchmark.yml` (title, vuln class, difficulty, flag) and the README
  (vulnerability, difficulty, intended exploit path).
- Use **fake secrets only**. Never commit a real secret, key, or `.env`.

Prefer, in order: your own `docker-compose.yml`, your own `Dockerfile`, or
self-contained source that a generic template wraps (`native-python`,
`native-node`, `php-static`).

## 3. Register and test it

```bash
python3 tools/catalog.py     # register it in the catalog + docs/CATALOG.md
./bench up <id>              # build and run on its assigned host port
curl http://localhost:<port> # confirm it serves
./bench down <id>
```

## 4. Validate before opening a PR

```bash
./bench validate             # manifest schema + catalog is in sync
./bench doctor               # no port collisions
```

Commit the regenerated `catalog/benchmarks.yaml` and `docs/CATALOG.md` along
with your target. CI runs the same `validate` on every PR.

## Naming & domains

- Hostable domains: `Web/`, `API/`, `Cloud/`, folder `aq-<domain>-ben<NN>`.
- Out-of-band domains (`android/`, `ios/`, `Machines/`) ship source or a VM
  image with build/download instructions in their README; they are not
  containerised and are documented, not hosted by `bench`.

## Exposing your target

Once it runs, it can be put behind the nginx proxy and a Cloudflare tunnel —
see [docs/TUNNELING.md](docs/TUNNELING.md). Keep `expose: true` in the manifest
(the default) to make it eligible.
