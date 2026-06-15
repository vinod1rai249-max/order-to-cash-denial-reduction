import pytest
from billing.denial_predictor import predictor

def test_logistic_regression_logic():
    """
    Verifies that the Logistic Regression model produces expected risk shifts.
    """
    # BLUE_CROSS + 88305 + No Modifiers = Historically High Risk in our mock data
    high_risk_claim = {
        "payer_id": "BLUE_CROSS",
        "cpt_code": "88305",
        "modifiers": []
    }
    
    # BLUE_CROSS + 80053 + Modifiers = Historically Low Risk
    low_risk_claim = {
        "payer_id": "BLUE_CROSS",
        "cpt_code": "80053",
        "modifiers": ["26"]
    }
    
    risk_high = predictor.predict_denial_risk(high_risk_claim)
    risk_low = predictor.predict_denial_risk(low_risk_claim)
    
    print(f"High Risk Score: {risk_high}")
    print(f"Low Risk Score: {risk_low}")
    
    assert risk_high > risk_low
    # Based on our training data, high risk should be significantly higher
    assert risk_high > 0.5

def test_auto_fix_reduces_risk():
    """
    Verifies that the auto-fix (adding modifier) actually reduces the statistical risk.
    """
    original_claim = {
        "payer_id": "BLUE_CROSS",
        "cpt_code": "88305",
        "modifiers": []
    }
    
    initial_risk = predictor.predict_denial_risk(original_claim)
    
    fixed_claim = predictor.suggest_corrections(original_claim)
    assert fixed_claim["_auto_fixed"] is True
    
    final_risk = predictor.predict_denial_risk(fixed_claim)
    
    assert final_risk < initial_risk
