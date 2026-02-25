import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.db import log_event as db_log_event
from app.config import ALERT_COOLDOWN_SECONDS, VIOLATION_LABELS

class EventLogger:
    """Service for logging detection events with cooldown management."""
    
    def __init__(self):
        # Track last alert time per track_id for live stream
        self._last_alert_time: Dict[str, float] = {}
        self.cooldown_seconds = ALERT_COOLDOWN_SECONDS
    
    def should_alert(self, track_id: str) -> bool:
        """
        Check if enough time has passed since last alert for this track.
        
        Args:
            track_id: Unique identifier for the tracked face
        
        Returns:
            True if alert should be triggered, False if in cooldown
        """
        current_time = time.time()
        last_time = self._last_alert_time.get(track_id, 0)
        
        if current_time - last_time >= self.cooldown_seconds:
            self._last_alert_time[track_id] = current_time
            return True
        
        return False
    
    def log_detection(
        self,
        source: str,
        label: str,
        confidence: float,
        track_id: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        meta: Optional[Dict] = None,
        force_log: bool = False
    ) -> tuple[int, bool]:
        """
        Log a detection event.
        
        For live detections with track_id, applies cooldown logic.
        For uploads (image/video), always logs.
        
        Args:
            source: Event source (live, image, video)
            label: Detection label
            confidence: Prediction confidence
            track_id: Optional track ID (for live)
            snapshot_path: Optional snapshot path
            meta: Optional metadata
            force_log: Force logging even during cooldown
        
        Returns:
            Tuple of (event_id, should_alert)
        """
        should_alert = False
        
        # For live detections with violations, check cooldown
        if source == "live" and track_id and label in VIOLATION_LABELS:
            if force_log or self.should_alert(track_id):
                should_alert = True
                event_id = db_log_event(
                    source=source,
                    label=label,
                    confidence=confidence,
                    track_id=track_id,
                    snapshot_path=snapshot_path,
                    meta=meta
                )
            else:
                # During cooldown, don't log
                event_id = -1
        else:
            # Always log for image/video uploads or MASK_ON detections
            event_id = db_log_event(
                source=source,
                label=label,
                confidence=confidence,
                track_id=track_id,
                snapshot_path=snapshot_path,
                meta=meta
            )
            
            # Alert for violations in uploads
            if label in VIOLATION_LABELS:
                should_alert = True
        
        return event_id, should_alert

    def set_cooldown(self, seconds: int):
        """Update cooldown seconds for live alerts."""
        try:
            self.cooldown_seconds = max(1, int(seconds))
        except (TypeError, ValueError):
            pass
    
    def reset_cooldowns(self):
        """Reset all cooldown timers (useful for testing or when stopping live stream)."""
        self._last_alert_time.clear()

# Global logger instance
event_logger = EventLogger()
