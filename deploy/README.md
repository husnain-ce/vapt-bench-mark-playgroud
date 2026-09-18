# deploy/ -- reverse proxy and tunneling

This directory backs `bench proxy` and `bench tunnel`. See
[../docs/TUNNELING.md](../docs/TUNNELING.md) for the full workflow.

- `nginx/nginx.conf` -- base nginx config; per-target server blocks are
  generated into `.bench/nginx/conf.d/` by `bench proxy up`.
- `nginx/templates/target.conf.tmpl` -- the per-target server-block template
  (subdomain routing, X-Forwarded headers, redirect rewriting).
- `cloudflared/config.example.yml` -- template for a **named** tunnel on your
  own domain. Copy to `config.yml` and fill in your tunnel + domain.
- `docker-compose.proxy.yml` -- optional compose stack (nginx + cloudflared)
  for users who prefer plain compose over the CLI.

Quick tunnels (the default) need none of this: `bench tunnel <id>` opens an
ephemeral `trycloudflare.com` URL straight to one target.
