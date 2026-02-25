"""
Vercel serverless handler for MaskGuard
Note: This deployment has limitations - WebSocket and video processing disabled
"""

from app.main import app

# Vercel expects 'app' or 'application' to be exported
handler = app
