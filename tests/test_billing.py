import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_denial_prediction_low_risk():
    """
    Test a standard claim with low predicted risk.
    """
    payload = {
        "resourceType": "ServiceRequest",
        "payer_id": "BLUE_CROSS_STABLE",
        "cpt_code": "80053", # Basic Metabolic Panel
        "modifiers": ["26"]
    }
    
    response = client.post("/api/v1/order", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Confidence should be high for low risk (Confidence = 1 - Risk)
    assert data["confidence"] > 0.7
    assert data["status"] == "processed"

def test_denial_prediction_high_risk_and_fix():
    """
    Test a claim that triggers high risk and check for auto-fix.
    Using BLUE_CROSS + 88305 + No Modifiers (triggers high risk in Step 2)
    """
    payload = {
        "resourceType": "ServiceRequest",
        "payer_id": "BLUE_CROSS",
        "cpt_code": "88305",
        "modifiers": [] # Missing modifier
    }
    
    response = client.post("/api/v1/order", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check that logs mention the auto-fix
    billing_log = next(l for l in data["logs"] if l["agent"] == "BillingAgent")
    assert "applied auto-correction" in billing_log["details"]

    assert "26" in data["claim_data"]["modifiers"]

def test_governance_log_contains_risk_data(caplog):
    """
    Verifies that the governance sink captures the risk scoring details.
    """
    payload = {
        "resourceType": "ServiceRequest",
        "payer_id": "MEDICARE",
        "cpt_code": "81479"
    }
    
    with caplog.at_level("INFO"):
        client.post("/api/v1/order", json=payload)
    
    assert "BillingAgent" in caplog.text
    assert "Denial Risk Scoring" in caplog.text
