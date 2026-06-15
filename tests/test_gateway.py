import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_order_with_phi():
    """
    Verifies that the gateway redacts PHI and returns a sanitized payload.
    """
    phi_payload = {
        "resourceType": "ServiceRequest",
        "id": "123",
        "patient": {
            "display": "John Doe",
            "birthDate": "1980-01-01"
        },
        "orderDetail": "Blood test for SSN-123"
    }
    
    response = client.post("/api/v1/order", json=phi_payload)
    
    assert response.status_code == 200
    data = response.json()
    # Integrated system status is 'processed' or 'sanitized' depending on logic
    assert data["status"] in ["processed", "sanitized", "complete"]
    
    sanitized = data["sanitized_data"]
    # Check that PHI was redacted
    assert sanitized["patient"]["display"] == "[REDACTED]"
    assert sanitized["patient"]["birthDate"] == "[REDACTED]"
    assert "[REDACTED]" in sanitized["orderDetail"]

def test_governance_logging(caplog):
    """
    Verifies that the governance sink logging is triggered.
    """
    payload = {"resourceType": "Patient", "id": "456", "name": [{"text": "Jane Smith"}]}
    
    with caplog.at_level("INFO"):
        response = client.post("/api/v1/order", json=payload)
    
    assert response.status_code == 200
    # Check if GOVERNANCE_SINK_LOG appeared in logs
    assert "GOVERNANCE_SINK_LOG" in caplog.text
    assert "SecurityCheckpoint" in caplog.text
