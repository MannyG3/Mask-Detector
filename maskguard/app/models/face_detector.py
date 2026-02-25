import cv2
import numpy as np
from typing import List, Tuple

# MediaPipe is optional — on Vercel we use a lightweight OpenCV cascade fallback
try:
    import mediapipe as mp
    _HAS_MEDIAPIPE = True
except ImportError:
    _HAS_MEDIAPIPE = False

class FaceDetector:
    """Face detector with MediaPipe (preferred) or OpenCV Haar cascade fallback."""

    def __init__(self, min_detection_confidence: float = 0.5):
        self._use_mediapipe = _HAS_MEDIAPIPE

        if self._use_mediapipe:
            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=min_detection_confidence,
            )
            print("✓ Face detector: MediaPipe")
        else:
            # Fallback: OpenCV Haar cascade (always available with opencv-python-headless)
            self._cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            print("ℹ Face detector: OpenCV Haar cascade (mediapipe not installed)")

    # ------------------------------------------------------------------ #
    def detect_faces(self, image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
        if image_bgr is None or image_bgr.size == 0:
            return []
        if self._use_mediapipe:
            return self._detect_mediapipe(image_bgr)
        return self._detect_cascade(image_bgr)

    # ---- MediaPipe path ------------------------------------------------ #
    def _detect_mediapipe(self, image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        h, w = image_bgr.shape[:2]
        results = self.detector.process(image_rgb)

        boxes: List[Tuple[int, int, int, int]] = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x1 = max(0, int(bbox.xmin * w))
                y1 = max(0, int(bbox.ymin * h))
                x2 = min(w, int((bbox.xmin + bbox.width) * w))
                y2 = min(h, int((bbox.ymin + bbox.height) * h))
                if x2 > x1 and y2 > y1:
                    boxes.append((x1, y1, x2, y2))
        return boxes

    # ---- OpenCV Haar cascade path -------------------------------------- #
    def _detect_cascade(self, image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        detections = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        boxes: List[Tuple[int, int, int, int]] = []
        for (x, y, w, h) in detections:
            boxes.append((x, y, x + w, y + h))
        return boxes

    def __del__(self):
        if self._use_mediapipe and hasattr(self, "detector"):
            self.detector.close()

# Global face detector instance
face_detector = FaceDetector()
