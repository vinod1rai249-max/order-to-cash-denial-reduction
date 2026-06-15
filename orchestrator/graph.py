import logging
from typing import Dict, Any, TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator

# Configure logging
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """
    Represents the state of the Order-to-Cash AI process.
    """
    raw_payload: Dict[str, Any]
    sanitized_payload: Dict[str, Any]
    agent_logs: Annotated[List[Dict[str, Any]], operator.add]
    current_agent: str
    current_action: str
    confidence_score: float
    status: str
    metadata: Dict[str, Any]
    is_denied: bool
    denial_info: Dict[str, Any]
    ai_enabled: bool # New flag to demonstrate Before vs After

def order_node(state: AgentState) -> Dict[str, Any]:
    """Node: Order Agent (Stage 1 Prevent)"""
    from billing.order_agent import order_agent
    from governance.sink import log_to_governance_sink
    
    logger.info("Node: Order Entry Validation")
    payload = state["raw_payload"]
    ai_enabled = state.get("ai_enabled", True)
    
    if not ai_enabled:
        details = "STANDARD WORKFLOW (No AI): Order entered with missing authorization. Bypassing clinical note inference."
        log = {"agent": "OrderAgent", "action": "Manual Order Entry", "details": details, "confidence": 0.0}
        log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=0.0, payload={"ai_status": "disabled", "order": payload})
        return {**state, "agent_logs": [log], "status": "order_bypass", "confidence_score": 0.0}

    validation = order_agent.validate_order(payload)
    
    details = "Order validated successfully."
    if not validation["is_valid"]:
        details = f"Prevented Stage 1 write-off: {'; '.join(validation['issues'])}"
    elif validation["suggestions"]:
        details = f"Optimized order at Stage 1: {validation['suggestions'][0]['reasoning']}"

    log = {"agent": "OrderAgent", "action": "Order Entry Validation", "details": details, "confidence": 1.0}
    log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=1.0, payload=validation)
    
    return {**state, "agent_logs": [log], "status": "order_validated", "confidence_score": 1.0}

def sanitize_node(state: AgentState) -> Dict[str, Any]:
    """Node: Security Checkpoint (DLP)"""
    from security.dlp_service import redact_phi
    from governance.sink import log_to_governance_sink
    
    logger.info("Node: Sanitizing PHI")
    sanitized = redact_phi(state["raw_payload"])
    
    log = {
        "agent": "SecurityCheckpoint",
        "action": "DLP Sanitization",
        "details": "PHI redacted for HIPAA compliance prior to Stage 5 analysis.",
        "confidence": 1.0
    }
    
    log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=1.0, payload=sanitized)
    
    return {**state, "sanitized_payload": sanitized, "agent_logs": [log], "status": "sanitized"}

def billing_node(state: AgentState) -> Dict[str, Any]:
    """Node: Billing Agent (Stage 5 Catch)"""
    from billing.denial_predictor import predictor
    from governance.sink import log_to_governance_sink
    
    logger.info("Node: Billing Agent Risk Scoring")
    payload = state["sanitized_payload"]
    ai_enabled = state.get("ai_enabled", True)
    
    claim_data = {
        "payer_id": payload.get("payer_id", "UNKNOWN"),
        "cpt_code": payload.get("cpt_code", "UNKNOWN"),
        "modifiers": payload.get("modifiers", [])
    }
    
    initial_risk = predictor.predict_denial_risk(claim_data)
    final_risk = initial_risk
    auto_fixed = False
    
    if ai_enabled and initial_risk > 0.5:
        corrected_claim = predictor.suggest_corrections(claim_data)
        if corrected_claim.get("_auto_fixed"):
            final_risk = predictor.predict_denial_risk(corrected_claim)
            auto_fixed = True
            claim_data = corrected_claim
            
    if not ai_enabled:
        details = f"STANDARD WORKFLOW (No AI): Claim submitted with {initial_risk*100:.0f}% denial risk. No intervention performed."
    else:
        details = f"Analyzed claim for 'Missed Deadline' risk. Initial Risk: {initial_risk:.2f}. "
        if auto_fixed:
            details += f"Caught high-risk pattern and applied auto-correction. Final Risk: {final_risk:.2f}."
        else:
            details += "Claim scored as low risk."

    log = {"agent": "BillingAgent", "action": "Denial Risk Scoring", "details": details, "confidence": 1.0 if ai_enabled else 0.0}
    log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=log["confidence"], payload={"initial_risk": initial_risk, "final_risk": final_risk, "claim": claim_data, "ai_enabled": ai_enabled})
    
    return {**state, "agent_logs": [log], "confidence_score": 1.0 - final_risk, "status": "processed", "metadata": {**state.get("metadata", {}), "claim_data": claim_data, "auto_fixed": auto_fixed}}

