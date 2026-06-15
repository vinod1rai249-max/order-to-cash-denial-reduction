import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order-to-Cash AI Denial Reduction Gateway")

# Standard CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Lightweight health check that doesn't trigger heavy AI loading."""
    return {"status": "healthy"}

@app.get("/api/v1/dashboard/cfo")
async def get_cfo_dashboard():
    """Stage 7: Payment Dashboard (Live View)"""
    from dashboard.analytics import analytics
    return analytics.get_cfo_summary()

@app.get("/api/v1/dashboard/hitl")
async def get_hitl_queue():
    """Stage 6: Human-in-the-Loop Queue"""
    from dashboard.analytics import analytics
    return analytics.get_hitl_queue()

@app.post("/api/v1/hitl/approve/{claim_id}")
async def approve_claim(claim_id: str):
    """Auditor approval of an AI action."""
    from governance.sink import log_to_governance_sink
    log_to_governance_sink(
        agent="HumanAuditor",
        action="Approve Appeal",
        details=f"Auditor manually approved appeal for {claim_id}",
        confidence=1.0,
        payload={"claim_id": claim_id}
    )
    return {"status": "approved", "claim_id": claim_id}

@app.post("/api/v1/appeal")
async def process_appeal(denial_data: Dict[str, Any]):
    """Stage 6: Recover (Appeals Agent)"""
    from billing.appeals_agent import appeals_agent
    from governance.sink import log_to_governance_sink
    from orchestrator.graph import app_graph
    
    try:
        claim_id = denial_data.get("claim_id", "UNK-123")
        denial_reason = denial_data.get("denial_code", "CO-16")
        payer_id = denial_data.get("payer_id", "DEFAULT")
        claim_data = denial_data.get("claim_data", {})
        ai_enabled = denial_data.get("ai_enabled", True)

        initial_state = {
            "raw_payload": {"payer_id": payer_id, "cpt_code": claim_data.get("cpt_code")},
            "sanitized_payload": {"payer_id": payer_id, "cpt_code": claim_data.get("cpt_code")},
            "agent_logs": [],
            "current_agent": "Gateway",
            "current_action": "Recovery Initiation",
            "confidence_score": 1.0,
            "status": "received",
            "metadata": {"claim_id": claim_id, "claim_data": claim_data},
            "is_denied": True,
            "denial_info": {"denial_code": denial_reason},
            "ai_enabled": ai_enabled
        }

        final_state = app_graph.invoke(initial_state)
        return {
            "status": final_state["status"],
            "appeal_details": final_state.get("metadata", {}).get("appeal_result")
        }

    except Exception as e:
        logger.error(f"Appeal failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/order")
async def process_order(payload: Dict[str, Any]):
    """Stage 1, 5 & 6 Integrated Flow"""
    from orchestrator.graph import app_graph
    
    try:
        is_denied = payload.get("is_denied", False)
        denial_info = payload.get("denial_info", {})
        ai_enabled = payload.get("ai_enabled", True)
        
        initial_state = {
            "raw_payload": payload,
            "sanitized_payload": {},
            "agent_logs": [],
            "current_agent": "Gateway",
            "current_action": "Reception",
            "confidence_score": 1.0,
            "status": "received",
            "metadata": {"claim_id": payload.get("claim_id", "DEMO-" + os.urandom(2).hex().upper())},
            "is_denied": is_denied,
            "denial_info": denial_info,
            "ai_enabled": ai_enabled
        }
        
        # This will trigger heavy AI loading ONLY on first call
        final_state = app_graph.invoke(initial_state)
        
        return {
            "status": final_state["status"],
            "confidence": round(final_state.get("confidence_score", 0.0), 2),
            "logs": final_state["agent_logs"],
            "sanitized_data": final_state["sanitized_payload"],
            "claim_data": final_state["metadata"].get("claim_data"),
            "appeal_letter": final_state["metadata"].get("appeal_letter")
        }
    except Exception as e:
        logger.error(f"Orchestration failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
