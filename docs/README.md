# Documentation

Start here.

## Guides

- **[HOSTING.md](HOSTING.md)** — run targets with the `bench` CLI: commands,
  the port map, and troubleshooting. Read this first if you just want to spin
  up a target.
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — how the catalog, scanner, and CLI
  fit together, and how to extend them.
- **[SECURITY.md](SECURITY.md)** — isolation rules and safe-use guidance.
  These targets are intentionally vulnerable; read this before running anything.
- **[CATALOG.md](CATALOG.md)** — the full inventory of every target, its host
  port, run method, and vulnerability class. **Auto-generated** from
  `catalog/benchmarks.yaml`; do not edit by hand.

## Per-domain guides

| Domain | Guide | Hosting |
|--------|-------|---------|
| Web     | [domains/web.md](domains/web.md)         | `bench` CLI (Docker) |
| API     | [domains/api.md](domains/api.md)         | `bench` CLI (Docker) |
| Cloud   | [domains/cloud.md](domains/cloud.md)     | `bench` CLI (Docker) |
| Android | [domains/android.md](domains/android.md) | Android Studio / emulator |
| iOS     | [domains/ios.md](domains/ios.md)         | Xcode / simulator |
| Machines| [domains/machines.md](domains/machines.md)| VirtualBox (VulnHub VMs) |

## Regenerating the catalog

The catalog and `CATALOG.md` are produced by the scanner:

```bash
python3 tools/catalog.py          # regenerate after adding/changing a target
python3 tools/catalog.py --check  # CI: fail if they are out of date
```

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for adding a new target.
