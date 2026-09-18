# Domain / subdomain targets

Subdomain enumeration, virtual-host routing, and subdomain-takeover challenges.
Host ports: **8900s**.

```bash
./bench list --domain domain
./bench up aq-domain-ben1
curl -s localhost:8901/ -H "Host: internal.acme.local"
```

## How they run

One `native-python` app routes by the `Host` header, serving several virtual
hosts. The flag lives on an undocumented vhost the player must discover
(wordlist enumeration), usually with a hint in the public site (robots.txt, an
HTML comment). Because routing is by Host header, these pair naturally with the
nginx proxy (`bench proxy`) for real subdomain URLs -- see
[../TUNNELING.md](../TUNNELING.md).
