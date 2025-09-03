#!/usr/bin/env bash
set -e
export PYTHONPATH=$(pwd)
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
