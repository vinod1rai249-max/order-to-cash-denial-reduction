import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OrderAgent:
    """
    Stage 1 Agent: Order Entry & Validation.
    Stops the denial at its origin (Preventable Write-offs).
    """
    
    def validate_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs rule-based validation and AI-assisted diagnosis inference.
        """
        issues = []
        suggestions = []
        is_valid = True
        
        # 1. Rule-based check: Missing Prior Authorization for expensive tests
        cpt_code = order_data.get("cpt_code") or ""
        # High value tests usually start with 81 (Molecular)
        if cpt_code.startswith("81") and not order_data.get("prior_auth"):
            issues.append("Missing required Prior Authorization for high-value genetic test.")
            is_valid = False
            
        # 2. AI-Assisted Diagnosis Inference (Preventable Write-off category)
        clinical_notes = order_data.get("clinical_notes", "")
        if clinical_notes and not order_data.get("diagnosis_code"):
            # Simulate Gemini reading the note and suggesting a code
            if "hereditary cancer" in clinical_notes.lower() or "brca" in clinical_notes.lower():
                suggestion = {
                    "field": "diagnosis_code",
                    "suggested_value": "Z80.3", # Family history of malignant neoplasm of breast
                    "reasoning": "Inferred from clinical note mentioning 'hereditary cancer risk' and family history.",
                    "confidence": 0.95
                }
                suggestions.append(suggestion)
                issues.append(f"AI Suggestion: Apply {suggestion['suggested_value']} based on clinical notes.")

        return {
            "is_valid": is_valid,
            "issues": issues,
            "suggestions": suggestions,
            "agent": "OrderAgent",
            "stage": 1
        }

order_agent = OrderAgent()
