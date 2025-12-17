"""Dashboard page routes."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.dependencies import get_store
from app.data import DataStore

# Get BUILD_INFO
try:
    import sys
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from version import get_build_info
    BUILD_INFO = get_build_info()
except Exception:
    BUILD_INFO = {"version": "0.1.0", "build_number": 0, "version_string": "0.1.0"}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


def get_version() -> str:
    """Get application version."""
    return BUILD_INFO.get("version_string", os.getenv("APP_VERSION", settings.app_version))


def get_initial_metrics_html(store: DataStore) -> str:
    """Build initial metrics HTML for dashboard pages."""
    kpis = store.kpis()
    labels, values = store.latency_series()
    thr_labels, thr_values = store.throughput_series()
    prof_labels, prof_values = store.profit_series()
    heat = store.heatmap_matrix()
    return templates.env.get_template("partials/metrics.html").render(
        {
            "kpis": kpis,
            "latency_series": list(zip(labels, values)),
            "throughput_series": list(zip(thr_labels, thr_values)),
            "profit_series": list(zip(prof_labels, prof_values)),
            "heatmap": heat,
            "last_events": store.last_events(25),
        }
    )


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """IDE Dashboard - Unified interface. Default entry point."""
    version = get_version()
    sample_mode = getattr(request.app.state, "sample_mode", False)
    store = get_store(request)
    initial_metrics_html = get_initial_metrics_html(store)
    return templates.TemplateResponse(
        "ide-dashboard.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html, "version": version},
    )


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Home page with feature overview / start menu."""
    version = get_version()
    return templates.TemplateResponse("home.html", {"request": request, "version": version})


@router.get("/tv", response_class=HTMLResponse)
async def tv_dashboard(request: Request) -> HTMLResponse:
    """TV-style dashboard (original view)."""
    version = get_version()
    sample_mode = getattr(request.app.state, "sample_mode", False)
    store = get_store(request)
    initial_metrics_html = get_initial_metrics_html(store)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html, "last_events": store.last_events(25), "version": version},
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """New sidebar dashboard layout with Alpine.js."""
    sample_mode = getattr(request.app.state, "sample_mode", False)
    store = get_store(request)
    initial_metrics_html = get_initial_metrics_html(store)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html},
    )


@router.get("/explorer", response_class=HTMLResponse)
async def bot_explorer_page(request: Request) -> HTMLResponse:
    """Bot Explorer page - Etherscan meets stock research."""
    version = get_version()
    return templates.TemplateResponse("bot-explorer.html", {"request": request, "version": version})


@router.get("/logic-builder", response_class=HTMLResponse)
async def logic_builder_page(request: Request) -> HTMLResponse:
    """Visual conditional logic builder page."""
    version = get_version()
    return templates.TemplateResponse("logic-builder.html", {"request": request, "version": version})


@router.get("/chart-annotations", response_class=HTMLResponse)
async def chart_annotations_page(request: Request) -> HTMLResponse:
    """Chart annotations and event triggers page."""
    version = get_version()
    return templates.TemplateResponse("chart-annotations.html", {"request": request, "version": version})


@router.get("/bots", response_class=HTMLResponse)
async def bots_page(request: Request) -> HTMLResponse:
    """Bots management page."""
    version = get_version()
    return templates.TemplateResponse("bots.html", {"request": request, "version": version})


@router.get("/bots/{bot_id}", response_class=HTMLResponse)
async def bot_profile(request: Request, bot_id: str) -> HTMLResponse:
    """Individual bot profile page."""
    version = get_version()
    return templates.TemplateResponse("bot-profile.html", {"request": request, "bot_id": bot_id, "version": version})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request) -> HTMLResponse:
    """Settings page."""
    version = get_version()
    return templates.TemplateResponse("settings.html", {"request": request, "version": version})


@router.get("/downloads", response_class=HTMLResponse)
async def downloads_page(request: Request) -> HTMLResponse:
    """Downloads page for standalone applications."""
    version = get_version()
    return templates.TemplateResponse("downloads.html", {"request": request, "version": version})


@router.get("/report", response_class=HTMLResponse)
async def report(request: Request) -> HTMLResponse:
    """Daily report page."""
    store = get_store(request)
    summary = store.daily_summary()
    return templates.TemplateResponse("report.html", {"request": request, "summary": summary})


@router.get("/demo", response_class=HTMLResponse)
async def demo(request: Request) -> HTMLResponse:
    """Demo page."""
    sample_mode = getattr(request.app.state, "sample_mode", False)
    store = get_store(request)
    initial_metrics_html = get_initial_metrics_html(store)
    return templates.TemplateResponse(
        "demo.html",
        {"request": request, "sample_mode": sample_mode, "initial_metrics_html": initial_metrics_html},
    )


@router.get("/logs", response_class=HTMLResponse)
async def logs_viewer(request: Request) -> HTMLResponse:
    """Logs viewer page for displaying JSON log entries."""
    return templates.TemplateResponse("logs.html", {"request": request})


@router.get("/pointcloud", response_class=HTMLResponse)
async def pointcloud_viewer(request: Request) -> HTMLResponse:
    """Standalone 3D point cloud visualization page."""
    version = get_version()
    return templates.TemplateResponse("pointcloud.html", {"request": request, "version": version})


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    """About page with tech stack overview."""
    version = get_version()
    return templates.TemplateResponse("about.html", {"request": request, "version": version})

