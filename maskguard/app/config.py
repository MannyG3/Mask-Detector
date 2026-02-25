import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Model configuration
DUMMY_MODEL = os.getenv("DUMMY_MODEL", "true").lower() == "true"
MODEL_PATH = os.getenv("MODEL_PATH", "models/mask_detection_model.h5")

# Alert configuration
ALERT_COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN_SECONDS", "10"))
SNAPSHOTS_ENABLED = os.getenv("SNAPSHOTS_ENABLED", "false").lower() == "true"
SOUND_ALERTS_ENABLED = os.getenv("SOUND_ALERTS_ENABLED", "true").lower() == "true"

# Upload limits (in MB)
MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "50"))
MAX_IMAGE_MB = int(os.getenv("MAX_IMAGE_MB", "10"))

# Performance
LIVE_FPS_CAP = int(os.getenv("LIVE_FPS_CAP", "5"))
VIDEO_PROCESS_FPS = int(os.getenv("VIDEO_PROCESS_FPS", "5"))

# Storage paths
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "logs" / "events.db"))
UPLOADS_DIR = os.getenv("UPLOADS_DIR", str(DATA_DIR / "uploads"))
OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", str(DATA_DIR / "outputs"))
CAPTURES_DIR = os.getenv("CAPTURES_DIR", str(DATA_DIR / "captures"))

# Server
PORT = int(os.getenv("PORT", "8000"))

# Ensure directories exist (may fail on read-only FS; /tmp dirs work on Vercel)
for directory in [DB_PATH, UPLOADS_DIR, OUTPUTS_DIR, CAPTURES_DIR]:
    try:
        Path(directory).parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

for d in [UPLOADS_DIR, OUTPUTS_DIR, CAPTURES_DIR]:
    try:
        Path(d).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

# Labels
LABELS = ["MASK_ON", "NO_MASK", "MASK_INCORRECT"]
VIOLATION_LABELS = ["NO_MASK", "MASK_INCORRECT"]
