import cv2
import numpy as np
import base64
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from app.models.face_detector import face_detector
from app.models.classifier import mask_classifier
from app.models.tracker import centroid_tracker
from app.services.logger import event_logger
from app.services.storage import storage_service
from app.config import SNAPSHOTS_ENABLED, VIOLATION_LABELS

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for live detection."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

manager = ConnectionManager()

@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """
    WebSocket endpoint for live webcam mask detection.
    
    Receives frames from client, performs detection, and returns results.
    """
    client_id = f"client_{id(websocket)}"
    await manager.connect(websocket, client_id)
    
    frame_id = 0
    snapshots_enabled = SNAPSHOTS_ENABLED
    
    try:
        while True:
            # Receive frame data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "config":
                snapshots_enabled = bool(message.get("snapshots_enabled", snapshots_enabled))
                cooldown_seconds = message.get("cooldown_seconds")
                if cooldown_seconds is not None:
                    event_logger.set_cooldown(cooldown_seconds)

                await websocket.send_json({
                    "type": "config_ack",
                    "snapshots_enabled": snapshots_enabled,
                    "cooldown_seconds": event_logger.cooldown_seconds
                })
                continue

            if message.get("type") == "frame":
                # Decode frame data
                frame_data = message.get("data", "")
                
                # Remove data URL prefix if present
                if "," in frame_data:
                    frame_data = frame_data.split(",", 1)[1]
                
                # Decode base64 to image
                try:
                    img_bytes = base64.b64decode(frame_data)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        continue
                    
                except Exception as e:
                    print(f"Frame decode error: {e}")
                    continue
                
                # Detect faces
                boxes = face_detector.detect_faces(frame)
                
                # Update tracker to get stable IDs
                tracked = centroid_tracker.update(boxes)
                
                # Process each tracked face
                detections = []
                has_alerts = False
                
                for track_id, box in tracked:
                    x1, y1, x2, y2 = box
                    
                    # Extract face
                    face = frame[y1:y2, x1:x2]
                    if face.size == 0:
                        continue
                    
                    # Classify
                    label, confidence = mask_classifier.predict(face)
                    
                    # Check if violation and should alert
                    should_alert = False
                    snapshot_path = None
                    track_id_str = f"track_{track_id}"

                    if label in VIOLATION_LABELS:
                        # Check cooldown before logging
                        if event_logger.should_alert(track_id_str):
                            # Save snapshot if enabled
                            if snapshots_enabled:
                                try:
                                    snapshot_path = storage_service.save_snapshot(
                                        face,
                                        f"live_track_{track_id}"
                                    )
                                except Exception as e:
                                    print(f"Snapshot save error: {e}")

                            # Log with snapshot if available
                            event_logger.log_detection(
                                source="live",
                                label=label,
                                confidence=confidence,
                                track_id=track_id_str,
                                snapshot_path=snapshot_path,
                                force_log=True
                            )
                            should_alert = True
                            has_alerts = True
                    else:
                        # Log non-violation detections
                        event_logger.log_detection(
                            source="live",
                            label=label,
                            confidence=confidence,
                            track_id=track_id_str
                        )
                    
                    # Add detection to results
                    detections.append({
                        "track_id": f"track_{track_id}",
                        "box": [int(x1), int(y1), int(x2), int(y2)],
                        "label": label,
                        "confidence": float(confidence),
                        "alert": should_alert
                    })
                
                # Send results back to client
                response = {
                    "frame_id": frame_id,
                    "detections": detections,
                    "alert": has_alerts,
                    "faces_count": len(tracked)
                }
                
                await websocket.send_json(response)
                frame_id += 1
            
            elif message.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # Reset tracker for this client
        centroid_tracker.objects.clear()
        centroid_tracker.disappeared.clear()
        event_logger.reset_cooldowns()
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)
