from governance.sink import get_logs
from typing import Dict, Any, List
from datetime import datetime
import json

class AnalyticsService:
    """
    Enterprise-grade Analytics Service for the Order-to-Cash AI System.
    Provides real-time business intelligence for the CFO and HITL dashboards.
    """
    
    def __init__(self):
        self.avg_test_value = 500.0 # Standard lab test reimbursement estimate

    def get_cfo_summary(self) -> Dict[str, Any]:
        """
        Stage 7: Provides the 'Revenue at Risk' and 'Protected Revenue' summary.
        Calculated by aggregating immutable logs from the Governance Sink.
        """
        logs = get_logs()
        
        stats = {
            "total_processed": 0,
            "prevented_denials": 0,
            "appeals_drafted": 0,
            "revenue_protected": 0.0,
            "revenue_at_risk": 0.0,
            "denial_loss_standard": 0.0, # Impact of Standard Workflow
            "payer_risk_distribution": {},
            "test_type_risk_distribution": {}
        }
        
        for log in logs:
            payload = log.get("payload", {})
            while isinstance(payload, str):
                try: payload = json.loads(payload)
                except: break
            
            # Check if AI was enabled for this transaction
            ai_enabled = payload.get("ai_enabled", payload.get("ai_status") != "disabled")

            # Process Billing Agent Logs
            if log["agent"] == "BillingAgent":
                stats["total_processed"] += 1
                claim = payload.get("claim", {})
                payer = claim.get("payer_id", "UNKNOWN")
                initial_risk = payload.get("initial_risk", 0.0)
                
                # Update Trends (Risk patterns are independent of intervention)
                if initial_risk > 0.5:
                    stats["revenue_at_risk"] += self.avg_test_value
                    stats["payer_risk_distribution"][payer] = stats["payer_risk_distribution"].get(payer, 0) + self.avg_test_value

                if ai_enabled:
                    if claim.get("_auto_fixed") or "_auto_fixed" in str(payload):
                        stats["prevented_denials"] += 1
                        stats["revenue_protected"] += self.avg_test_value
                else:
                    # STANDARD LOSS: No intervention on high risk
                    if initial_risk > 0.5:
                        stats["denial_loss_standard"] += self.avg_test_value
            
            # Process Appeals Agent Logs
            if log["agent"] == "AppealsAgent":
                payer = payload.get("payer_id", "UNKNOWN")
                cpt = payload.get("cpt_code", "UNKNOWN")
                
                # Update Trends
                stats["revenue_at_risk"] += self.avg_test_value
                stats["payer_risk_distribution"][payer] = stats["payer_risk_distribution"].get(payer, 0) + self.avg_test_value
                stats["test_type_risk_distribution"][cpt] = stats["test_type_risk_distribution"].get(cpt, 0) + self.avg_test_value

                if ai_enabled:
                    stats["appeals_drafted"] += 1
                    stats["revenue_protected"] += self.avg_test_value
                else:
                    stats["denial_loss_standard"] += self.avg_test_value

        return {
            "kpis": {
                "total_volume": stats["total_processed"],
                "preventable_write_offs_stopped": stats["prevented_denials"],
                "unworked_appeals_reclaimed": stats["appeals_drafted"],
                "revenue_protected_formatted": f"${stats['revenue_protected']:,.2f}",
                "revenue_at_risk_formatted": f"${stats['revenue_at_risk']:,.2f}",
                "standard_denial_loss_formatted": f"${stats['denial_loss_standard']:,.2f}",
                "revenue_protected_raw": stats["revenue_protected"],
                "revenue_at_risk_raw": stats["revenue_at_risk"]
            },
            "trends": {
                "top_risk_payers": stats["payer_risk_distribution"],
                "top_risk_tests": stats["test_type_risk_distribution"]
            },
            "logs": logs[:10], # Return top 10 logs for the dashboard feed
            "system_status": "Operational",
            "last_updated": datetime.now().isoformat()
        }

    def get_hitl_queue(self) -> List[Dict[str, Any]]:
        """
        Stage 6: Returns a structured queue for the Human-in-the-Loop Auditor Workspace.
        """
        logs = get_logs()
        queue = []
        
        # Sort by timestamp descending
        for log in sorted(logs, key=lambda x: x["timestamp"], reverse=True):
            if log["agent"] == "AppealsAgent":
                payload = log.get("payload", {})
                while isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except:
                        break
                
                if not isinstance(payload, dict):
                    continue
                    
                queue.append({
                    "id": f"TASK-{log['timestamp']}",
                    "type": "APPEAL_REVIEW",
                    "timestamp": log["timestamp"],
                    "claim_id": payload.get("claim_id"),
                    "payer": payload.get("payer_id", "Unknown"),
                    "confidence": log["confidence"],
                    "details": {
                        "policy_citation": payload.get("policy_citation"),
                        "draft_letter": payload.get("drafted_letter"),
                        "source": payload.get("rag_source")
                    }
                })
        return queue

analytics = AnalyticsService()
