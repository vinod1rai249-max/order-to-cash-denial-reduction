import streamlit as st
import requests
from style_utils import apply_premium_style
from demo_data import PREVENT_SCENARIOS, CATCH_SCENARIOS, RECOVER_SCENARIOS

st.set_page_config(
    page_title="Order-to-Cash AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_premium_style()

API_BASE = "http://127.0.0.1:8080"

# Header Section
st.markdown('<h1 class="main-title">Order-to-Cash AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Intelligent Denial Reduction & Autonomous Revenue Recovery</p>', unsafe_allow_html=True)

# A/B Toggle Section
st.markdown("### ⚙️ Demo Configuration")
col_toggle, col_empty = st.columns([1, 2])
with col_toggle:
    ai_enabled = st.toggle("🚀 Activate AI-Assisted Workflow", value=True, help="Toggle OFF to see the 'Standard' workflow where denials occur.")
    mode_text = "✨ AI-ASSISTED" if ai_enabled else "⚠️ STANDARD (NO AI)"
    st.markdown(f"**Current Mode:** `{mode_text}`")

# Main Grid
col1, col2 = st.columns(2, gap="large")
# ... (rest of layout unchanged) ...

st.markdown("---")

# Management Narrative: Three Types of Denial Loss
st.subheader("📊 The Management Demo: Traceable Denial Reduction")
st.markdown("<p style='color: #64748b; margin-top: -10px; margin-bottom: 25px;'>Select a scenario to witness how AI-driven data flow eliminates financial waste.</p>", unsafe_allow_html=True)

loss_col1, loss_col2, loss_col3 = st.columns(3, gap="medium")

# Initialize session state for trace logs
if 'trace_logs' not in st.session_state:
    st.session_state.trace_logs = None

with loss_col1:
    st.markdown('<div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; height: 120px;">'
                '<h4 style="margin-top: 0; color: #0f172a;">1. Preventable Write-offs</h4>'
                '<p style="font-size: 0.85rem; color: #64748b;">Stage 1: Stops denials at origin.</p></div>', unsafe_allow_html=True)
    scenario_1 = st.selectbox("Select Prevent Scenario", options=list(PREVENT_SCENARIOS.keys()), key="sel_1")
    if st.button("Run Prevent Scenario", use_container_width=True):
        try:
            payload = PREVENT_SCENARIOS[scenario_1].copy()
            payload["ai_enabled"] = ai_enabled
            res = requests.post(f"{API_BASE}/api/v1/order", json=payload)
            st.session_state.trace_logs = {"scenario": scenario_1, "data": res.json(), "ai": ai_enabled}
            st.toast(f"Executed: {scenario_1}", icon="✅")
        except Exception as e: st.error(f"Error: {e}")

with loss_col2:
    st.markdown('<div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; height: 120px;">'
                '<h4 style="margin-top: 0; color: #0f172a;">2. Missed Deadlines</h4>'
                '<p style="font-size: 0.85rem; color: #64748b;">Stage 5: Catch risk before submission.</p></div>', unsafe_allow_html=True)
    scenario_2 = st.selectbox("Select Catch Scenario", options=list(CATCH_SCENARIOS.keys()), key="sel_2")
    if st.button("Run Catch Scenario", use_container_width=True):
        try:
            payload = CATCH_SCENARIOS[scenario_2].copy()
            payload["ai_enabled"] = ai_enabled
            res = requests.post(f"{API_BASE}/api/v1/order", json=payload)
            st.session_state.trace_logs = {"scenario": scenario_2, "data": res.json(), "ai": ai_enabled}
            st.toast(f"Executed: {scenario_2}", icon="🔍")
        except Exception as e: st.error(f"Error: {e}")

with loss_col3:
    st.markdown('<div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; height: 120px;">'
                '<h4 style="margin-top: 0; color: #0f172a;">3. Unworked Appeals</h4>'
                '<p style="font-size: 0.85rem; color: #64748b;">Stage 6: Recover abandoned money.</p></div>', unsafe_allow_html=True)
    scenario_3 = st.selectbox("Select Recover Scenario", options=list(RECOVER_SCENARIOS.keys()), key="sel_3")
    if st.button("Run Recover Scenario", use_container_width=True):
        try:
            payload = RECOVER_SCENARIOS[scenario_3].copy()
            payload["ai_enabled"] = ai_enabled
            res = requests.post(f"{API_BASE}/api/v1/appeal", json=payload)
            st.session_state.trace_logs = {"scenario": scenario_3, "data": res.json(), "ai": ai_enabled}
            st.toast(f"Executed: {scenario_3}", icon="⚖️")
        except Exception as e: st.error(f"Error: {e}")

# Live Pipeline Trace Visualization
if st.session_state.trace_logs:
    trace = st.session_state.trace_logs
    st.markdown(f"### 🧬 End-to-End Data Journey: {trace['scenario']}")
    
    # A/B Header
    if trace['ai']:
        st.success("✨ AI-ASSISTED FLOW (Denial Protected)")
    else:
        st.error("⚠️ STANDARD WORKFLOW (Denial Imminent/Occurred)")

    with st.expander("View Data Journey Detail", expanded=True):
        trace_cols = st.columns([1, 2, 1])
        with trace_cols[0]:
            st.markdown("##### 📥 Input Payload")
            st.json(trace['data'].get("sanitized_data", trace['data']))
        
        with trace_cols[1]:
            st.markdown("##### 🧠 AI Reasoning Agent")
            logs = trace['data'].get("logs", [])
            if logs:
                for log in logs:
                    st.info(log["details"])
            elif "appeal_details" in trace['data']:
                details = trace['data']['appeal_details']
                if details:
                    st.info("AI drafted a complete appeal letter citing insurance policy.")
                else:
                    st.warning("Manual appeal required (Unworked).")
            
        with trace_cols[2]:
            st.markdown("##### 📜 GCP Governance Log")
            st.markdown(f"**Status:** `{trace['data'].get('status', 'Logged')}`")
            st.success("Immutable audit record committed to BigQuery.")

st.markdown("---")

# Footer Features
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("#### 🔒 HIPAA Compliant\nBuilt-in PHI redaction via Google Cloud DLP.")
with f2:
    st.markdown("#### 🧠 Agentic Workflows\nStateful orchestration using LangGraph.")
with f3:
    st.markdown("#### 📜 Proof Layer\nImmutable governance logs in BigQuery.")

st.markdown('<div style="text-align: center; color: #52525b; font-size: 0.8rem; margin-top: 4rem;">© 2026 ADPO Healthcare AI • Proprietary & Confidential</div>', unsafe_allow_html=True)
