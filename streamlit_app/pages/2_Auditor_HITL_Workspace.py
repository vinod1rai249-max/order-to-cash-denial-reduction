import os
import streamlit as st
import requests
from style_utils import apply_premium_style

st.set_page_config(page_title="Auditor HITL Workspace", page_icon="🛡️", layout="wide")
apply_premium_style()

# Backend URL configuration
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")

# Header
st.markdown('<h1 class="main-title" style="font-size: 3rem;">Auditor Workspace</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text" style="margin-top: -1.5rem;">Stage 6: GOVERN — Human-in-the-Loop AI Oversight</p>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; margin-top: -20px; margin-bottom: 30px;'>Review AI-drafted appeals, verify policy evidence, and commit final decisions to the immutable audit trail.</p>", unsafe_allow_html=True)

# Fetch Queue
try:
    response = requests.get(f"{API_URL}/api/v1/dashboard/hitl")
    if response.status_code == 200:
        queue = response.json()
        
        if not queue:
            st.markdown("""
                <div class="premium-card" style="text-align: center; padding: 100px;">
                    <h3 style="color: #16a34a;">✅ All Claims Cleared</h3>
                    <p style="color: #64748b;">The clinical audit queue is currently empty.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Check for New Tasks", use_container_width=True):
                st.rerun()
        else:
            st.markdown(f"### 📥 Pending Review ({len(queue)})")
            
            for task in queue:
                with st.container():
                    st.markdown(f"""
                        <div class="premium-card">
                            <div class="premium-badge badge-blue">CLAIM #{task['claim_id']}</div>
                            <span style="float: right; color: #64748b; font-size: 0.9rem; font-weight: 500;">Received: {task['timestamp']}</span>
                            <h2 style="margin-top: 5px; color: #0f172a;">Payer: {task['payer']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Split view inside container
                    c1, c2 = st.columns([1, 1], gap="medium")
                    
                    with c1:
                        st.markdown("""
                            <div class="premium-card" style="background: #f8fafc; border-color: #cbd5e1;">
                                <h4 style="color: #2563eb; margin-top: 0;">1. Policy Evidence (RAG)</h4>
                                <p style="font-size: 1rem; line-height: 1.6; color: #334155; font-style: italic; background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
                                    "{content}"
                                </p>
                                <p style="font-size: 0.8rem; color: #64748b; margin-top: 15px; font-weight: 500;">Source: {source}</p>
                                <hr style="margin: 20px 0; border-color: #e2e8f0;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">AI CONFIDENCE</span>
                                    <span style="color: #16a34a; font-weight: 800; font-size: 1.5rem;">{conf}%</span>
                                </div>
                            </div>
                        """.format(
                            content=task['details']['policy_citation'],
                            source=task['details']['source'],
                            conf=int(task['confidence']*100)
                        ), unsafe_allow_html=True)
                        
                    with c2:
                        st.markdown('<h4 style="margin-top: 0; color: #0f172a;">2. AI Appeal Letter Draft</h4>', unsafe_allow_html=True)
                        edited_letter = st.text_area(
                            "Audit Log & Final Edit", 
                            value=task['details']['draft_letter'], 
                            height=350, 
                            key=f"area_{task['claim_id']}",
                            label_visibility="collapsed"
                        )
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✅ Finalize & Approve", key=f"app_{task['claim_id']}", use_container_width=True):
                                app_res = requests.post(f"{API_URL}/api/v1/hitl/approve/{task['claim_id']}")
                                if app_res.status_code == 200:
                                    st.toast(f"Claim {task['claim_id']} Approved and Logged to Governance Sink", icon="✅")
                                    st.rerun()
                        with col_btn2:
                            st.button("❌ Flag for Manual Re-work", key=f"rej_{task['claim_id']}", use_container_width=True)

    else:
        st.error("Backend Response Error: Status Code 500")

except Exception as e:
    st.error("API Connectivity Error: Is the Backend Running?")
