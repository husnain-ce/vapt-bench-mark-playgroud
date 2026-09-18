# Network / IP targets

Multi-service "boxes" for network-recon challenges: port-scan, find an exposed
service, exploit it. Host ports: **9000s**, assigned in 10-port blocks per
target (these targets are multi-port).

```bash
./bench list --domain network
./bench up aq-network-ben1
./bench ports        # shows the host->container map for every port
```

## How they run

A target declares several container ports in its manifest:

```yaml
run: dockerfile
ports: [8000, 6379]
```

`bench` maps each to a host port from the target's block (e.g. 9010->8000,
9011->6379). One container (or compose stack) runs the services -- an HTTP recon
page plus an unauthenticated data service, for `aq-network-ben1`. The player
scans the mapped ports, finds the open service, and reads the flag.

Use `run: dockerfile` (or `compose`) for multi-port targets so you control the
`EXPOSE`d ports and how the services bind.
