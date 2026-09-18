#!/usr/bin/env python3
"""QuickCart -- a checkout API with a business-logic flaw (A04 Insecure Design).

The cart total is computed as sum(price * qty) minus coupon discounts, but
quantity is never validated. A negative quantity makes the total zero or
negative, and the checkout "rewards" a non-positive total with the flag --
a stand-in for the real-world bug where a manipulated total unlocks value.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)
FLAG = "f13{business_logic_negative_total}"
COUPONS = {"SAVE10": 10, "SAVE20": 20}


@app.route("/")
def index():
    return jsonify(service="QuickCart",
                   usage="POST /checkout {items:[{price,qty}], coupon}")


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(force=True, silent=True) or {}
    items = data.get("items", [])
    total = 0.0
    for it in items:
        # BUG: qty is trusted as-is; negative quantities are accepted.
        total += float(it.get("price", 0)) * float(it.get("qty", 0))
    total -= COUPONS.get(data.get("coupon", ""), 0)
    if total <= 0:
        return jsonify(status="approved", total=total,
                       reward=FLAG,
                       note="Non-positive total accepted -- you exploited the flaw.")
    return jsonify(status="approved", total=total)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
