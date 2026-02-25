"""
Vercel serverless entry-point for MaskGuard.

Limitations on Vercel:
  - WebSocket (live camera) not supported
  - Video processing limited by 60 s function timeout
  - Ephemeral filesystem (/tmp only)
"""

import os, sys
from pathlib import Path

# ── make sure the *maskguard* package root is on sys.path so that
#    "from app.xxx import yyy" works regardless of how Vercel resolves cwd.
_project_root = Path(__file__).resolve().parent.parent   # maskguard/
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Vercel expects the variable `app` (ASGI) to be defined at module level.
from app.main import app  # noqa: E402  (must come after path fix)
