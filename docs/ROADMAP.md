# Roadmap: growing the corpus

The point of the tooling (catalog, `bench`, manifests, proxy/tunnel, CI) is to
make adding targets cheap and safe so the repo can grow without turning into a
pile of one-off directories. This is the ongoing plan, tiered by priority. The
numbers come from [AUDIT.md](AUDIT.md); re-run `python3 tools/audit.py` to
refresh them.

## Tier 1 — Critical (unblock what exists)

- **Fix the `needs_review` targets.** A handful can't be auto-hosted (broken
  Dockerfile, Ansible/Laravel setup, a CLI-only lab). Fix or explicitly document
  each so `bench up` either works or clearly says "run it this way."

## Tier 2 — High (reproducibility)

- **Pin every base image.** The audit lists targets on `:latest` or EOL distros.
  Non-reproducible builds rot. Pin them to a specific tag as they are touched.

## Tier 3 — Medium (contribution readiness)

- **Backfill `benchmark.yml`** across the corpus so every target is declarative,
  not heuristic. Start with the most-hosted ones.
- **Add a README** to every target missing one, using
  [the README template](../templates/TARGET_README_TEMPLATE.md).
- **Declare difficulty** everywhere so the difficulty tables are meaningful.

## Tier 4 — Low (classification + breadth)

- **Sharpen `vuln_class`** so OWASP mapping stops saying `Uncategorised`.
- **Fill category gaps.** Aim for balanced OWASP Top 10 and API Top 10 coverage;
  the audit's category table shows where the corpus is thin.

## How we keep pushing

1. Someone proposes a target (**New machine** issue) or opens a PR directly.
2. `./bench new` scaffolds it; the author fills in the app + manifest + README.
3. CI validates the manifest, checks catalog sync, and builds the changed target.
4. Merge. `bench` hosts it; the audit picks it up on the next run.

Every merged target should leave the coverage scorecard in [AUDIT.md](AUDIT.md)
the same or better. That is the one metric to watch as the repo scales.
