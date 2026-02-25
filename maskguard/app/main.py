from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes import api, pages, ws
from app.db import init_db
from app.config import PORT

# Create FastAPI app
app = FastAPI(
    title="MaskGuard",
    description="Advanced mask detection system with live monitoring",
    version="1.0.0"
)

# Include routers
app.include_router(api.router, tags=["API"])
app.include_router(ws.router, tags=["WebSocket"])
app.include_router(pages.router, tags=["Pages"])

# Mount static files
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount data files for serving outputs — only when the directory exists
# (on Vercel the data dir lives under /tmp and may not exist yet)
data_dir = Path(__file__).resolve().parent.parent / "data"
if data_dir.is_dir():
    app.mount("/files", StaticFiles(directory=str(data_dir)), name="files")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting MaskGuard application...")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Import models to ensure they're loaded
    from app.models.face_detector import face_detector
    from app.models.classifier import mask_classifier
    print("✓ Models loaded")
    
    print(f"✓ Server ready on port {PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down MaskGuard application...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True
    )
