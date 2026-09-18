#!/usr/bin/env python3
"""AcmePortal -- session tokens with a broken JWT check (A02/A07).

/login issues a signed JWT for a normal user. /admin is supposed to be
admin-only, but it decodes the token with signature verification DISABLED,
so an attacker can forge an unsigned (alg:none) token claiming role=admin.
"""
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = "acme-portal-signing-secret"
FLAG = "f13{jwt_alg_none_forgery}"


@app.route("/")
def index():
    return jsonify(service="AcmePortal",
                   usage="GET /login -> token; GET /admin with Authorization: Bearer <token>")


@app.route("/login")
def login():
    token = jwt.encode({"user": "guest", "role": "user"}, SECRET, algorithm="HS256")
    return jsonify(token=token, note="A normal user token. /admin needs role=admin.")


@app.route("/admin")
def admin():
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.lower().startswith("bearer ") else auth
    if not token:
        return jsonify(error="missing token"), 401
    try:
        # BUG: signature verification disabled -> unsigned alg:none tokens trusted.
        claims = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return jsonify(error=str(e)), 400
    if claims.get("role") == "admin":
        return jsonify(flag=FLAG, note="Forged admin token accepted.")
    return jsonify(error="not admin", claims=claims), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
