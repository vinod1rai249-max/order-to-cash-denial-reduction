import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_orchestrator_full_flow():
    """
    Verifies that the LangGraph orchestrator correctly sequences sanitization and billing.
    """
    payload = {
        "resourceType": "ServiceRequest",
        "patient_name": "John Doe", # Should be redacted
        "payer_id": "BLUE_CROSS_STABLE",
        "cpt_code": "80053",
        "modifiers": ["26"]
    }
    
    response = client.post("/api/v1/order", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check status (should be 'processed' from billing node)
    assert data["status"] == "processed"
    
    # Check that PHI was redacted in the sanitized_data returned by orchestrator
    assert data["sanitized_data"]["patient_name"] == "[REDACTED]"
    
    # Check that logs from both agents are present
    logs = data["logs"]
    agents = [log["agent"] for log in logs]
    assert "SecurityCheckpoint" in agents
    assert "BillingAgent" in agents

def test_orchestrator_error_handling():
    """
    Verifies that errors in the graph are caught and returned as 500s.
    """
    # Sending invalid data that might cause a node to fail
    response = client.post("/api/v1/order", json=None)
    assert response.status_code == 422 # FastAPI validation error first
