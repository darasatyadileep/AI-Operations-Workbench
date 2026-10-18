from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from pathlib import Path
import pandas as pd
import tempfile
import shutil

from optimizer import run_optimizer

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "module2_feed_allocation_inputs_v1.xlsx"

app = FastAPI(title="Feed Allocation Optimizer API")

class ScenarioPayload(BaseModel):
    feeds: list[dict]
    plants: list[dict]
    fractionation: list[dict]
    prices: list[dict]


def _read_scenario(path=INPUT_FILE):
    feeds = pd.read_excel(path, sheet_name="Feeds")
    plants = pd.read_excel(path, sheet_name="Plants")
    fractionation = pd.read_excel(path, sheet_name="Fractionation")
    prices = pd.read_excel(path, sheet_name="Product_Prices")
    # Start the UI with the demonstrative downstream capacities used in the prior MVP.
    demo_caps = {"FR1": 18000, "FR2": 16000, "FR3": 15000}
    fractionation["Max_NGL_kmol_per_day"] = fractionation.apply(
        lambda r: demo_caps.get(r["Fractionator_ID"], r["Max_NGL_kmol_per_day"]), axis=1
    )
    return {
        "feeds": feeds.to_dict("records"),
        "plants": plants.to_dict("records"),
        "fractionation": fractionation.to_dict("records"),
        "prices": prices.to_dict("records"),
    }


def _write_scenario(payload: ScenarioPayload, target: Path):
    # Preserve detailed engineering assumptions from the master workbook;
    # replace the scenario-level operating/economic inputs exposed in the UI.
    recovery = pd.read_excel(INPUT_FILE, sheet_name="Feed_Plant_Recovery")
    routing = pd.read_excel(INPUT_FILE, sheet_name="Routing")
    overview = pd.read_excel(INPUT_FILE, sheet_name="Overview")
    with pd.ExcelWriter(target, engine="openpyxl") as writer:
        overview.to_excel(writer, sheet_name="Overview", index=False)
        pd.DataFrame(payload.feeds).to_excel(writer, sheet_name="Feeds", index=False)
        pd.DataFrame(payload.plants).to_excel(writer, sheet_name="Plants", index=False)
        recovery.to_excel(writer, sheet_name="Feed_Plant_Recovery", index=False)
        pd.DataFrame(payload.fractionation).to_excel(writer, sheet_name="Fractionation", index=False)
        routing.to_excel(writer, sheet_name="Routing", index=False)
        pd.DataFrame(payload.prices).to_excel(writer, sheet_name="Product_Prices", index=False)

@app.get("/")
def home():
    return {"message": "Feed Allocation Optimizer API is running"}

@app.get("/optimizer/inputs")
def optimizer_inputs():
    return _read_scenario()

@app.post("/optimizer/run")
def optimize(payload: Optional[ScenarioPayload] = None):
    if payload is None:
        return run_optimizer(str(INPUT_FILE))
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        _write_scenario(payload, temp_path)
        return run_optimizer(str(temp_path))
    finally:
        temp_path.unlink(missing_ok=True)

@app.post("/optimizer/upload")
async def optimize_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Upload an Excel workbook (.xlsx or .xls).")
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        temp_path = Path(tmp.name)
        shutil.copyfileobj(file.file, tmp)
    try:
        return run_optimizer(str(temp_path))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not optimize uploaded workbook: {exc}")
    finally:
        temp_path.unlink(missing_ok=True)
