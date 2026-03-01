# backend\tests\test_api.py
"""
API Integration Tests.

Tests full flow: Route → Orchestration → Loader → Engine
"""

from fastapi.testclient import TestClient
from api.main import app 


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_evaluate_endpoint_success():
    """
    Integration test:
    Route -> Orchestration -> Loader -> Engine
    """

    payload = {
        "profile": {
            "occupation": "farmer"
        }
    }

    response = client.post("/v1/evaluate", json=payload)

    assert response.status_code == 200

    data = response.json()

    # Structure validation
    assert "eligible" in data
    assert "partially_eligible" in data
    assert "ineligible" in data

    # Business validation (based on mock scheme loader)
    assert len(data["eligible"]) == 1
    assert data["eligible"][0]["scheme_id"] == "FARMER_SUPPORT"
    
    # Verify request ID header
    assert "X-Request-ID" in response.headers


def test_evaluate_endpoint_missing_profile():
    """
    Validation test:
    Should return 422 if profile missing
    """

    response = client.post("/v1/evaluate", json={})
    
    assert response.status_code == 422


def test_evaluate_endpoint_null_profile():
    """
    Validation test:
    Should return 400 if profile is null
    """
    
    payload = {"profile": None}
    response = client.post("/v1/evaluate", json=payload)
    
    assert response.status_code == 400
    assert "Profile is required" in response.json()["detail"]


def test_session_start():
    """Test session creation endpoint"""
    response = client.post("/v1/session/start")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert "created_at" in data
    assert "expires_at" in data


def test_request_id_tracking():
    """Test that request ID is tracked in headers"""
    payload = {"profile": {"occupation": "farmer"}}
    response = client.post("/v1/evaluate", json=payload)
    
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0


def test_deterministic_output():
    """Test that same input produces same output"""
    payload = {"profile": {"occupation": "farmer", "age": 30}}
    
    response1 = client.post("/v1/evaluate", json=payload)
    response2 = client.post("/v1/evaluate", json=payload)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Results should be identical (excluding request IDs)
    data1 = response1.json()
    data2 = response2.json()
    
    assert data1 == data2