#!/usr/bin/env python3
"""ConfigLoader -- a config import API with insecure deserialization (A08).

POST /import parses a submitted YAML config with an UNSAFE loader, which lets a
crafted document construct arbitrary Python objects and execute commands. The
flag lives in ./flag.txt; a deserialization payload that runs `cat` on it (or
reads it any other way) returns the flag through the object's value.
"""
import yaml
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(service="ConfigLoader",
                   usage="POST /import  (body: a YAML config document)")


@app.route("/import", methods=["POST"])
def import_config():
    body = request.get_data(as_text=True)
    try:
        # BUG: UnsafeLoader constructs arbitrary Python objects from YAML tags.
        obj = yaml.load(body, Loader=yaml.UnsafeLoader)
    except Exception as e:
        return jsonify(error=str(e)), 400
    return jsonify(loaded=str(obj))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
