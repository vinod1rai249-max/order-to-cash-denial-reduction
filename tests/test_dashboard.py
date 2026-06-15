import pytest
from fastapi.testclient import TestClient
from main import app
from governance.sink import LOG_HISTORY

@pytest.fixture(autouse=True)
def clear_logs():
    LOG_HISTORY.clear()

client = TestClient(app)

def test_cfo_dashboard_aggregation():
    """
    Simulates a sequence of claims and verifies the CFO dashboard aggregates them.
    """
    # 1. Low risk claim
    client.post("/api/v1/order", json={"payer_id": "STABLE", "cpt_code": "80000"})
    
    # 2. High risk claim that gets fixed
    client.post("/api/v1/order", json={"payer_id": "PAYER_EXP_99", "cpt_code": "88305", "modifiers": []})
    
    # 3. Denied claim that gets appealed
    client.post("/api/v1/appeal", json={"claim_id": "CLM-1", "denial_code": "CO-4", "payer_id": "BLUE_CROSS"})
    
    response = client.get("/api/v1/dashboard/cfo")
    assert response.status_code == 200
    data = response.json()
    
    # 1 fix + 1 appeal = $1000 at risk or protected
    assert data["kpis"]["preventable_write_offs_stopped"] == 1
    assert data["kpis"]["unworked_appeals_reclaimed"] == 1
    assert "$1,000.00" in data["kpis"]["revenue_protected_formatted"]

def test_hitl_queue_and_approval():
    """
    Verifies that appeals appear in the HITL queue and can be approved.
    """
    # Create an appeal
    client.post("/api/v1/appeal", json={"claim_id": "CLM-HITL", "denial_code": "CO-16", "payer_id": "MEDICARE"})
    
    # Check queue
    queue_res = client.get("/api/v1/dashboard/hitl")
    assert len(queue_res.json()) == 1
    assert queue_res.json()[0]["claim_id"] == "CLM-HITL"
    
    # Approve
    app_res = client.post("/api/v1/hitl/approve/CLM-HITL")
    assert app_res.json()["status"] == "approved"
    
    # Verify approval logged in Governance Sink
    from governance.sink import get_logs
    logs = get_logs()
    assert any(log["agent"] == "HumanAuditor" for log in logs)
