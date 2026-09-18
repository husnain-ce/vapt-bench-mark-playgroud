## What this adds

<!-- Which target(s) and vulnerability class. Link the proposal issue if any. -->

Closes #

## Contributor checklist

- [ ] Target lives in the right domain folder, named `aq-<domain>-ben<NN>`
- [ ] `benchmark.yml` present and filled (id, domain, title, vuln_class, difficulty, run, port)
- [ ] `README.md` documents vuln class, difficulty, and intended exploit path
- [ ] Base images / upstream tags are **pinned** (no `:latest`, no EOL distros)
- [ ] Self-contained: builds and runs offline, no external accounts
- [ ] Secrets/flags are obviously fake
- [ ] `./bench up <id>` serves it; `./bench down <id>` cleans up
- [ ] `python3 tools/catalog.py` run; `catalog/benchmarks.yaml` + `docs/CATALOG.md` committed
- [ ] `./bench validate` passes and `./bench doctor` shows no port collisions

## Notes for reviewers

<!-- Anything non-obvious: dependencies, why a specific base image, etc. -->
