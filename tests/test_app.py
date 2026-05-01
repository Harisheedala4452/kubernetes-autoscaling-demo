from app.main import app


def test_index_returns_endpoint_list():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "/health" in response.get_json()["endpoints"]


def test_health_returns_ok():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_version_returns_app_metadata():
    client = app.test_client()

    response = client.get("/version")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["app"] == "kubernetes-autoscaling-demo"
    assert "version" in payload


def test_cpu_load_is_bounded_and_returns_success():
    client = app.test_client()

    response = client.get("/cpu-load?seconds=0.1")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "load generated"
    assert payload["seconds"] == 0.1


def test_metrics_endpoint_exposes_prometheus_metrics():
    client = app.test_client()

    response = client.get("/metrics")

    assert response.status_code == 200
    assert b"flask_autoscaling_demo_requests_total" in response.data
