# Multi-stage Dockerfile for TuneTrail (React Frontend + Flask Backend)

FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_PORT=5000 \
    DATABASE_PATH=/app/database/tunetrail.db

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY database/ ./database/
COPY datasets/ ./datasets/
COPY recommendation_engine/ ./recommendation_engine/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

RUN python -m database.seed

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "backend.app:create_app()"]
