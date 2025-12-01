"""
Download endpoints for standalone applications.
Handles file downloads with proper headers and error handling.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
import os

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"


def get_download_file(platform: str, filename: str) -> Path:
    """Get the full path to a download file."""
    if platform == "windows":
        file_path = DOWNLOADS_DIR / "windows" / filename
    elif platform == "macos":
        file_path = DOWNLOADS_DIR / "macos" / filename
    elif platform == "linux":
        file_path = DOWNLOADS_DIR / "linux" / filename
    else:
        # Direct downloads folder
        file_path = DOWNLOADS_DIR / filename
    
    return file_path


@router.get("/downloads/{platform}/{filename}")
async def download_file(platform: str, filename: str, request: Request):
    """Download a file from the downloads directory."""
    file_path = get_download_file(platform, filename)
    
    if not file_path.exists():
        # Try alternative locations
        alt_path = DOWNLOADS_DIR / filename
        if alt_path.exists():
            file_path = alt_path
        else:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}. The file may not have been built yet."
            )
    
    # Determine media type
    media_type = "application/octet-stream"
    if filename.endswith(".zip"):
        media_type = "application/zip"
    elif filename.endswith(".exe"):
        media_type = "application/x-msdownload"
    elif filename.endswith(".dmg"):
        media_type = "application/x-apple-diskimage"
    elif filename.endswith(".AppImage"):
        media_type = "application/x-executable"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        }
    )


@router.get("/downloads/{filename}")
async def download_file_direct(filename: str, request: Request):
    """Download a file directly from downloads directory."""
    file_path = DOWNLOADS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}. The file may not have been built yet."
        )
    
    # Determine media type
    media_type = "application/octet-stream"
    if filename.endswith(".zip"):
        media_type = "application/zip"
    elif filename.endswith(".exe"):
        media_type = "application/x-msdownload"
    elif filename.endswith(".dmg"):
        media_type = "application/x-apple-diskimage"
    elif filename.endswith(".AppImage"):
        media_type = "application/x-executable"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        }
    )


