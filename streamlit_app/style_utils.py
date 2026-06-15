import streamlit as st

def apply_premium_style():
    st.markdown("""
        <style>
        /* Main Background and Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f8fafc;
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }

        [data-testid="stHeader"] {
            background-color: rgba(248, 250, 252, 0.8);
            backdrop-filter: blur(10px);
        }

        /* Premium Light Cards */
        .premium-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .premium-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border-color: #3b82f6;
        }

        /* Metrics Styling - High Readability */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            letter-spacing: -0.02em !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.075em;
            font-size: 0.85rem !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }

        /* Button Styling - World Class */
        .stButton>button {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            width: 100%;
            border: 1px solid #1d4ed8;
        }
        
        .stButton>button:hover {
            background: #1d4ed8;
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
            border-color: #1e40af;
        }

        /* Title Styling */
        .main-title {
            color: #0f172a;
            font-size: 4rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .sub-text {
            color: #64748b;
            font-size: 1.25rem;
            font-weight: 400;
            margin-bottom: 2.5rem;
        }

        /* Badges */
        .premium-badge {
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .badge-blue { background: #eff6ff; color: #2563eb; border: 1px solid #dbeafe; }
        .badge-green { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }

        /* Text Overrides */
        h1, h2, h3, h4, h5, h6, p, span, li {
            color: #1e293b;
        }

        hr {
            margin: 2rem 0;
            border-color: #e2e8f0;
        }

        </style>
    """, unsafe_allow_html=True)
