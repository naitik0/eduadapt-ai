#!/usr/bin/env bash
# Recreate the database with the catalog and the 5 demo students. Pass --keep to not drop tables.
set -euo pipefail
cd "$(dirname "$0")/../backend"
if [ "${1:-}" = "--keep" ]; then python3 -m app.seed; else python3 -m app.seed --reset; fi
