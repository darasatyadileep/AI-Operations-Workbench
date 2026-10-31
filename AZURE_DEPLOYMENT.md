# Azure Deployment — AI Operations Workbench

Target architecture:

GitHub -> GitHub Actions -> Azure Container Registry -> Azure Container Apps
                                              |
                                              -> React + FastAPI + AI modules in one container

Public application:
- React frontend at /
- FastAPI health endpoint at /api/health
- Compressor API under /api/compressor
- Optimizer API under /api/optimizer
- Vision API under /api/vision
- Technology Intelligence API under /api/intelligence

Recommended region: UAE North (if available to your subscription).

Recommended first deployment:
- Azure Container Apps Consumption
- External ingress
- Target port: 8000
- Min replicas: 0
- Max replicas: 1
- 1 vCPU / 2 GiB memory minimum for OCR demonstration
- Add OPENAI_API_KEY later as a Container Apps secret/environment variable if API credits are available.

The repository-root Dockerfile builds the React frontend and packages it with the consolidated FastAPI backend.

After these files are committed to GitHub, use Azure Cloud Shell:

az containerapp up \
  --name ai-operations-workbench \
  --resource-group rg-ai-operations-workbench \
  --location uaenorth \
  --repo https://github.com/darasatyadileep/AI-Operations-Workbench \
  --ingress external \
  --target-port 8000

The Azure CLI flow can create the resource group, Container Apps environment, registry, deployment, and GitHub Actions workflow.
