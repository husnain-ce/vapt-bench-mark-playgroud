#!/usr/bin/env python3
"""AccountService -- registration with mass assignment (API6 / A04).

/api/register copies every field from the request body onto the new account,
including privileged fields the client should never set. Registering with
"is_admin": true yields an admin api_key, which unlocks the admin-only flag.
"""
import secrets
from flask import Flask, request, jsonify

app = Flask(__name__)
FLAG = "f13{mass_assignment_is_admin}"
USERS = {}


@app.route("/")
def index():
    return jsonify(service="AccountService",
                   usage="POST /api/register {username,...}; GET /api/flag with X-Api-Key")


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    key = secrets.token_hex(8)
    # BUG: whole body is merged onto the account (mass assignment).
    user = {"username": data.get("username", "anon"), "is_admin": False}
    user.update(data)
    USERS[key] = user
    return jsonify(api_key=key, account=user)


@app.route("/api/flag")
def flag():
    user = USERS.get(request.headers.get("X-Api-Key", ""))
    if not user:
        return jsonify(error="unknown api key"), 401
    if user.get("is_admin") is True:
        return jsonify(flag=FLAG)
    return jsonify(error="admin only"), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
