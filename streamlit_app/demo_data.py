# Management-focused Demo Data Scenarios
# Aligned with the 3 Types of Denial Loss

# LOSS TYPE 1: Preventable Write-offs (Stage 1 Order Agent)
PREVENT_SCENARIOS = {
    "BRCA Genetic Test (Missing Auth)": {
        "claim_id": "PREVENT-BRCA-001",
        "payer_id": "UNITED_HEALTHCARE",
        "cpt_code": "81162",
        "clinical_notes": "Patient presents with strong family history of early-onset breast cancer. Grandmother and mother both diagnosed before age 45.",
        "is_denied": False
    },
    "Molecular Oncology (Invalid Code)": {
        "claim_id": "PREVENT-ONCO-002",
        "payer_id": "AETNA",
        "cpt_code": "81210",
        "clinical_notes": "BRAF mutation testing for melanoma patient.",
        "is_denied": False
    }
}

# LOSS TYPE 2: Missed Deadlines / High Risk (Stage 5 Billing Agent)
CATCH_SCENARIOS = {
    "Pathology 88305 (Missing Modifier)": {
        "claim_id": "CATCH-88305-001",
        "payer_id": "BLUE_CROSS",
        "cpt_code": "88305",
        "modifiers": [],
        "is_denied": False
    },
    "Chemistry Panel (Mismatched Payer)": {
        "claim_id": "CATCH-PANEL-002",
        "payer_id": "HUMANA_EXP",
        "cpt_code": "80053",
        "modifiers": [],
        "is_denied": False
    }
}

# LOSS TYPE 3: Unworked Appeals (Stage 6 Appeals Agent)
RECOVER_SCENARIOS = {
    "Medical Necessity Denial (CO-16)": {
        "claim_id": "RECOVER-CO16-001",
        "payer_id": "MEDICARE",
        "denial_code": "CO-16",
        "claim_data": {"cpt_code": "81479", "test_name": "Unlisted Molecular"}
    },
    "Experimental/Investigational (CO-50)": {
        "claim_id": "RECOVER-CO50-002",
        "payer_id": "CIGNA",
        "denial_code": "CO-50",
        "claim_data": {"cpt_code": "81519", "test_name": "Oncotype DX"}
    }
}
