import streamlit as st
import requests
from style_utils import apply_premium_style

st.set_page_config(page_title="CFO Control Center", page_icon="📊", layout="wide")
apply_premium_style()

API_URL = "http://127.0.0.1:8080"

# Header
st.markdown('<h1 class="main-title" style="font-size: 3rem;">CFO Control Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text" style="margin-top: -1.5rem;">Stage 7: The Proof Layer — Traceable Revenue Protection</p>', unsafe_allow_html=True)

# Fetch Data
try:
    response = requests.get(f"{API_URL}/api/v1/dashboard/cfo")
    if response.status_code == 200:
        data = response.json()
        kpis = data.get("kpis", {})
        logs = data.get("logs", [])
        
        # Dashboard Grid
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.metric("Preventable Write-offs", kpis.get("preventable_write_offs_stopped", 0))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with m2:
            st.markdown('<div class="premium-card" style="border-left: 6px solid #3b82f6;">', unsafe_allow_html=True)
            st.metric("Protected Revenue", kpis.get("revenue_protected_formatted", "$0.00"))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with m3:
            st.markdown('<div class="premium-card" style="border-left: 6px solid #ef4444;">', unsafe_allow_html=True)
            st.metric("Revenue At Risk", kpis.get("revenue_at_risk_formatted", "$0.00"))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with m4:
            st.markdown('<div class="premium-card" style="border-left: 6px solid #64748b;">', unsafe_allow_html=True)
            st.metric("Standard Denial Loss", kpis.get("standard_denial_loss_formatted", "$0.00"), help="Revenue lost in 'Standard' mode (No AI intervention).")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Visual Analytics
        col_left, col_right = st.columns([2, 1], gap="medium")
        
        with col_left:
            st.markdown("""
                <div class="premium-card" style="height: 620px;">
                    <div class="premium-badge badge-blue">LIVE BIGQUERY ANALYTICS</div>
                    <h3 style="margin-top: 0;">Enterprise BI Dashboard</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">Predictive risk modeling surfacing loss patterns before they become bad debt.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Looker Embed (Positioned inside the card area)
            looker_url = "https://lookerstudio.google.com/embed/reporting/placeholder"
            st.components.v1.iframe(looker_url, height=500, scrolling=True)
            
        with col_right:
            st.markdown("""
                <div class="premium-card" style="height: 620px; overflow-y: auto;">
                    <div class="premium-badge badge-green">GOVERNANCE FEED</div>
                    <h3 style="margin-top: 0;">Immutable Audit Trail</h3>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 20px;">
            """, unsafe_allow_html=True)
            
            if not logs:
                st.write("No logs recorded yet. Trigger a scenario to see live tracing.")
            else:
                for log in logs:
                    color = "#2563eb" if log["agent"] == "AppealsAgent" else "#16a34a" if log["agent"] == "BillingAgent" else "#64748b"
                    st.markdown(f"""
                        <p><b>{log['agent']}:</b> {log['details']}</p>
                        <span style="font-size: 0.7rem; color: #94a3b8;">{log['timestamp']} • Confidence: {log['confidence']}</span>
                        <hr style="margin: 12px 0; opacity: 0.3;">
                    """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        st.error("Error: Backend communication failure.")

except Exception as e:
    st.error("Connection Refused: Ensure Backend (port 8000) is running.")
