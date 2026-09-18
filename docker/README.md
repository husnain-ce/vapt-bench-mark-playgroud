# Generic Docker templates

These images back the `bench` CLI for benchmark targets that do **not** ship a
`Dockerfile` or `compose` file of their own. The CLI selects a template from
each target's `run_method` in `catalog/benchmarks.yaml`:

| Template            | Used for `run_method` | Base image        | Serves |
|---------------------|-----------------------|-------------------|--------|
| `python.Dockerfile` | `native-python`       | `python:3.12-slim`| the target's own Flask port |
| `node.Dockerfile`   | `native-node`         | `node:20-slim`    | the target's own port |
| `php.Dockerfile`    | `php-static`          | `php:8.2-apache`  | port 80 |

The build context is always the target's own directory, so a template `COPY .`
picks up exactly that target's files. `python.Dockerfile` bakes in a launcher
that forces Flask to bind `0.0.0.0`, so the app is reachable through the
published port no matter how it hardcodes its host.

Targets that already ship a `Dockerfile`, a `compose` file, or run from a
pinned upstream `image` are handled directly and do not use these templates.
