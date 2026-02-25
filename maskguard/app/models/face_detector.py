import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple

class FaceDetector:
    """Face detector using MediaPipe Face Detection."""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        """
        Initialize MediaPipe Face Detector.
        
        Args:
            min_detection_confidence: Minimum confidence for detection
        """
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0 for short-range (< 2m), 1 for full-range
            min_detection_confidence=min_detection_confidence
        )
    
    def detect_faces(self, image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.
        
        Args:
            image_bgr: Image in BGR format (OpenCV default)
        
        Returns:
            List of bounding boxes as (x1, y1, x2, y2)
        """
        if image_bgr is None or image_bgr.size == 0:
            return []
        
        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        h, w = image_bgr.shape[:2]
        
        # Detect faces
        results = self.detector.process(image_rgb)
        
        boxes = []
        if results.detections:
            for detection in results.detections:
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                
                # Convert to absolute coordinates
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)
                
                # Clip to image boundaries
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                
                # Only add if box is valid
                if x2 > x1 and y2 > y1:
                    boxes.append((x1, y1, x2, y2))
        
        return boxes
    
    def __del__(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'detector'):
            self.detector.close()

# Global face detector instance
face_detector = FaceDetector()
