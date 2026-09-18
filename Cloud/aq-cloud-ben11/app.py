#!/usr/bin/env python3
"""MetricsGateway -- a service that leaves its debug endpoints exposed (A05).

Spring-Boot-style /actuator/env is reachable with no authentication and dumps
the process environment, including secrets that should never be exposed --
here, an API key that carries the flag.
"""
from flask import Flask, jsonify

app = Flask(__name__)
FLAG = "f13{exposed_actuator_env_leak}"
# Emulated process environment (as a misconfigured actuator would expose it).
ENV = {
    "SERVICE_NAME": "metrics-gateway",
    "LOG_LEVEL": "INFO",
    "DB_HOST": "db.internal",
    "INTERNAL_API_KEY": FLAG,
    "AWS_REGION": "us-east-1",
}


@app.route("/")
def index():
    return jsonify(service="MetricsGateway", usage="GET /health, GET /actuator/env")


@app.route("/health")
def health():
    return jsonify(status="UP")


@app.route("/actuator/env")
def env():
    # BUG: no auth on the actuator; full environment (with secrets) is dumped.
    return jsonify(propertySources=[{"name": "systemEnvironment", "properties":
                   {k: {"value": v} for k, v in ENV.items()}}])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
