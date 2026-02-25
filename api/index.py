"""
Vercel serverless entry-point for MaskGuard.

Limitations on Vercel:
  - WebSocket (live camera) not supported
  - Video processing limited by 60 s function timeout
  - Ephemeral filesystem (/tmp only)
"""

import sys
from pathlib import Path

# Add the maskguard package root to sys.path so "from app.xxx" works.
_maskguard_root = Path(__file__).resolve().parent.parent / "maskguard"
if str(_maskguard_root) not in sys.path:
    sys.path.insert(0, str(_maskguard_root))

# Vercel expects the variable `app` (ASGI callable) at module level.
from app.main import app  # noqa: E402
