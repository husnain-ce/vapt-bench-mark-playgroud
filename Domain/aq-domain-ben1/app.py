#!/usr/bin/env python3
"""AcmeCorp site -- a subdomain/vhost enumeration challenge.

One app serves several virtual hosts, routed by the Host header. The public
site is benign but leaks a hint (an HTML comment and robots.txt) that an
"internal" vhost exists. Requesting the app with Host: internal.<domain>
reaches the internal environment, which serves the flag. The player enumerates
subdomains (a wordlist that includes "internal") and sets the Host header.
"""
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
FLAG = "f13{hidden_vhost_internal}"
HIDDEN_SUB = "internal"


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /admin\n"
                    "# note: internal-* hosts are staging only\n",
                    mimetype="text/plain")


@app.route("/")
def index():
    sub = request.host.split(":")[0].split(".")[0]
    if sub == HIDDEN_SUB:
        return jsonify(env="internal", flag=FLAG,
                       note="You found the undocumented internal vhost.")
    return Response(
        "<!-- TODO: decommission the internal.acme vhost before launch -->\n"
        "<h1>Acme Corp</h1><p>Welcome to our public site.</p>",
        mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
