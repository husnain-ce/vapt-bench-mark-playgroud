#!/usr/bin/env python3
"""In-depth corpus audit for the VAPT benchmark playground.

Reads catalog/benchmarks.yaml and the target directories and produces a
quantified health report at docs/AUDIT.md: coverage (README, manifest, flag,
difficulty), run-method mix, OWASP Top 10 categorisation, build-reproducibility
risk (loose/EOL base images), and a prioritised list of what to fix.

Re-run it any time the corpus changes:
    python3 tools/audit.py
    python3 tools/audit.py --check    # exit non-zero if docs/AUDIT.md is stale
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent

# OWASP Top 10 2021 keyword map (first match wins, most specific first).
OWASP = [
    ("A03: Injection", r"\b(sql|sqli|injection|xss|cross.site|command inject|rce|"
                       r"remote code|xxe|ssti|template inject|ldap inject|code inject)\b"),
    ("A10: SSRF", r"\bssrf|server.side request|metadata service\b"),
    ("A01: Broken Access Control", r"\b(idor|access control|authoriz|privilege|"
                                   r"path travers|directory travers|lfi|local file|forced brows)\b"),
    ("A07: Auth Failures", r"\b(auth|jwt|session|login|brute|credential|password)\b"),
    ("A02: Cryptographic Failures", r"\b(crypto|encrypt|hardcoded secret|cleartext|"
                                    r"weak hash|tls|plaintext)\b"),
    ("A05: Security Misconfiguration", r"\b(misconfig|cors|default cred|exposure|"
                                       r"disclosure|open bucket|public bucket|config)\b"),
    ("A08: Software & Data Integrity", r"\b(deseriali|ci/cd|pipeline|supply chain|"
                                       r"insecure deseriali)\b"),
    ("A06: Vulnerable Components", r"\b(cve-|log4|outdated|vulnerable (lib|component|dependency))\b"),
    ("A04: Insecure Design", r"\b(business logic|race condition|insecure design|mass assignment)\b"),
    ("A09: Logging & Monitoring", r"\b(logging|monitoring|audit trail)\b"),
]
# Non-reproducible or end-of-life base images.
EOL_BASE = re.compile(
    r"ubuntu:(1[4-9]|2[01])\.|:[^ ]*buster|:[^ ]*stretch|:[^ ]*jessie|"
    r"debian:[89]\b|python:2|node:1[0-4]\b|:latest\b", re.I)

DOC_NAMES = ("README.md", "Readme.md", "readme.md", "Guide.md", "readme.txt",
             "CHALLENGE.md")


def has_readme(path: str) -> bool:
    return any((REPO / path / n).exists() for n in DOC_NAMES)


def has_flag(path: str) -> bool:
    base = REPO / path
    for f in glob.glob(str(base / "**" / "flag*"), recursive=True):
        return True
    for f in list(glob.glob(str(base / "**" / "*"), recursive=True))[:500]:
        p = Path(f)
        if p.is_file() and p.stat().st_size < 200_000:
            try:
                if re.search(r"f13\{|CTF\{|flag\{|FLAG\{",
                             p.read_text(errors="ignore")[:20000]):
                    return True
            except OSError:
                pass
    return False


def owasp_of(text: str) -> str:
    t = (text or "").lower()
    for label, pat in OWASP:
        if re.search(pat, t):
            return label
    return "Uncategorised"


def build_risk(target: dict):
    """Return (level, notes) for build reproducibility."""
    path = REPO / target["path"]
    notes = []
    for df in glob.glob(str(path / "**" / "Dockerfile"), recursive=True):
        txt = Path(df).read_text(errors="ignore")
        for base in re.findall(r"(?im)^FROM\s+(\S+)", txt):
            if EOL_BASE.search(base):
                notes.append(base)
    if target.get("needs_review"):
        notes.append("needs_review")
    if not notes:
        return "ok", []
    if any("needs_review" == n for n in notes):
        return "high", sorted(set(notes))
    return "medium", sorted(set(notes))


def gather():
    doc = yaml.safe_load((REPO / "catalog" / "benchmarks.yaml").read_text())
    rows = []
    for e in doc["targets"]:
        readme_text = ""
        for n in DOC_NAMES:
            f = REPO / e["path"] / n
            if f.exists():
                readme_text = f.read_text(errors="ignore")[:4000]
                break
        cat = owasp_of(f"{e.get('vuln_class','')} {e.get('title','')} {readme_text}")
        level, notes = build_risk(e)
        rows.append({
            "id": e["id"], "domain": e["domain"],
            "run": e["run_method"], "host_port": e.get("host_port"),
            "difficulty": (e.get("difficulty") or "").lower(),
            "owasp": cat,
            "readme": has_readme(e["path"]),
            "manifest": bool(e.get("has_manifest")),
            "flag": has_flag(e["path"]),
            "risk": level, "risk_notes": notes,
            "needs_review": bool(e.get("needs_review")),
        })
    return doc, rows


def pct(n, d):
    return f"{n}/{d} ({round(100*n/d) if d else 0}%)"


def render(doc, rows) -> str:
    n = len(rows)
    L = [f"# Corpus Audit", "",
         f"Auto-generated by `tools/audit.py` on {date.today().isoformat()}. "
         f"Re-run after adding or changing targets.", "",
         f"**Hostable targets audited: {n}** "
         f"(plus {len(doc['offline'])} offline / out-of-band).", "",
         "## Coverage scorecard", "",
         "| Signal | Coverage | Gap |",
         "|--------|----------|-----|"]
    readme = sum(r["readme"] for r in rows)
    manifest = sum(r["manifest"] for r in rows)
    flag = sum(r["flag"] for r in rows)
    diff = sum(1 for r in rows if r["difficulty"] in ("easy", "medium", "hard"))
    L += [f"| Has README / guide | {pct(readme,n)} | {n-readme} missing |",
          f"| Has `benchmark.yml` manifest | {pct(manifest,n)} | {n-manifest} to backfill |",
          f"| Has a flag | {pct(flag,n)} | {n-flag} without a detectable flag |",
          f"| Declares difficulty | {pct(diff,n)} | {n-diff} unknown |", ""]

    # Run method
    L += ["## Run-method mix", "",
          "| Run method | Count |", "|-----------|-------|"]
    for k, v in Counter(r["run"] for r in rows).most_common():
        L.append(f"| `{k}` | {v} |")
    L.append("")

    # Domain x difficulty
    L += ["## Difficulty by domain", "",
          "| Domain | easy | medium | hard | unknown |",
          "|--------|------|--------|------|---------|"]
    dom = sorted({r["domain"] for r in rows})
    for dm in dom:
        c = Counter(r["difficulty"] for r in rows if r["domain"] == dm)
        unk = sum(v for k, v in c.items() if k not in ("easy", "medium", "hard"))
        L.append(f"| {dm} | {c.get('easy',0)} | {c.get('medium',0)} | "
                 f"{c.get('hard',0)} | {unk} |")
    L.append("")

    # OWASP
    L += ["## OWASP Top 10 (2021) coverage", "",
          "Heuristic mapping from each target's vulnerability class and README. "
          "`Uncategorised` means the audit could not classify it -- add a clearer "
          "`vuln_class` in the manifest.", "",
          "| Category | Count |", "|----------|-------|"]
    for k, v in sorted(Counter(r["owasp"] for r in rows).items(),
                       key=lambda kv: (kv[0] == "Uncategorised", kv[0])):
        L.append(f"| {k} | {v} |")
    L.append("")

    # Build risk
    risky = [r for r in rows if r["risk"] != "ok"]
    L += ["## Build-reproducibility risk", "",
          f"{len(risky)} target(s) use a loose/EOL base image or are flagged "
          f"`needs_review`. Loose tags (`:latest`, EOL distros) make builds "
          f"non-reproducible and may stop building over time. Pin them.", "",
          "| Target | Level | Notes |", "|--------|-------|-------|"]
    for r in sorted(risky, key=lambda x: (x["risk"] != "high", x["id"])):
        L.append(f"| `{r['id']}` | {r['risk']} | {', '.join(r['risk_notes'])} |")
    L.append("")

    # Missing README list
    no_doc = [r["id"] for r in rows if not r["readme"]]
    L += ["## Targets missing a README", "",
          f"{len(no_doc)} target(s). Every target should document its vuln class, "
          "difficulty, and intended exploit path.", "",
          "> " + (", ".join(f"`{i}`" for i in no_doc) if no_doc else "none") + "", ""]

    # Recommendations
    L += ["## Prioritised recommendations", "",
          "**Critical** -- unblock hosting",
          f"- Fix or document the {sum(r['needs_review'] for r in rows)} "
          "`needs_review` targets (broken/undetectable run method).",
          "",
          "**High** -- reproducibility",
          f"- Pin the {len(risky)} loose/EOL base images to a specific tag.",
          "",
          "**Medium** -- contribution readiness",
          f"- Backfill `benchmark.yml` on the {n-manifest} targets without one, "
          "starting with the most-used ones.",
          f"- Add a README to the {n-readme} targets missing one.",
          f"- Declare difficulty on the {n-diff} targets marked unknown.",
          "",
          "**Low** -- classification",
          "- Give `Uncategorised` targets a clearer `vuln_class` so OWASP "
          "mapping is accurate.", "",
          "See [CONTRIBUTING.md](../CONTRIBUTING.md) and "
          "[TARGET_SPEC.md](TARGET_SPEC.md) for how contributors close these gaps.",
          ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if docs/AUDIT.md is stale")
    args = ap.parse_args()
    out = REPO / "docs" / "AUDIT.md"
    doc, rows = gather()
    text = render(doc, rows)
    if args.check:
        prev = out.read_text() if out.exists() else ""
        # ignore the date line when comparing
        norm = lambda s: re.sub(r"on \d{4}-\d{2}-\d{2}", "on DATE", s)
        changed = norm(prev) != norm(text)
        print("stale" if changed else "up-to-date")
        sys.exit(1 if changed else 0)
    out.write_text(text)
    print(f"Wrote {out.relative_to(REPO)} "
          f"({len(rows)} targets audited).")


if __name__ == "__main__":
    main()
