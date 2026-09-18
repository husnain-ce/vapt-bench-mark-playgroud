# Exposing targets: nginx proxy + cloudflared

`bench` can put any running target behind an nginx reverse proxy and expose it
through a Cloudflare tunnel. Two independent pieces:

- **`bench proxy`** — a local nginx that routes `<id>.<base-domain>` to each
  running, exposed target (subdomain routing).
- **`bench tunnel`** — cloudflared, in two modes: a zero-config **quick**
  tunnel to a single target, or a **named** tunnel that maps subdomains on your
  own domain through the proxy.

> ⚠️ Exposing an intentionally vulnerable target makes it reachable by others.
> Only do this deliberately, ideally with access control. See
> [SECURITY.md](SECURITY.md).

## Quick tunnel (default, no account)

The fastest way to share one target. Start it, then tunnel it:

```bash
./bench up aq-web-ben01
./bench tunnel aq-web-ben01
```

cloudflared prints an ephemeral `https://<random>.trycloudflare.com` URL that
proxies straight to that target's host port. Press Ctrl-C to stop. The URL
changes every run — fine for a quick share, not for a persistent lab.

## Local reverse proxy (subdomain routing)

Route several running targets by hostname on one port:

```bash
./bench up aq-web-ben01 aq-web-ben53
./bench proxy up --base lab.local --port 8080
```

Each running, exposed target is served at `http://<id>.lab.local:8080`. For
local use, point the hostnames at loopback:

```
# /etc/hosts
127.0.0.1  aq-web-ben01.lab.local aq-web-ben53.lab.local
```

`bench proxy up` regenerates the routes for whatever is running; re-run it
after starting or stopping targets. `bench proxy down` removes the proxy.

The proxy reaches targets at `host.docker.internal:<host_port>`, so it works
with the published ports targets already use — no shared Docker network needed.

## Named tunnel (your own domain, persistent subdomains)

For a stable lab on your own domain, use a Cloudflare named tunnel in front of
the proxy. One-time setup:

```bash
cloudflared tunnel login
cloudflared tunnel create bench
cloudflared tunnel route dns bench "*.lab.example.com"   # wildcard DNS
```

Then configure and run:

```bash
cp deploy/cloudflared/config.example.yml deploy/cloudflared/config.yml
# edit: set tunnel name/UUID, credentials-file, and base_domain

./bench proxy up --base lab.example.com --port 8080
./bench tunnel --named --all
```

`bench tunnel --named` generates the cloudflared ingress from the running,
exposed targets (each `<id>.lab.example.com` → the nginx proxy) and runs the
tunnel. `deploy/cloudflared/config.yml` and the generated config are gitignored
because they reference your credentials.

### Compose alternative

`deploy/docker-compose.proxy.yml` runs nginx (and, with the `named` profile,
cloudflared) as a plain compose stack if you prefer that to the CLI.

## Troubleshooting

- **`address already in use`** on `proxy up` — another service holds the proxy
  port; pass a free `--port`.
- **Quick tunnel `context deadline exceeded`** — the host has no outbound
  route to Cloudflare's edge; quick tunnels need internet egress.
- **502 through the proxy** — the target isn't running, or `expose` is false in
  its manifest. Check `./bench status`.
