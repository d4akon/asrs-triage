#!/usr/bin/env bash
# Starts the API (port 8000) and the Angular client (port 4200). Ctrl+C stops both.
set -euo pipefail
cd "$(dirname "$0")"

source .venv/bin/activate
[ -f models/baseline/model.joblib ] || python scripts/export_baseline.py

uvicorn api.main:app --port 8000 &
api_pid=$!
trap 'kill $api_pid 2>/dev/null' EXIT

cd web
[ -d node_modules ] || npm install
npm start
