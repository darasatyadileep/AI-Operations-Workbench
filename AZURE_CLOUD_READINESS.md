# Azure cloud-readiness changes

This patch prepares the existing Workbench for cloud deployment without changing the core AI logic.

## Frontend
- Uses `VITE_*_API_BASE` environment variables in Azure.
- Keeps the existing `/api/...` local proxy paths for local development.
- Adds SPA routing config for Azure Static Web Apps.

## APIs
- Adds configurable CORS using `ALLOWED_ORIGINS`.
- Dockerfiles accept Azure `PORT` while preserving current local defaults.

## Technology Intelligence
- `RESEARCH_DB_PATH` is configurable so research history can later be mounted on persistent Azure storage.
- `OPENAI_API_KEY` remains an environment secret; never commit a real key.

## Recommended Azure topology
- React frontend -> Azure Static Web Apps
- Four FastAPI services -> Azure Container Apps
- Module 4 persistent history -> Azure Files / managed database later
- Secrets -> Container App secrets / Key Vault
- Monitoring -> Azure Monitor / Application Insights

## Deployment order
1. Deploy four backend services.
2. Record their HTTPS URLs.
3. Configure the four `VITE_*_API_BASE` values for the frontend build.
4. Deploy the React frontend.
5. Restrict `ALLOWED_ORIGINS` from `*` to the final frontend domain.
