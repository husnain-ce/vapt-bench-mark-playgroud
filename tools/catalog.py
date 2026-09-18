#!/usr/bin/env python3
"""Benchmark catalog scanner and generator.

Walks the benchmark domain directories, classifies every target by how it
runs, detects the container port it serves on, assigns a stable and
collision-free host port, and writes the machine-readable catalog plus the
human-readable catalog table.

Outputs
-------
- ``catalog/benchmarks.yaml`` : source of truth consumed by the ``bench`` CLI.
- ``docs/CATALOG.md``         : rendered table of every target.

The scanner is deliberately conservative: when it cannot determine a fact it
records a sensible default and flags the target with ``needs_review: true``
instead of guessing silently. Re-running the scanner never discards curated
fields (see MERGE_KEYS) that a human has edited by hand.

Usage
-----
    python3 tools/catalog.py            # regenerate catalog + docs/CATALOG.md
    python3 tools/catalog.py --check    # fail if regeneration would change files
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a hard dependency
    sys.exit("PyYAML is required: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent

# Domains that produce network services we can containerise and host.
# `block` is the host-port spacing per target (network targets are multi-port,
# so they reserve a block of ports each).
NETWORK_DOMAINS = {
    "Web": {"key": "web", "port_base": 8100, "block": 1},
    "API": {"key": "api", "port_base": 8300, "block": 1},
    "Cloud": {"key": "cloud", "port_base": 8500, "block": 1},
    "AI": {"key": "ai", "port_base": 8700, "block": 1},
    "Domain": {"key": "domain", "port_base": 8900, "block": 1},
    "Network": {"key": "network", "port_base": 9000, "block": 10},
}
# Domains that ship source or VM images and are hosted out-of-band.
OFFLINE_DOMAINS = {
    "android": "android",   # Gradle source -> emulator
    "ios": "ios",           # Xcode source -> simulator / device
    "Machines": "machine",  # VulnHub OVA -> VirtualBox
}

COMPOSE_NAMES = ("docker-compose.yml", "docker-compose.yaml",
                 "compose.yml", "compose.yaml")

# Fields the scanner will NOT overwrite once present in an existing catalog
# entry, so hand-curated corrections survive a regenerate.
MERGE_KEYS = ("title", "vuln_class", "difficulty", "internal_port",
              "run_method", "notes", "needs_review", "enabled")

BEN_RE = re.compile(r"ben(\d+)$")


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def find_first(target: Path, names: tuple[str, ...], max_depth: int = 2):
    """Return the shallowest matching file under *target*, or None."""
    best = None
    best_depth = 99
    for name in names:
        for match in target.rglob(name):
            depth = len(match.relative_to(target).parts)
            if depth <= max_depth and depth < best_depth:
                best, best_depth = match, depth
    return best


def has_file(target: Path, pattern: re.Pattern) -> bool:
    return any(pattern.match(c.name) for c in target.iterdir() if c.is_file())


def parse_compose_ports(compose: Path):
    """Return (host_port, container_port, service_name) for the first
    published service, or (None, None, None)."""
    try:
        data = yaml.safe_load(compose.read_text(errors="ignore")) or {}
    except yaml.YAMLError:
        return None, None, None
    services = data.get("services") or {}
    for name, svc in services.items():
        if not isinstance(svc, dict):
            continue
        for mapping in svc.get("ports", []) or []:
            host, container = _split_port(mapping)
            if container:
                return host, container, name
    return None, None, None


def _split_port(mapping) -> tuple[str | None, str | None]:
    text = str(mapping).strip().strip('"').strip("'")
    # forms: "8000:80", "127.0.0.1:8000:80", "80", "8000:80/tcp"
    text = text.split("/")[0]
    parts = text.split(":")
    parts = [p for p in parts if p != ""]
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    if len(parts) == 1:
        return None, parts[0]
    return None, None


def grep_int(paths, patterns):
    for path in paths:
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return int(m.group(1))
    return None


def detect_internal_port(target: Path, run_method: str) -> int | None:
    py = list(target.rglob("*.py"))[:20]
    js = list(target.rglob("*.js"))[:20]
    dockerfile = find_first(target, ("Dockerfile",))
    if dockerfile:
        p = grep_int([dockerfile], [
            r"EXPOSE\s+(\d{2,5})",
            r"0\.0\.0\.0:(\d{2,5})",          # gunicorn -b 0.0.0.0:5000
            r"--port[= ]+(\d{2,5})",
            r"-p\s+(\d{2,5})",
            r":(\d{2,5})\"\s*,\s*\"?app",     # -b host:port app:app
        ])
        if p:
            return p
    port = grep_int(py, [
        r"app\.run\([^)]*port\s*=\s*(\d{2,5})",
        r"run\([^)]*port\s*=\s*(\d{2,5})",
        r"\.run\([^)]*port\s*=\s*(\d{2,5})",
        r"PORT[\"']?\s*[:=]\s*[\"']?(\d{2,5})",
        r"port\s*=\s*(\d{4,5})",
    ])
    if port:
        return port
    port = grep_int(js, [
        r"listen\(\s*(\d{2,5})",
        r"PORT\s*\|\|\s*(\d{2,5})",
        r"PORT\s*=\s*(\d{2,5})",
    ])
    if port:
        return port
    if run_method == "php-static":
        return 80
    if run_method == "native-node":
        return 3000
    if run_method == "native-python":
        return 8000
    return None


def classify(target: Path):
    """Return (run_method, compose_file, dockerfile, needs_review)."""
    compose = find_first(target, COMPOSE_NAMES)
    dockerfile = find_first(target, ("Dockerfile",))
    files = {c.name.lower() for c in target.iterdir() if c.is_file()}

    if compose:
        return "compose", compose, dockerfile, False
    if dockerfile:
        return "dockerfile", None, dockerfile, False
    if "server.js" in files or "index.js" in files:
        return "native-node", None, None, False
    if any(f in files for f in ("app.py", "server.py", "main.py")):
        return "native-python", None, None, False
    # PHP source with an index at top level -> serveable with generic php image
    if "index.php" in files:
        return "php-static", None, None, False
    # nested project (e.g. a chall/ or src/ subdir) with no top-level entry
    return "manual", None, None, True


def read_meta(target: Path):
    """Pull a title, vuln class and difficulty from the target's docs."""
    title = vuln = difficulty = None
    doc = None
    for name in ("README.md", "Readme.md", "readme.md", "Guide.md",
                 "CHALLENGE.md", "readme.txt"):
        cand = target / name
        if cand.exists():
            doc = cand
            break
    if doc is None:
        docs = sorted(target.glob("*.md"))
        doc = docs[0] if docs else None
    if doc is not None:
        text = doc.read_text(errors="ignore")
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                title = s.lstrip("#").strip()
                break
            if s and title is None and not s.startswith(("!", "[", "<", "```")):
                title = s
                break
        m = re.search(r"(?:\*\*Type:\*\*|Type:|Vulnerabilit(?:y|ies)[^\n:]*:)\s*(.+)",
                      text)
        if m:
            vuln = m.group(1).strip().strip("*").strip()[:80]
        m = re.search(r"(?:Difficulty[^\n:]*:|\*\*Difficulty\*\*)\s*\n?\s*(\w+)",
                      text, re.IGNORECASE)
        if m:
            difficulty = m.group(1).strip().capitalize()
    if title:
        title = re.sub(r"\s+", " ", title)[:90]
    return title, vuln, difficulty


