FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY deploy/frontend/package.json ./
RUN npm install
COPY deploy/frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    EASYOCR_MODULE_PATH=/tmp/easyocr

WORKDIR /app

COPY deploy/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY deploy/backend/ ./backend/
COPY --from=frontend-build /frontend/dist ./backend/frontend_dist/

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
