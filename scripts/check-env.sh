#!/usr/bin/env bash
# Prints each tool's version and exits non-zero naming the first one that is missing or too old.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

if ! docker_version="$(docker compose version 2>&1)"; then
  fail "docker compose is not available. Turn on Docker Desktop > Settings > Resources > WSL integration > Ubuntu."
fi
echo "docker compose: ${docker_version}"

want_node="$(tr -d '[:space:]' < "${root}/frontend/.nvmrc")"
want_node="${want_node#v}"
if ! node_version="$(node --version 2>&1)"; then
  fail "node is not installed. Install nvm, then run 'nvm install' in frontend/."
fi
node_major="${node_version#v}"
node_major="${node_major%%.*}"
echo "node: ${node_version}"
if [ "${node_major}" != "${want_node}" ]; then
  fail "node ${node_version} is the wrong version; frontend/.nvmrc wants ${want_node}. Run 'nvm install' in frontend/."
fi

if ! uv_version="$(uv --version 2>&1)"; then
  fail "uv is not on PATH. In a non-login shell run 'bash -lc'."
fi
echo "uv: ${uv_version}"

want_python="$(tr -d '[:space:]' < "${root}/backend/.python-version")"
if ! python_version="$(uv run --project "${root}/backend" python --version 2>&1)"; then
  fail "uv could not run python from backend/: ${python_version}"
fi
echo "python: ${python_version}"
case "${python_version}" in
  "Python ${want_python}."*) ;;
  *) fail "${python_version} is the wrong version; backend/.python-version wants ${want_python}." ;;
esac

echo "OK"
