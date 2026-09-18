# Security & safe use

These targets are **intentionally vulnerable**. Treat them the way you would
treat live malware samples: useful in a lab, dangerous anywhere else.

## Golden rules

1. **Never expose a target to an untrusted network.** No public internet, no
   shared office LAN, no bridged VM networking. Some of these (for example
   Metasploitable 2) have been found and compromised in the wild within minutes
   of being reachable.
2. **Run on an isolated host or segment.** A dedicated VM, an air-gapped lab
   box, or a host whose Docker bridge is not routed anywhere sensitive.
3. **Bind to localhost when you can.** `bench` publishes ports on all
   interfaces by default (Docker's behaviour). If your host is multi-homed,
   put it behind a firewall or bind Docker to loopback.
4. **These images ship real-looking secrets.** Flags, fake AWS keys, hardcoded
   passwords, and PII-shaped sample data are part of the exercises. They are
   fake, but scanners and secret-detectors will (correctly) flag them. Do not
   reuse any credential you see here anywhere real.
5. **Tear down when done.** `./bench down --all` removes every container and
   volume `bench` created.

## Isolation with Docker

- Each target runs in its own container; `bench` gives compose targets their own
  isolated Compose project so they cannot see each other's networks.
- Prefer running the whole playground on a disposable VM. If a target is
  compromised during testing, you throw the VM away, not your workstation.
- Do not mount host paths into these containers beyond what a target's own
  compose file already declares.

## Data and secrets

- The repository's `.gitignore` already excludes `.env`, `*.key`, `*.pem`,
  `*credential*`, and database artifacts so live secrets are not committed.
- Sample "secrets" that are part of a challenge (e.g. `flag.txt`,
  `credentials.json` with `AKIAIOSFODNN7EXAMPLE`) are intentionally present.
- If you add a target, never commit a **real** secret. Use obviously-fake
  placeholder values, following the existing targets.

## Legal

Use these targets only against infrastructure you own or are explicitly
authorised to test. You are responsible for complying with all applicable laws
and with the terms of any environment you run them in.