def ben_index(name: str) -> int:
    m = BEN_RE.search(name)
    return int(m.group(1)) if m else 0


MANIFEST_NAME = "benchmark.yml"
VALID_DOMAINS = {"web", "api", "cloud", "android", "ios", "machine",
                 "ai", "domain", "network"}
VALID_RUN = {"compose", "dockerfile", "image", "native-python",
             "native-node", "php-static", "external", "manual"}


def load_manifest(target: Path) -> dict | None:
    """Load a target's benchmark.yml, or None if absent."""
    path = target / MANIFEST_NAME
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(errors="ignore"))
    except yaml.YAMLError:
        return {"_error": "invalid YAML"}
    return data if isinstance(data, dict) else {"_error": "not a mapping"}


def overlay_manifest(entry: dict, target: Path) -> None:
    """Overlay a target's declared benchmark.yml onto its scanned entry.

    A present manifest is authoritative: any field it declares wins over the
    heuristic guess. Fields it omits are left as scanned. A target that
    declares a manifest is never flagged needs_review.
    """
    m = load_manifest(target)
    if not m or "_error" in (m or {}):
        return
    entry["has_manifest"] = True
    field_map = {
        "title": "title", "vuln_class": "vuln_class", "difficulty": "difficulty",
        "run": "run_method", "port": "internal_port", "host_port": "host_port",
        "image": "image", "flag": "flag", "expose": "expose", "author": "author",
    }
    for src, dst in field_map.items():
        if src in m and m[src] not in (None, ""):
            entry[dst] = m[src]
    if "compose_file" in m and m["compose_file"]:
        entry["compose_file"] = rel(target / m["compose_file"])
    if isinstance(m.get("ports"), list) and m["ports"]:
        entry["internal_ports"] = [int(p) for p in m["ports"]]
        entry["internal_port"] = entry["internal_ports"][0]
    if entry.get("run_method") not in ("manual", "external"):
        entry["hostable"] = True
    entry["needs_review"] = False


