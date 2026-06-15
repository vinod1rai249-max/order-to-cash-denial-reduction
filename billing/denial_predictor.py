import logging
import random
import os
import pandas as pd
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DenialPredictor:
    """
    Implements a real Logistic Regression model for Denial Prediction.
    This replaces the previous hardcoded simulation.
    """
    
    def __init__(self):
        self.model_path = 'models/denial_model.joblib'
        self.encoder_path = 'models/encoder.joblib'
        self.model = None
        self.encoder = None

    def _ensure_initialized(self):
        """Lazy load models."""
        if self.model is None:
            import joblib
            if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
                self.model = joblib.load(self.model_path)
                self.encoder = joblib.load(self.encoder_path)
                logger.info("Logistic Regression model and encoder loaded successfully.")
            else:
                logger.warning("Predictive model files not found. Scoring may be inaccurate.")
        
    def predict_denial_risk(self, claim_data: Dict[str, Any]) -> float:
        """
        Scores a claim for denial risk using the trained Logistic Regression model.
        """
        self._ensure_initialized()
        if not self.model or not self.encoder:
            # Fallback to simple baseline if model not loaded
            return 0.2
            
        try:
            # Prepare input
            payer_id = claim_data.get("payer_id", "UNKNOWN")
            cpt_code = claim_data.get("cpt_code", "UNKNOWN")
            has_modifier = 1 if claim_data.get("modifiers") else 0
            
            input_df = pd.DataFrame([{
                'payer_id': payer_id,
                'cpt_code': cpt_code
            }])
            
            # Transform categorical features
            X_cat = self.encoder.transform(input_df)
            X = np.hstack([X_cat, [[has_modifier]]])
            
            # Predict probability of class 1 (Denied)
            probs = self.model.predict_proba(X)
            risk_score = probs[0][1]
            
            return float(risk_score)
            
        except Exception as e:
            logger.error(f"Error during denial risk prediction: {str(e)}")
            return 0.5 # Safe fallback

    def suggest_corrections(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Logic for 'Automatic Correction' based on high-risk triggers.
        """
        corrected_data = claim_data.copy()
        
        # Rule: Pathology (88305) often requires modifier '26'
        if claim_data.get("cpt_code") == "88305" and not claim_data.get("modifiers"):
            corrected_data["modifiers"] = ["26"]
            corrected_data["_auto_fixed"] = True
            
        return corrected_data

# Singleton instance
predictor = DenialPredictor()
