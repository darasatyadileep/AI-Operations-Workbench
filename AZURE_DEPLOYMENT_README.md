# AI Operations Workbench — Azure deployment preparation

## What changed
The Workbench is now container-ready. Each backend is an independent FastAPI service and the Streamlit website is a separate frontend container.

Services:
- Compressor Health API — port 8001
- Feed Optimizer API — port 8002
- Visual Operator Rounds API — port 8003
- Technology Intelligence API — port 8004
- Unified Streamlit frontend — port 8501

The frontend now reads API locations from environment variables. This means the same code works locally and in the cloud without rewriting URLs.

## Local container test
1. Install Docker Desktop.
2. Open this folder.
3. Double-click `start_docker.bat` or run `docker compose up --build`.
4. Open http://localhost:8501.
5. Test all four modules.
6. Stop with `stop_docker.bat` or `docker compose down`.

The original `start_workbench.bat` is still available, so Docker is optional for local use.

## Azure target architecture
Recommended target for the portfolio build:

User -> Azure-hosted Streamlit frontend -> four FastAPI services -> model artifacts / SQLite / external LLM API

A practical Azure implementation is to host the five containers as managed container services, configure the four API URLs as frontend environment variables, and store secrets such as the OpenAI API key as cloud secrets rather than in source code.

## Environment variables used by the frontend
- `COMPRESSOR_API_URL`
- `OPTIMIZER_API_URL`
- `VISION_API_URL`
- `INTELLIGENCE_API_BASE`
- `COMPRESSOR_API_BASE`
- `OPTIMIZER_API_BASE`
- `VISION_API_BASE`

## Technology Intelligence secrets
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Do not put a real API key in a Dockerfile, Python file, ZIP, or public repository.

## Next deployment step
After the Docker version works locally, deploy the four APIs first, record their public/internal service URLs, then deploy the frontend with those URLs supplied as environment variables. Finally test all four modules through the cloud URL.
