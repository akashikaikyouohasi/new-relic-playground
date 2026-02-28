import pytest
from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "new-relic-playground"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "new-relic-playground"
    assert data["version"] == "0.1.0"


def test_apm_fast(client: TestClient) -> None:
    response = client.get("/api/apm/fast")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "fast response"
    assert "elapsed_ms" in data


def test_apm_variable(client: TestClient) -> None:
    response = client.get("/api/apm/variable?delay_ms=0")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["requested_delay_ms"] == 0


def test_apm_cpu_intensive(client: TestClient) -> None:
    response = client.get("/api/apm/cpu-intensive")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["result"] == 832040


def test_errors_unhandled(client: TestClient) -> None:
    with pytest.raises(RuntimeError, match="unhandled error"):
        client.get("/api/errors/unhandled")


def test_errors_handled(client: TestClient) -> None:
    response = client.get("/api/errors/handled")
    assert response.status_code == 200
    data = response.json()
    assert data["error_class"] == "ValueError"


def test_errors_http_error(client: TestClient) -> None:
    response = client.get("/api/errors/http-error?status_code=404")
    assert response.status_code == 404


def test_errors_custom_error(client: TestClient) -> None:
    response = client.post(
        "/api/errors/custom-error",
        json={
            "error_message": "Payment failed",
            "user_id": "user-123",
            "order_id": "order-456",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["attributes"]["user_id"] == "user-123"


def test_custom_instrumentation_function_trace(client: TestClient) -> None:
    response = client.get("/api/custom-instrumentation/function-trace")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "function trace demo"
    assert len(data["steps"]) == 3


def test_custom_instrumentation_custom_attributes(client: TestClient) -> None:
    response = client.get("/api/custom-instrumentation/custom-attributes")
    assert response.status_code == 200
    data = response.json()
    assert data["attributes"]["user_tier"] == "premium"


def test_logs_basic(client: TestClient) -> None:
    response = client.get("/api/logs/basic")
    assert response.status_code == 200
    data = response.json()
    assert data["levels"] == ["debug", "info", "warning", "error"]


def test_logs_structured(client: TestClient) -> None:
    response = client.get("/api/logs/structured")
    assert response.status_code == 200
    data = response.json()
    assert data["attributes"]["user_id"] == "user-123"


def test_logs_with_error(client: TestClient) -> None:
    response = client.get("/api/logs/with-error")
    assert response.status_code == 200


def test_custom_event(client: TestClient) -> None:
    response = client.post(
        "/api/custom/event",
        json={
            "event_type": "UserAction",
            "attributes": {"action": "purchase", "amount": 2500},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "UserAction"


def test_custom_metric(client: TestClient) -> None:
    response = client.post(
        "/api/custom/metric",
        json={
            "metric_name": "Custom/BusinessMetric/OrderProcessingTime",
            "value": 1250.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 1250.5


def test_custom_batch_events(client: TestClient) -> None:
    response = client.post(
        "/api/custom/batch-events",
        json={"event_type": "PageView", "count": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
