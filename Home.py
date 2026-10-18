import os
import requests
import streamlit as st
from ui_shared import apply_theme, card

st.set_page_config(page_title="AI Operations Workbench", page_icon="⚙️", layout="wide")
apply_theme()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Industrial AI • End-to-End Portfolio</div>
        <h1>AI Operations Workbench</h1>
        <p>A unified industrial AI application combining predictive analytics, mathematical optimization, computer vision/OCR, and GenAI/agentic technology intelligence — from data and model logic through APIs, application architecture and deployment-ready services.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Portfolio Overview</div>', unsafe_allow_html=True)
st.subheader("Four AI capabilities. One operating interface.")

c1, c2 = st.columns(2)
with c1:
    card("01 · Compressor Health Monitoring",
         "Detect abnormal compressor behaviour from multivariate operating data and surface health trends for early attention.",
         ["Predictive Analytics", "Isolation Forest", "FastAPI"])
    card("03 · Visual Operator Rounds",
         "Extract information from industrial equipment nameplates using image preprocessing, OCR and structured business logic.",
         ["Computer Vision", "OpenCV", "EasyOCR"])
with c2:
    card("02 · Gas Feed Allocation Optimizer",
         "Optimize feed routing across plants and fractionators to maximize synthetic product value subject to physical constraints.",
         ["Optimization", "SciPy LP", "Decision Support"])
    card("04 · Technology Intelligence",
         "Collect and structure oil & gas technology developments, score maturity/significance and retain a historical intelligence repository.",
         ["GenAI / Agents", "Web Retrieval", "SQLite"])

st.divider()
st.markdown('<div class="section-label">System Readiness</div>', unsafe_allow_html=True)
st.subheader("Local services")

services = [
    ("Compressor API", os.getenv("COMPRESSOR_API_BASE", "http://127.0.0.1:8001/")),
    ("Optimizer API", os.getenv("OPTIMIZER_API_BASE", "http://127.0.0.1:8002/")),
    ("Vision API", os.getenv("VISION_API_BASE", "http://127.0.0.1:8003/")),
    ("Intelligence API", os.getenv("INTELLIGENCE_API_BASE", "http://127.0.0.1:8004/")),
]
cols = st.columns(4)
for col, (name, url) in zip(cols, services):
    try:
        r = requests.get(url, timeout=0.8)
        online = r.status_code < 500
    except Exception:
        online = False
    with col:
        st.metric(name, "Online" if online else "Offline")
        st.caption("Ready for requests" if online else "Start Workbench services")

st.divider()
st.markdown('<div class="section-label">Architecture</div>', unsafe_allow_html=True)
st.subheader("How the Workbench is assembled")

st.code(
"""User
  │
  ▼
Unified Streamlit Web Interface
  │
  ├── Compressor Health API        :8001
  ├── Feed Optimizer API           :8002
  ├── Visual Operator Rounds API   :8003
  └── Technology Intelligence API  :8004
          │
          ▼
Models • Optimization Engines • OCR • LLM / Rule Engine
          │
          ▼
Model Artifacts • Input Files • SQLite / Storage
"""
)

st.info("Use the left navigation to open a module. The Architecture & About page documents the full end-to-end design and deployment path.")
