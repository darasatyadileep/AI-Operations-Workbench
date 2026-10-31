# Working Website Deployment Patch

This patch adds a single deployable web application:

React frontend + one consolidated FastAPI host + all four AI modules.

Public routes:
- `/` — React Workbench
- `/api/health`
- `/api/compressor/...`
- `/api/optimizer/...`
- `/api/vision/...`
- `/api/intelligence/...`

## Recommended hosting
Azure Container Apps for the enterprise lifecycle exercise.

Why: the OCR module uses EasyOCR/PyTorch and needs materially more memory than a 512 MB free container. Serverless lets an occasional portfolio demo sleep between visits.

## Module 4
Set `OPENAI_API_KEY` as a platform environment variable only if you want live web research. Never commit a real key.

## Note
The first OCR request can be slow because EasyOCR initializes/downloads model resources when the service starts.
