import streamlit as st
import pandas as pd
from ui_shared import apply_theme, module_header

st.set_page_config(page_title="Architecture & About", page_icon="🧩", layout="wide")
apply_theme()
module_header(
    "Workbench Design",
    "Architecture & About",
    "A consolidated view of the application layers, technology choices, module boundaries and the path from local prototype to cloud deployment.",
)

st.subheader("End-to-End Architecture")
st.code(
"""Browser / User
      │
      ▼
Unified Streamlit Frontend
      │
      ├──────────────┬──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
Compressor API   Optimizer API    Vision API    Intelligence API
  FastAPI          FastAPI         FastAPI          FastAPI
      │              │              │              │
Isolation       SciPy Linear     OpenCV + OCR   Collector +
Forest          Programming                     LLM/Rules
      │              │              │              │
.pkl/.json      Excel Inputs      Images         SQLite
      └──────────────┴──────────────┴──────────────┴──────────────┘
                              │
                              ▼
                    Deployment / Monitoring
"""
)

st.subheader("What each module demonstrates")
rows = [
    ["1", "Compressor Health", "Predictive analytics", "Data prep, feature engineering, scaling, anomaly detection, model artifacts, API inference"],
    ["2", "Feed Allocation Optimizer", "Optimization", "Business formulation, constraints, economic objective, linear programming, scenario comparison"],
    ["3", "Visual Operator Rounds", "Computer vision / OCR", "Image handling, preprocessing, OCR, structured interpretation, image upload API"],
    ["4", "Technology Intelligence", "GenAI / agentic workflow", "Source registry, collection, filtering, semantic analysis layer, persistence, intelligence dashboard"],
]
st.dataframe(pd.DataFrame(rows, columns=["Module", "Application", "AI discipline", "Demonstrates"]), use_container_width=True, hide_index=True)

st.subheader("Application Layers")
for title, text in [
    ("Frontend", "Streamlit provides the unified human interface and visualizes outputs from each module."),
    ("API / Backend", "FastAPI exposes each analytical capability as a service and separates UI logic from model/business logic."),
    ("Analytics Engines", "scikit-learn, SciPy optimization, OpenCV/EasyOCR, and GenAI/rule-based analysis perform the core computation."),
    ("Persistence", "Serialized model artifacts, Excel/CSV inputs and SQLite retain trained models, structured inputs and intelligence history."),
    ("Deployment Path", "The local multi-service prototype is structured for containerization and deployment to Azure services with centralized monitoring and secrets management."),
]:
    with st.expander(title, expanded=False):
        st.write(text)

st.subheader("Productionization Roadmap")
st.markdown(
"""
1. **Containerize** each FastAPI service and the Streamlit frontend.
2. **Externalize configuration** such as ports, model paths and API credentials.
3. **Move files to managed storage** and SQLite to a managed database where appropriate.
4. **Deploy to Azure** using App Service or Container Apps for the portfolio version.
5. **Add identity, secrets and monitoring** using managed identity / Key Vault / Application Insights.
6. **Add CI/CD and automated tests** for repeatable deployment.
"""
)

st.success("Portfolio objective: demonstrate understanding of the complete AI solution lifecycle — not just model development, but how models become usable applications and deployable services.")