def scan():
    entries = []
    for domain, cfg in NETWORK_DOMAINS.items():
        ddir = REPO / domain
        if not ddir.is_dir():
            continue
        for target in sorted(ddir.iterdir(), key=lambda p: ben_index(p.name)):
            if not target.is_dir() or target.name.startswith("."):
                continue
            idx = ben_index(target.name)
            run_method, compose, dockerfile, needs_review = classify(target)
            service_name = ""
            orig_host = ""
            internal = None
            if run_method == "compose" and compose is not None:
                host, container, service_name = parse_compose_ports(compose)
                orig_host = host or ""
                if container and str(container).isdigit():
                    internal = int(container)
            if internal is None:
                internal = detect_internal_port(target, run_method)
            if internal is None:
                internal = 80
                needs_review = True
            title, vuln, difficulty = read_meta(target)
            host_port = cfg["port_base"] + idx * cfg.get("block", 1)
            entry = {
                "id": target.name,
                "domain": cfg["key"],
                "path": rel(target),
                "title": title or target.name,
                "vuln_class": vuln or "",
                "difficulty": difficulty or "",
                "run_method": run_method,
                "host_port": host_port,
                "internal_port": int(internal),
                "compose_file": rel(compose) if compose else "",
                "compose_service": service_name or "",
                "dockerfile": rel(dockerfile) if dockerfile else "",
                "image": "",
                "hostable": run_method != "manual",
                "needs_review": needs_review,
                "enabled": True,
                "expose": run_method != "manual",
                "notes": "",
            }
            overlay_manifest(entry, target)
            # Multi-port targets: assign a host-port block from the domain range.
            if entry.get("internal_ports"):
                block = cfg["port_base"] + idx * cfg.get("block", 1)
                entry["host_ports"] = [block + i
                                       for i in range(len(entry["internal_ports"]))]
                entry["host_port"] = entry["host_ports"][0]
                entry["internal_port"] = entry["internal_ports"][0]
            entries.append(entry)

    # OWASP flagship suite: a single curated compose stack (DVWA + DB, Juice
    # Shop, WebGoat/WebWolf, BodgeIt, and nginx portals) on its own clean
    # 5200-5205 port range. Run as-is on its native ports rather than remapped.
    owasp_compose = REPO / "Web" / ".OWASP" / "docker-compose.host.yml"
    if owasp_compose.exists():
        entries.append({
            "id": "aq-web-owasp-suite",
            "domain": "web",
            "path": "Web/.OWASP",
            "title": "OWASP flagship suite (DVWA, Juice Shop, WebGoat, BodgeIt)",
            "vuln_class": "OWASP Top 10 (flagship apps)",
            "difficulty": "",
            "run_method": "compose",
            "host_port": 5200,
            "internal_port": 80,
            "compose_file": rel(owasp_compose),
            "compose_service": "aqsec-portal",
            "dockerfile": "",
            "image": "",
            "native_ports": True,
            "hostable": True,
            "needs_review": False,
            "enabled": True,
            "expose": True,
            "notes": "Portal on :5200; DVWA :5201, Juice :5202, WebGoat "
                     "(via proxy) :5203, BodgeIt :5204, WebWolf :5205. "
                     "Runs on its own native ports (not remapped).",
        })

    offline = []
    for domain, key in OFFLINE_DOMAINS.items():
        ddir = REPO / domain
        if not ddir.is_dir():
            continue
        for target in sorted(ddir.iterdir(), key=lambda p: ben_index(p.name)):
            if not target.is_dir():
                continue
            title, vuln, difficulty = read_meta(target)
            offline.append({
                "id": target.name,
                "domain": key,
                "path": rel(target),
                "title": title or target.name,
                "vuln_class": vuln or "",
                "difficulty": difficulty or "",
                "run_method": "external",
                "hostable": False,
                "expose": False,
            })
    return entries, offline


