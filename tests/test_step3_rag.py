import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_recovery_flow_with_rag():
    """
    Verifies that a denied claim triggers the Appeals Agent and uses RAG context.
    """
    payload = {
        "claim_id": "CLM-RAG-001",
        "payer_id": "MEDICARE",
        "is_denied": True,
        "denial_info": {
            "denial_code": "CO-16"
        },
        "cpt_code": "81479"
    }
    
    response = client.post("/api/v1/order", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check status
    assert data["status"] == "appeal_drafted"
    
    # Check logs
    agents = [log["agent"] for log in data["logs"]]
    assert "AppealsAgent" in agents
    
    # Check RAG content in letter (Medicare Rule 101-A should be retrieved)
    assert "Rule 101-A" in data["appeal_letter"]
    assert "Genetic testing" in data["appeal_letter"]

def test_rag_retrieval_accuracy():
    """
    Verifies that the correct policy is retrieved for a specific payer.
    """
    from billing.appeals_agent import appeals_agent
    
    # Query for Blue Cross Pathology
    query = "Why was 88305 denied?"
    policy = appeals_agent.retrieve_policy(query, "BLUE_CROSS")
    
    assert "Section 4.2" in policy
    assert "modifier 26" in policy
    assert "BLUE_CROSS" not in policy # The content doesn't contain the name, but the match is correct
