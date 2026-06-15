import pytest
from fastapi.testclient import TestClient
from main import app
from governance.sink import LOG_HISTORY

@pytest.fixture(autouse=True)
def clear_logs():
    LOG_HISTORY.clear()

client = TestClient(app)

def test_enterprise_cfo_dashboard_metrics():
    """
    Verifies that the CFO dashboard provides the deep-dive metrics required by the blueprint.
    """
    # 1. High risk claim that gets fixed (Reduces risk, protects revenue)
    # Using BLUE_CROSS + 88305 + No Modifiers (triggers high risk in Step 2)
    client.post("/api/v1/order", json={
        "payer_id": "BLUE_CROSS", 
        "cpt_code": "88305", 
        "modifiers": []
    })
    
    # 2. Denied claim that enters recovery (Revenue at risk)
    client.post("/api/v1/order", json={
        "claim_id": "CLM-DENY-1",
        "payer_id": "MEDICARE",
        "is_denied": True,
        "denial_info": {"denial_code": "CO-16"},
        "cpt_code": "81479"
    })
    
    response = client.get("/api/v1/dashboard/cfo")
    assert response.status_code == 200
    data = response.json()
    
    # Check KPIs
    kpis = data["kpis"]
    assert kpis["total_volume"] >= 1
    assert kpis["preventable_write_offs_stopped"] == 1
    assert kpis["revenue_protected_raw"] == 1000.0
    
    # Check Trends (Payer and Test Type analysis)
    trends = data["trends"]
    assert "BLUE_CROSS" in trends["top_risk_payers"] or "MEDICARE" in trends["top_risk_payers"]
    assert "81479" in trends["top_risk_tests"]

def test_enterprise_hitl_workspace_data():
    """
    Verifies that the HITL queue provides rich details for the Auditor Workspace.
    """
    # Trigger an appeal
    client.post("/api/v1/order", json={
        "claim_id": "CLM-HITL-001",
        "payer_id": "BLUE_CROSS",
        "is_denied": True,
        "denial_info": {"denial_code": "CO-4"},
        "cpt_code": "88305"
    })
    
    response = client.get("/api/v1/dashboard/hitl")
    assert response.status_code == 200
    queue = response.json()
    
    assert len(queue) >= 1
    item = queue[0]
    assert item["type"] == "APPEAL_REVIEW"
    assert "Section 4.2" in item["details"]["policy_citation"] # RAG verification
    assert "Subject: Formal Appeal" in item["details"]["draft_letter"] # Gemini verification
    assert item["details"]["source"] == "Vertex_AI_Search_Mock"
