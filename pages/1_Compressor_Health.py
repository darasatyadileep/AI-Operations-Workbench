import os
import streamlit as st
import requests
import pandas as pd
from ui_shared import apply_theme, module_header


COMPRESSOR_API_URL = os.getenv("COMPRESSOR_API_URL", "http://127.0.0.1:8001/compressor/analyze")

st.set_page_config(
    page_title="AI Operations Workbench",
    page_icon="⚙️",
    layout="wide"
)

apply_theme()
module_header("Module 01 · Predictive Analytics", "Compressor Health Monitoring", "Detect abnormal compressor operating behaviour using a trained anomaly-detection model and trend-based health interpretation.")

tab1, tab2 = st.tabs([
    "Compressor Health",
    "Architecture & Technology Options"
])

with tab1:
    st.subheader("Compressor Health Monitoring")

    st.markdown(
        """
        Upload compressor operating data to assess whether the latest behavior
        is normal or drifting toward an abnormal condition.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload compressor CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        if st.button("Analyze Compressor", type="primary"):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            }

            try:
                response = requests.post(
                    COMPRESSOR_API_URL,
                    files=files
                )

                if response.status_code == 200:
                    result = response.json()

                    st.success("Analysis completed successfully")

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Current Status", result["status"])
                    col2.metric(
                        "Current Anomaly Score",
                        result["current_anomaly_score"]
                    )
                    col3.metric(
                        "Rows Analyzed",
                        result["rows_analyzed"]
                    )

                    st.subheader("Anomaly Trend")

                    trend_df = pd.DataFrame(result["trend"])
                    trend_df["timestamp"] = pd.to_datetime(
                        trend_df["timestamp"]
                    )
                    trend_df = trend_df.set_index("timestamp")

                    st.line_chart(
                        trend_df["anomaly_score"]
                    )

                    st.subheader("Alert Thresholds")

                    t1, t2 = st.columns(2)

                    t1.metric(
                        "Attention Threshold",
                        result["attention_threshold"]
                    )

                    t2.metric(
                        "High Threshold",
                        result["high_threshold"]
                    )

                    with st.expander("How it works"):
                        st.markdown(
                            """
                            **1. Upload operational data**

                            Compressor measurements such as pressure,
                            temperature, flow, speed, power, vibration
                            and bearing temperature are provided.

                            **2. Feature engineering**

                            Additional indicators are calculated:
                            - Pressure ratio
                            - Temperature rise
                            - Power per unit flow

                            **3. Scaling**

                            New measurements are transformed using the same
                            scaling rules learned from the normal training data.

                            **4. Anomaly detection**

                            A trained Isolation Forest compares the new
                            operating patterns with the learned normal envelope.

                            **5. Health interpretation**

                            Anomaly scores are smoothed and compared with
                            thresholds derived from normal historical operation.

                            **6. Result**

                            The application reports:
                            - Normal
                            - Attention
                            - High
                            """
                        )

                else:
                    st.error(
                        f"Backend error: {response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the FastAPI backend. "
                    "Make sure the Compressor Health API is running on port 8001."
                )


with tab2:
    st.header("Module 1 — Compressor Health")

    st.subheader("End-to-End Architecture")

    st.code("""
User
 ↓
Streamlit Frontend
 ↓
API Request
 ↓
FastAPI Backend
 ↓
Data Validation
 ↓
Feature Engineering
 ↓
Scaler
 ↓
Isolation Forest Model
 ↓
Threshold / Business Logic
 ↓
API Response
 ↓
Frontend Dashboard
    """)

    st.subheader("Technology Options")

    options = pd.DataFrame({
        "Layer": [
            "Data Development",
            "ML Model",
            "Model Storage",
            "Backend",
            "Frontend",
            "Database",
            "File Storage",
            "Deployment",
            "Monitoring"
        ],
        "Used in MVP": [
            "Jupyter + Python",
            "scikit-learn Isolation Forest",
            ".pkl / joblib",
            "FastAPI",
            "Streamlit",
            "Not used yet",
            "Local folder",
            "Local PC",
            "Not used yet"
        ],
        "Alternatives": [
            "Azure ML, Dataiku, Databricks",
            "Autoencoder, One-Class SVM, XGBoost",
            "ONNX, MLflow, Azure ML Registry",
            "Flask, Django, Serverless Functions",
            "React/Next.js, Gradio, Dash, Power Apps",
            "PostgreSQL, SQL Server, Cosmos DB",
            "Azure Blob Storage, AWS S3",
            "Azure App Service, Container Apps, VM, Kubernetes",
            "Azure Monitor, App Insights, MLflow"
        ]
    })

    st.dataframe(
        options,
        use_container_width=True
    )

    st.subheader("Module Status")

    st.markdown(
        """
        - Synthetic dataset created ✅
        - Feature engineering completed ✅
        - Isolation Forest trained ✅
        - Model validated ✅
        - Model artifacts saved ✅
        - FastAPI backend built ✅
        - API tested ✅
        - Streamlit frontend built ✅
        - Trend visualization added ✅
        - Basic validation logic added ✅
        - Cloud deployment pending
        - Production monitoring pending
        """
    )