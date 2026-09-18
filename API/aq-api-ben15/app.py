#!/usr/bin/env python3
"""OrderService -- an order API with no object-level authorization (API1 / A01).

You are user 1. /api/users/<id>/orders returns any user's orders with no check
that the caller owns that id, so requesting user 2's orders leaks their data --
including the flag order.
"""
from flask import Flask, jsonify

app = Flask(__name__)
FLAG = "f13{bola_idor_other_user}"
ORDERS = {
    1: [{"id": 101, "item": "USB cable", "total": 9.99}],
    2: [{"id": 202, "item": "Confidential contract", "total": 0, "note": FLAG}],
}


@app.route("/")
def index():
    return jsonify(service="OrderService", you="user 1",
                   usage="GET /api/users/<id>/orders")


@app.route("/api/users/<int:uid>/orders")
def orders(uid):
    # BUG: no check that the caller is uid. Any id is readable.
    return jsonify(user=uid, orders=ORDERS.get(uid, []))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
