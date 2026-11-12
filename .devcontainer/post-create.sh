#!/usr/bin/env bash
set -euo pipefail

uv sync

if [ -f web/package.json ]; then
  (cd web && npm ci)
fi
