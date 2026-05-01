import math
import os
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from werkzeug.wrappers import Response

app = Flask(__name__)


APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
REQUEST_COUNT = Counter(
    "flask_autoscaling_demo_requests_total",
    "Total HTTP requests handled by the Flask autoscaling demo.",
    ["endpoint", "method", "status"],
)


@app.after_request
def record_request_metrics(response):
    """Count requests so Prometheus and Grafana can show app-level traffic."""
    REQUEST_COUNT.labels(
        endpoint=request.path,
        method=request.method,
        status=response.status_code,
    ).inc()
    return response


@app.get("/")
def index():
    """Return a simple landing response for humans and quick smoke tests."""
    return jsonify(
        {
            "message": "Kubernetes Autoscaling Demo",
            "endpoints": ["/health", "/version", "/cpu-load?seconds=2"],
        }
    )


@app.get("/health")
def health():
    """Health endpoint used by Docker and Kubernetes probes."""
    return jsonify({"status": "ok"})


@app.get("/version")
def version():
    """Show version and runtime details that help during rollouts."""
    return jsonify(
        {
            "app": "kubernetes-autoscaling-demo",
            "version": APP_VERSION,
            "hostname": os.getenv("HOSTNAME", "local"),
            "time": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics for scraping."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/cpu-load")
def cpu_load():
    """Create temporary CPU load so Kubernetes HPA has work to measure.

    The endpoint intentionally burns CPU for a short, bounded duration. Keeping
    the upper limit small protects beginner laptops and small Minikube clusters.
    """
    seconds = _bounded_seconds(request.args.get("seconds", "2"))
    deadline = time.perf_counter() + seconds
    iterations = 0
    result = 0.0

    while time.perf_counter() < deadline:
        for value in range(1, 5000):
            result += math.sqrt(value) * math.sin(value)
        iterations += 1

    return jsonify(
        {
            "status": "load generated",
            "seconds": seconds,
            "iterations": iterations,
            "result_sample": round(result, 4),
        }
    )


def _bounded_seconds(raw_value):
    """Parse a duration and clamp it to a beginner-safe range."""
    try:
        seconds = float(raw_value)
    except (TypeError, ValueError):
        seconds = 2.0

    return max(0.1, min(seconds, 10.0))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
