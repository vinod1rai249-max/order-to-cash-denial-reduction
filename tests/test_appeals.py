import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_appeal_blue_cross():
    """
    Test generating an appeal letter for a Blue Cross denial.
    Verifies that the correct policy section is cited.
    """
    denial_payload = {
        "claim_id": "CLM-999",
        "denial_code": "CO-4",
        "payer_id": "BLUE_CROSS",
        "claim_data": {
            "cpt_code": "88305"
        }
    }
    
    response = client.post("/api/v1/appeal", json=denial_payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "appeal_drafted"
    appeal = data["appeal_details"]
    assert "Section 4.2" in appeal["policy_citation"]
    assert "BLUE_CROSS" in appeal["drafted_letter"]
    assert "88305" in appeal["drafted_letter"]
    assert appeal["confidence_score"] == 0.92

def test_generate_appeal_medicare():
    """
    Test generating an appeal letter for a Medicare denial.
    """
    denial_payload = {
        "claim_id": "CLM-001",
        "denial_code": "CO-16",
        "payer_id": "MEDICARE",
        "claim_data": {
            "cpt_code": "81479"
        }
    }
    
    response = client.post("/api/v1/appeal", json=denial_payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "appeal_drafted"
    appeal = data["appeal_details"]
    assert "Rule 101-A" in appeal["policy_citation"]
    assert "Genetic testing" in appeal["drafted_letter"]

def test_appeal_governance_logging(caplog):
    """
    Verifies that the AppealsAgent logs to the Governance Sink.
    """
    payload = {
        "claim_id": "CLM-LOG-1",
        "denial_code": "CO-X",
        "payer_id": "DEFAULT"
    }
    
    with caplog.at_level("INFO"):
        client.post("/api/v1/appeal", json=payload)
    
    assert "AppealsAgent" in caplog.text
    assert "Generate Appeal Letter" in caplog.text
    assert "Recovered 'Unworked Appeal'" in caplog.text