def validate_all():
    """Validate every target's manifest (if present). Returns a list of
    human-readable error strings; empty means valid."""
    errors = []
    for domain in list(NETWORK_DOMAINS) + list(OFFLINE_DOMAINS):
        ddir = REPO / domain
        if not ddir.is_dir():
            continue
        for target in sorted(ddir.iterdir()):
            if not target.is_dir() or target.name.startswith("."):
                continue
            m = load_manifest(target)
            if m is None:
                continue  # heuristic-only target; allowed for existing targets
            where = rel(target / MANIFEST_NAME)
            if "_error" in m:
                errors.append(f"{where}: {m['_error']}")
                continue
            if m.get("id") and m["id"] != target.name:
                errors.append(f"{where}: id '{m['id']}' != folder '{target.name}'")
            dom = m.get("domain")
            if dom and dom not in VALID_DOMAINS:
                errors.append(f"{where}: invalid domain '{dom}'")
            run = m.get("run")
            if run and run not in VALID_RUN:
                errors.append(f"{where}: invalid run '{run}'")
            if run == "compose" and not m.get("compose_file"):
                errors.append(f"{where}: run: compose requires compose_file")
            if run == "image" and not m.get("image"):
                errors.append(f"{where}: run: image requires image")
            port = m.get("port")
            if port is not None and not (isinstance(port, int) and 1 <= port <= 65535):
                errors.append(f"{where}: port must be 1-65535")
            ports = m.get("ports")
            if ports is not None:
                if not isinstance(ports, list) or not ports:
                    errors.append(f"{where}: ports must be a non-empty list")
                elif not all(isinstance(p, int) and 1 <= p <= 65535 for p in ports):
                    errors.append(f"{where}: every ports entry must be 1-65535")
            diff = m.get("difficulty")
            if diff and str(diff).lower() not in ("easy", "medium", "hard"):
                errors.append(f"{where}: difficulty must be easy|medium|hard")
    return errors


def merge_existing(new_entries, catalog_path: Path):
    if not catalog_path.exists():
        return new_entries
    old = yaml.safe_load(catalog_path.read_text()) or {}
    old_by_id = {e["id"]: e for e in old.get("targets", [])}
    for entry in new_entries:
        prev = old_by_id.get(entry["id"])
        if not prev:
            continue
        for key in MERGE_KEYS:
            # keep a human's non-empty curated value over a fresh guess
            if key in prev and prev[key] not in (None, "", []):
                if entry.get(key) in (None, "", []) or prev.get("_locked"):
                    entry[key] = prev[key]
    return new_entries


