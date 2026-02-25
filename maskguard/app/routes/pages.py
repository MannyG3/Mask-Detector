from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.db import query_events, get_stats_summary
from app.config import (
    ALERT_COOLDOWN_SECONDS,
    SNAPSHOTS_ENABLED,
    LIVE_FPS_CAP,
    LABELS
)

router = APIRouter()

# Setup Jinja2 templates
templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page": "home"
    })

@router.get("/live", response_class=HTMLResponse)
async def live_page(request: Request):
    """Live webcam detection page."""
    return templates.TemplateResponse("live.html", {
        "request": request,
        "page": "live",
        "default_fps": LIVE_FPS_CAP,
        "default_cooldown": ALERT_COOLDOWN_SECONDS,
        "snapshots_enabled": SNAPSHOTS_ENABLED
    })

@router.get("/upload/image", response_class=HTMLResponse)
async def upload_image_page(request: Request):
    """Image upload page."""
    return templates.TemplateResponse("upload_image.html", {
        "request": request,
        "page": "upload_image"
    })

@router.get("/upload/video", response_class=HTMLResponse)
async def upload_video_page(request: Request):
    """Video upload page."""
    return templates.TemplateResponse("upload_video.html", {
        "request": request,
        "page": "upload_video"
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page with logs and statistics."""
    # Get filter parameters
    params = request.query_params
    filter_source = params.get("source") or None
    filter_label = params.get("label") or None
    filter_start_date = params.get("start_date") or None
    filter_end_date = params.get("end_date") or None

    # Get recent logs with filters
    logs = query_events(
        source=filter_source,
        label=filter_label,
        start_date=filter_start_date,
        end_date=filter_end_date,
        limit=100
    )
    
    # Get statistics (date range only)
    stats = get_stats_summary(
        start_date=filter_start_date,
        end_date=filter_end_date
    )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "page": "dashboard",
        "logs": logs,
        "stats": stats,
        "labels": LABELS,
        "filter_source": filter_source,
        "filter_label": filter_label,
        "filter_start_date": filter_start_date,
        "filter_end_date": filter_end_date
    })
