import logging
import os
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
            
        # 2. AI-Assisted Diagnosis Inference (Gemini 1.5 Integration)
        clinical_notes = order_data.get("clinical_notes", "")
        if clinical_notes and not order_data.get("diagnosis_code"):
            try:
                from google import genai
                project_id = os.getenv("GCP_PROJECT_ID")
                client = genai.Client(vertexai=True, project=project_id, location="us-central1")
                
                prompt = f"""
                You are an expert medical billing auditor. 
                Read the following clinical notes and infer the most appropriate ICD-10 diagnosis code.
                Provide only the code and a one-sentence medical reasoning.
                
                NOTES: {clinical_notes}
                """
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                
                # Simple extraction (Production would use structured output)
                ai_text = response.text.strip()
                suggested_value = ai_text.split()[0] if ai_text else "Z80.3"
                
                suggestion = {
                    "field": "diagnosis_code",
                    "suggested_value": suggested_value,
                    "reasoning": f"Gemini Inference: {ai_text}",
                    "confidence": 0.95
                }
                suggestions.append(suggestion)
                issues.append(f"AI Suggestion: Apply {suggestion['suggested_value']} based on clinical notes.")
                logger.info(f"Gemini 1.5 Flash: Successfully inferred diagnosis code {suggested_value}")

            except Exception as e:
                logger.warning(f"Gemini integration failed or not enabled: {str(e)}. Falling back to local inference.")
                if "hereditary cancer" in clinical_notes.lower() or "brca" in clinical_notes.lower():
                    suggestion = {
                        "field": "diagnosis_code",
                        "suggested_value": "Z80.3",
                        "reasoning": "Inferred from clinical note mentioning 'hereditary cancer risk'.",
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
