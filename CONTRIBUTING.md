# Contributing a benchmark target

## Naming & layout

Add your target under its domain folder, following the existing convention:

```
Web/aq-web-ben<N>/         API/aq-api-ben<N>/        Cloud/aq-cloud-ben<N>/
android/aq-android-ben<N>/ ios/aq-ios-ben<N>/        Machines/<Name>/
```

Use the next free `ben<N>` number in that domain.

## What to include

1. **A `README.md`** inside the target describing:
   - the vulnerability class / category (and CWE if you know it),
   - the difficulty,
   - the intended exploitation path (and a flag, if the target uses one).
2. **A way to run it**, in this order of preference for network targets:
   - a `docker-compose.yml` (best — declares ports, dependencies, env), or
   - a `Dockerfile`, or
   - a self-contained `app.py` / `server.js` / static PHP that one of the
     generic templates in [`docker/`](docker/) can wrap.
3. **Fake secrets only.** Flags and sample credentials must be obviously fake
   (see existing targets). Never commit a real secret, key, or `.env`.

Mobile (`android`/`ios`) and `Machines` targets ship source or a VM image with
build/download instructions in their README; they are not containerised.

## Register it in the catalog

Regenerate the catalog so the CLI and docs pick up your target:

```bash
python3 tools/catalog.py
```

Then check your new entry in `catalog/benchmarks.yaml`:

- If it is flagged `needs_review: true`, the scanner could not fully determine
  its run method or port. Fix `run_method`, `internal_port`, etc. by hand — your
  edits to curated fields are preserved on future regenerates.
- Verify it hosts: `./bench up <id>` then `curl` its port, then
  `./bench down <id>`.
- Run `./bench doctor` to confirm no port collisions.

## Before you open a PR

```bash
python3 tools/catalog.py --check   # catalog + docs/CATALOG.md are up to date
./bench doctor                     # environment + catalog sanity
```

Commit the regenerated `catalog/benchmarks.yaml` and `docs/CATALOG.md` together
with your target.
