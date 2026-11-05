from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import numpy as np
import joblib
import json
import io

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Compressor Health API")

# -----------------------------
# Load trained model artifacts
# -----------------------------

model = joblib.load(BASE_DIR / "compressor_isolation_forest.pkl")
scaler = joblib.load(BASE_DIR / "compressor_scaler.pkl")

with open(BASE_DIR / "compressor_thresholds.json", "r") as f:
    thresholds = json.load(f)

# -----------------------------
# Model feature list
# -----------------------------

features = [
    "suction_pressure_bar",
    "discharge_pressure_bar",
    "suction_temperature_C",
    "discharge_temperature_C",
    "gas_flow_ksm3h",
    "compressor_speed_rpm",
    "power_MW",
    "DE_vibration_mm_s",
    "NDE_vibration_mm_s",
    "DE_bearing_temperature_C",
    "NDE_bearing_temperature_C",
    "pressure_ratio",
    "temperature_rise_C",
    "power_per_flow"
]

# -----------------------------
# Required raw input columns
# -----------------------------

required_columns = [
    "timestamp",
    "suction_pressure_bar",
    "discharge_pressure_bar",
    "suction_temperature_C",
    "discharge_temperature_C",
    "gas_flow_ksm3h",
    "compressor_speed_rpm",
    "power_MW",
    "DE_vibration_mm_s",
    "NDE_vibration_mm_s",
    "DE_bearing_temperature_C",
    "NDE_bearing_temperature_C"
]

# -----------------------------
# Root endpoint
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Compressor Health API is running"
    }

# -----------------------------
# Compressor analysis endpoint
# -----------------------------

@app.post("/compressor/analyze")
async def analyze_compressor(file: UploadFile = File(...)):

    # Read uploaded file
    raw = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read CSV file"
        )

    # -----------------------------
    # Data validation
    # -----------------------------

    # Check required columns
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Required columns are missing",
                "missing_columns": missing_columns
            }
        )

    # Validate timestamp
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Timestamp column contains invalid values"
        )

    # Check duplicate timestamps
    duplicate_count = df["timestamp"].duplicated().sum()

    if duplicate_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"{duplicate_count} duplicate timestamps found"
        )

    # Check missing values
    missing_count = df[required_columns].isnull().sum().sum()

    if missing_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"{missing_count} missing values found"
        )

    # Basic physical checks
    if (df["gas_flow_ksm3h"] <= 0).any():
        raise HTTPException(
            status_code=400,
            detail="Gas flow contains zero or negative values"
        )

    if (df["suction_pressure_bar"] <= 0).any():
        raise HTTPException(
            status_code=400,
            detail="Suction pressure contains invalid values"
        )

    if (df["discharge_pressure_bar"] <= 0).any():
        raise HTTPException(
            status_code=400,
            detail="Discharge pressure contains invalid values"
        )

    # -----------------------------
    # Feature engineering
    # -----------------------------

    df["pressure_ratio"] = (
        df["discharge_pressure_bar"]
        / df["suction_pressure_bar"]
    )

    df["temperature_rise_C"] = (
        df["discharge_temperature_C"]
        - df["suction_temperature_C"]
    )

    df["power_per_flow"] = (
        df["power_MW"]
        / df["gas_flow_ksm3h"]
    )

    X_new = df[features]

    # Final numerical safety check
    if X_new.isnull().any().any():
        raise HTTPException(
            status_code=400,
            detail="Missing values found after feature engineering"
        )

    if np.isinf(X_new.to_numpy()).any():
        raise HTTPException(
            status_code=400,
            detail="Infinite values found in processed data"
        )

    # -----------------------------
    # Scaling
    # -----------------------------

    X_scaled = scaler.transform(X_new)

    # -----------------------------
    # Model inference
    # -----------------------------

    scores = -model.decision_function(X_scaled)

    # Smooth anomaly score over 24 hours
    score_series = pd.Series(scores)

    smoothed_scores = (
        score_series
        .rolling(24, min_periods=1)
        .mean()
    )

    current_score = float(
        smoothed_scores.iloc[-1]
    )

    # -----------------------------
    # Status logic
    # -----------------------------

    if current_score >= thresholds["high_threshold"]:
        status = "High"

    elif current_score >= thresholds["attention_threshold"]:
        status = "Attention"

    else:
        status = "Normal"

    # -----------------------------
    # Explainability support
    # -----------------------------
    # This is not causal feature importance. It shows which variables in the
    # latest 24-hour window are furthest from the normal training baseline
    # after applying the saved StandardScaler.
    recent_scaled = X_scaled[-min(24, len(X_scaled)):]
    recent_deviation = np.mean(np.abs(recent_scaled), axis=0)
    variable_deviations = sorted(
        [
            {
                "variable": feature,
                "deviation_from_normal": round(float(deviation), 2)
            }
            for feature, deviation in zip(features, recent_deviation)
        ],
        key=lambda item: item["deviation_from_normal"],
        reverse=True
    )[:5]

    # -----------------------------
    # Trend data for frontend chart
    # -----------------------------

    trend = []

    for i in range(0, len(df), 24):
        trend.append({
            "timestamp": df.iloc[i]["timestamp"].isoformat(),
            "anomaly_score": round(
                float(smoothed_scores.iloc[i]),
                4
            )
        })

    # -----------------------------
    # API response
    # -----------------------------

    return {
        "rows_analyzed": len(df),
        "current_anomaly_score": round(
            current_score,
            4
        ),
        "status": status,
        "attention_threshold": round(
            thresholds["attention_threshold"],
            4
        ),
        "high_threshold": round(
            thresholds["high_threshold"],
            4
        ),
        "trend": trend,
        "variable_deviations": variable_deviations
    }