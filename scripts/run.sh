#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.9+" >&2
  exit 1
fi

VENV_DIR="${PROJECT_DIR}/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip >/dev/null

echo "Installing dependencies..."
pip install -r requirements.txt

# Optional: load .env if present
if [[ -f .env ]]; then
  echo "Loading environment from .env"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${PORT:-8000}"
APP_MODULE="app.main:app"

echo "Starting server at http://localhost:${PORT}"
exec uvicorn "$APP_MODULE" --reload --port "$PORT"


