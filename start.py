#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"


def ensure_python_version() -> None:
    if sys.version_info < (3, 11):
        print("[start] Python 3.11+ is required.")
        sys.exit(1)


def load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                os.environ.setdefault(key, value)
    except Exception:
        # Non-fatal; continue without .env
        pass


def run_with_uv(port: str) -> int:
    cmd = [
        "uv",
        "run",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        port,
    ]
    print(f"[start] Using uv: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(PROJECT_DIR))


def create_venv() -> Path:
    if not VENV_DIR.exists():
        print(f"[start] Creating virtual environment at {VENV_DIR}")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    return VENV_DIR


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_deps_in_venv(py: Path) -> None:
    deps = [
        "fastapi",
        "uvicorn[standard]",
        "jinja2",
        "sse-starlette",
        "python-multipart",
    ]
    print("[start] Upgrading pip ...")
    subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip"]) 
    print("[start] Installing runtime dependencies ...")
    subprocess.check_call([str(py), "-m", "pip", "install", *deps])


def run_with_venv(py: Path, port: str) -> int:
    cmd = [
        str(py),
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        port,
    ]
    print(f"[start] Using venv: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(PROJECT_DIR))


def main() -> None:
    ensure_python_version()
    load_dotenv(PROJECT_DIR / ".env")

    port = os.environ.get("PORT", "8000")

    uv_path = shutil.which("uv")
    if uv_path:
        code = run_with_uv(port)
        sys.exit(code)

    # Fallback: local venv + pip
    venv = create_venv()
    py = venv_python()
    ensure_deps_in_venv(py)
    code = run_with_venv(py, port)
    sys.exit(code)


if __name__ == "__main__":
    main()


