#!/usr/bin/env bash
# One-time setup: Python deps, dataset + model, database seed, frontend deps.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
python3 -m pip install -r backend/requirements.txt
python3 ml/generate_dataset.py
python3 ml/train_model.py
(cd backend && python3 -m app.seed --reset)
(cd frontend && npm install)
echo "Setup complete. Run scripts/run_backend.sh and scripts/run_frontend.sh"
