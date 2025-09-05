FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=3001

WORKDIR /app

# System deps (opencv/mediapipe & psycopg2 runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libgl1 libglib2.0-0 libxext6 libsm6 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# App source
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
COPY app ./app

# Entrypoint (alembic upgrade + start uvicorn)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3001
CMD ["/entrypoint.sh"]
