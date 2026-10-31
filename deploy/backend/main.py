import importlib.util
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
MODULES = BASE_DIR / "modules"

# Make module-local imports such as optimizer.py, vision_engine.py and research_api.py resolvable.
for d in [MODULES/"compressor", MODULES/"optimizer", MODULES/"vision", MODULES/"intelligence"]:
    sys.path.insert(0, str(d))

def load_app(alias: str, path: Path):
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app

compressor_app = load_app("workbench_compressor_app", MODULES/"compressor"/"app.py")
optimizer_app = load_app("workbench_optimizer_app", MODULES/"optimizer"/"app.py")
vision_app = load_app("workbench_vision_app", MODULES/"vision"/"app.py")
intelligence_app = load_app("workbench_intelligence_app", MODULES/"intelligence"/"app.py")

app = FastAPI(title="AI Operations Workbench")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "application": "AI Operations Workbench",
        "modules": ["compressor", "optimizer", "vision", "intelligence"]
    }

app.mount("/api/compressor", compressor_app)
app.mount("/api/optimizer", optimizer_app)
app.mount("/api/vision", vision_app)
app.mount("/api/intelligence", intelligence_app)

frontend = BASE_DIR / "frontend_dist"
app.mount("/", StaticFiles(directory=str(frontend), html=True), name="frontend")
