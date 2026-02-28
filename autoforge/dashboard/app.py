"""
AutoForge Dashboard — Main Entry Point (Home Page)

This is the landing page. Streamlit auto-discovers pages in the
`pages/` directory (code_generator.py and live_dashboard.py).
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(Path(PROJECT_ROOT) / ".env")

# Page config
st.set_page_config(
    page_title="AutoForge — SDV Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3, h4, h5, h6 { color: white !important; }
    p, span, div { color: white; }
    .stButton > button {
        background-color: #238636; color: white;
        border: none; border-radius: 6px;
    }
    .stButton > button:hover { background-color: #2ea043; }
    .stTextArea textarea { background-color: #161b22; color: white; }
</style>
""", unsafe_allow_html=True)


# ---- Home Page Content ----
# Show hero car image
import base64

car_image_path = Path(__file__).parent / "assets" / "car_hero.png"
if car_image_path.exists():
    col_img, col_title = st.columns([1, 2])
    with col_img:
        st.image(str(car_image_path), width=300)
    with col_title:
        st.title("AutoForge")
        st.markdown("### The Compliant GenAI Pipeline for Software Defined Vehicles")
else:
    st.title("🚗 AutoForge")
    st.markdown("### The Compliant GenAI Pipeline for Software Defined Vehicles")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ## 🤖 Code Generator
    
    Generate MISRA-compliant automotive service code from natural language requirements.
    
    **Full Pipeline:**
    1. 📋 Requirement Refinement
    2. 📝 Code Generation (C++, Rust, Kotlin)
    3. 🔨 Self-Healing Build
    4. 📋 Static Analysis (MISRA Check)
    5. 🧪 Test Generation
    6. 📡 OTA Service Registration
    
    👉 **Click "code generator" in the sidebar to start!**
    """)

with col2:
    st.markdown("""
    ## 🏠 Live Dashboard
    
    Real-time vehicle health monitoring with predictive diagnostics.
    
    **Features:**
    - 📊 Real-time VSS signal gauges
    - 📈 Trend charts and history
    - 🔮 Predictive diagnostics (AI-powered)
    - 🚨 Active alerts and fault injection
    - 🏭 Vehicle variant config (ICE/Hybrid/EV)
    
    👉 **Click "live dashboard" in the sidebar to view!**
    """)

st.markdown("---")

# Quick stats
st.markdown("### 📊 System Status")

col1, col2, col3, col4 = st.columns(4)

import os
outputs_path = Path("autoforge/outputs")
service_count = len([d for d in outputs_path.iterdir() if d.is_dir()]) if outputs_path.exists() else 0

with col1:
    st.metric("Generated Services", service_count)
with col2:
    st.metric("Knowledge Chunks", "50")
with col3:
    st.metric("Supported Languages", "3")
with col4:
    api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    status = "✅ Set" if api_key else "❌ Missing"
    st.metric("API Key", status)

if not api_key:
    st.warning("⚠️ **API Key not set!** Add GEMINI_API_KEY or OPENAI_API_KEY to `.env`.")
