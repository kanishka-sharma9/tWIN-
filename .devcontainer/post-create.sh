#!/usr/bin/env bash
set -euo pipefail

(cd backend && uv sync)

if [ -f frontend/package.json ]; then
  (cd frontend && npm ci)
fi