def write_catalog(entries, offline, path: Path):
    counts = {}
    for e in entries + offline:
        counts[e["domain"]] = counts.get(e["domain"], 0) + 1
    doc = {
        "meta": {
            "generated_by": "tools/catalog.py",
            "hostable_domains": [c["key"] for c in NETWORK_DOMAINS.values()],
            "offline_domains": sorted(set(OFFLINE_DOMAINS.values())),
            "counts": dict(sorted(counts.items())),
            "total": len(entries) + len(offline),
        },
        "targets": entries,
        "offline": offline,
    }
    text = ("# Auto-generated by tools/catalog.py -- edit curated fields in place;\n"
            "# they are preserved on regenerate. Do not hand-edit host_port/path.\n"
            + yaml.safe_dump(doc, sort_keys=False, width=100))
    path.write_text(text)
    return doc


def render_catalog_md(doc, path: Path):
    lines = ["# Benchmark Catalog", "",
             f"Auto-generated from `catalog/benchmarks.yaml` by `tools/catalog.py`. "
             f"Total targets: **{doc['meta']['total']}**.", "",
             "Counts by domain: "
             + ", ".join(f"`{k}` {v}" for k, v in doc["meta"]["counts"].items())
             + ".", ""]

    lines += ["## Hostable targets (Docker)", "",
              "These run as containers via the `bench` CLI on the listed host port.",
              "",
              "| ID | Domain | Port | Run method | Vulnerability | Difficulty |",
              "|----|--------|------|-----------|---------------|------------|"]
    for e in doc["targets"]:
        flag = " ⚠️" if e.get("needs_review") else ""
        vuln = (e["vuln_class"] or e["title"]).replace("|", "\\|")[:60]
        lines.append(
            f"| `{e['id']}` | {e['domain']} | {e['host_port']} | "
            f"{e['run_method']}{flag} | {vuln} | {e['difficulty'] or '—'} |")

    lines += ["", "⚠️ = scanner could not fully determine run method or port; "
              "verify before relying on it.", "",
              "## Offline targets (built / run out-of-band)", "",
              "Source-only or VM targets. See the per-domain guides under "
              "`docs/domains/` for build and run steps.", "",
              "| ID | Domain | Target | Difficulty |",
              "|----|--------|--------|------------|"]
    for e in doc["offline"]:
        title = e["title"].replace("|", "\\|")[:70]
        lines.append(f"| `{e['id']}` | {e['domain']} | {title} | "
                     f"{e['difficulty'] or '—'} |")
    lines.append("")
    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if outputs would change")
    ap.add_argument("--validate", action="store_true",
                    help="validate target manifests; exit non-zero on errors")
    args = ap.parse_args()

    catalog_path = REPO / "catalog" / "benchmarks.yaml"
    md_path = REPO / "docs" / "CATALOG.md"

    if args.validate:
        errs = validate_all()
        if errs:
            print("manifest validation FAILED:")
            for e in errs:
                print(f"  - {e}")
            sys.exit(1)
        print("all target manifests valid")
        sys.exit(0)

    entries, offline = scan()
    entries = merge_existing(entries, catalog_path)

    if args.check:
        import io
        prev_cat = catalog_path.read_text() if catalog_path.exists() else ""
        prev_md = md_path.read_text() if md_path.exists() else ""
        # render to memory
        doc = {
            "meta": {}, "targets": entries, "offline": offline,
        }
        # cheap check: rewrite to temp strings
        tmp_cat = catalog_path.with_suffix(".yaml.tmp")
        write_catalog(entries, offline, tmp_cat)
        new_cat = tmp_cat.read_text()
        tmp_cat.unlink()
        changed = new_cat != prev_cat
        print("changed" if changed else "up-to-date")
        sys.exit(1 if changed else 0)

    doc = write_catalog(entries, offline, catalog_path)
    render_catalog_md(doc, md_path)
    n_host = sum(1 for e in entries if e.get("hostable"))
    n_review = sum(1 for e in entries if e.get("needs_review"))
    n_manifest = sum(1 for e in entries if e.get("has_manifest"))
    print(f"Wrote {rel(catalog_path)}: {len(entries)} network entries "
          f"({n_host} hostable, {n_manifest} with manifest, "
          f"{n_review} need review), {len(offline)} offline.")
    print(f"Wrote {rel(md_path)}.")


if __name__ == "__main__":
    main()
