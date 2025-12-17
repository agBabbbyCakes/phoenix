"""Health check and system endpoints."""
from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


@router.get("/healthz")
def healthz():
    """Kubernetes health check endpoint."""
    return {"ok": True}


@router.get("/version")
def version():
    """Get application version."""
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).resolve().parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from version import get_build_info
        BUILD_INFO = get_build_info()
        return {"version": BUILD_INFO.get("version_string", os.getenv("APP_VERSION", "0.1.0"))}
    except Exception:
        return {"version": os.getenv("APP_VERSION", "0.1.0")}

