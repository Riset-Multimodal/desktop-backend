#!/usr/bin/env bash
set -e

# Jalankan migrasi jika DATABASE_URL tersedia
if [ -n "$DATABASE_URL" ]; then
  echo "[entrypoint] Running Alembic migrations..."
  alembic upgrade head
fi

echo "[entrypoint] Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-3001}" --workers 4
