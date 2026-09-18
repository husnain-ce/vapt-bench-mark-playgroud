# For security researchers: designing a good machine

You bring the vulnerability. This guide is about turning a real bug class into a
clean, reproducible benchmark target that a scanner or a human can be tested
against. If you can package it too, read [for-developers.md](for-developers.md);
if not, hand a developer the vuln and this brief.

## What makes a good target

1. **One clear, intended vulnerability** (a target may have incidental extras,
   but the exercise is one thing done well). State it and its CWE.
2. **A deterministic solution path.** There is a specific way in; you can write
   it down step by step. If the path is luck, it is not a benchmark.
3. **A verifiable win.** A flag (`f13{...}`), a specific response, or a reachable
   file that proves exploitation. Benchmarks need a pass/fail signal.
4. **Self-contained.** No external accounts, no live third-party services, no
   internet at solve time. Emulate the surface locally (see the `Cloud/`
   targets, which fake AWS/K8s APIs with no cloud account).
5. **Realistic shape.** The vuln hides in plausible functionality, not behind a
   sign that says "exploit here." That is what makes it a fair scanner test.

## The brief you write (goes in the target's README)

- **Vulnerability class + CWE** — e.g. "SQL injection (CWE-89)".
- **Difficulty** — `easy` (single well-known bug, obvious surface), `medium`
  (needs chaining or discovery), `hard` (multi-step, non-obvious, or auth-gated).
- **Intended exploit path** — the steps you expect a solver to take.
- **The flag** and where it lives, if any.
- **Remediation** — one line on the fix (the `Cloud/` targets do this well).

## Difficulty rubric

| Level | Looks like |
|-------|-----------|
| easy   | One textbook bug on an obvious endpoint; no auth or trivial auth. |
| medium | Requires discovery (hidden param/endpoint), light chaining, or a bypass. |
| hard   | Multi-step chain, auth-gated, non-obvious entry, or a custom protocol. |

## Categories we track

Targets are mapped to the **OWASP Top 10 (2021)** and, for API targets, the
**OWASP API Security Top 10**. Say the class plainly in `vuln_class` so the
audit (`tools/audit.py`) categorises it correctly. Current coverage and gaps
are in [AUDIT.md](AUDIT.md) — pick an under-represented category if you want
your contribution to move the needle.

## Flags and fake secrets

- Flags use the `f13{...}` format (see existing targets). Keep them out of
  static files a scanner would trivially grep unless that IS the exercise.
- Every secret, key, or credential must be **obviously fake**. Never commit a
  real one. The repo's `.gitignore` blocks `.env`, `*.key`, `*.pem`, and
  `*credential*` as a backstop, but the responsibility is yours.

## Handing off

If you can Dockerize it, follow [for-developers.md](for-developers.md) and open
a PR. If you cannot, open a **New machine** issue (the template asks for exactly
the brief above) and a developer will package it. Either way, the
[TARGET_SPEC.md](TARGET_SPEC.md) contract is the destination.