def appeals_node(state: AgentState) -> Dict[str, Any]:
    """Node: Appeals Agent (Stage 6 Recover)"""
    from billing.appeals_agent import appeals_agent
    from governance.sink import log_to_governance_sink
    
    logger.info("Node: Appeals Agent Recovery")
    metadata = state.get("metadata", {})
    claim_id = metadata.get("claim_id", "UNK-123")
    ai_enabled = state.get("ai_enabled", True)
    
    if not ai_enabled:
        details = f"STANDARD WORKFLOW (No AI): Denial received for {claim_id}. Claim abandoned (Unworked Appeal)."
        log = {"agent": "AppealsAgent", "action": "Manual Review Required", "details": details, "confidence": 0.0}
        log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=0.0, payload={"ai_status": "disabled", "claim_id": claim_id})
        return {**state, "agent_logs": [log], "status": "appeal_abandoned", "confidence_score": 0.0}

    denial_code = state.get("denial_info", {}).get("denial_code", "CO-16")
    payer_id = state.get("sanitized_payload", {}).get("payer_id", "DEFAULT")
    claim_data = metadata.get("claim_data", {})
    
    if not claim_data:
        claim_data = {"cpt_code": state["raw_payload"].get("cpt_code")}
    
    appeal_result = appeals_agent.draft_appeal_letter(claim_id, denial_code, payer_id, claim_data)
    
    log = {
        "agent": "AppealsAgent",
        "action": "Generate Appeal Letter",
        "details": f"Recovered 'Unworked Appeal' for {claim_id}. Cited specific medical necessity clauses via RAG.",
        "confidence": appeal_result["confidence_score"]
    }
    
    log_to_governance_sink(agent=log["agent"], action=log["action"], details=log["details"], confidence=log["confidence"], payload=appeal_result)
    
    return {**state, "agent_logs": [log], "confidence_score": appeal_result["confidence_score"], "status": "appeal_drafted", "metadata": {**metadata, "appeal_result": appeal_result, "appeal_letter": appeal_result["drafted_letter"]}}

def hitl_router(state: AgentState):
    confidence = state.get("confidence_score", 1.0)
    THRESHOLD = 0.85
    if confidence < THRESHOLD:
        return "hitl"
    return "complete"

def recovery_router(state: AgentState):
    is_denied = state.get("is_denied")
    if is_denied:
        return "appeals"
    return "router"

# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("order", order_node)
workflow.add_node("sanitize", sanitize_node)
workflow.add_node("billing", billing_node)
workflow.add_node("appeals", appeals_node)

workflow.set_entry_point("order")
workflow.add_edge("order", "sanitize")
workflow.add_edge("sanitize", "billing")

workflow.add_conditional_edges("billing", recovery_router, {"appeals": "appeals", "router": "router_logic"})

def router_node(state): return state
workflow.add_node("router_logic", router_node)

workflow.add_conditional_edges("router_logic", hitl_router, {"hitl": END, "complete": END})
workflow.add_edge("appeals", END)

app_graph = workflow.compile()
