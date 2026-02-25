import cv2
import numpy as np
import os
from pathlib import Path
from typing import Tuple
from app.config import DUMMY_MODEL, MODEL_PATH, LABELS

class MaskClassifier:
    """Mask classification model with dummy mode support."""
    
    def __init__(self):
        """Initialize the classifier."""
        self.model = None
        self.dummy_mode = DUMMY_MODEL
        self.labels = LABELS
        
        # Try to load real model if not in dummy mode
        if not self.dummy_mode:
            model_path = Path(MODEL_PATH)
            if model_path.exists():
                try:
                    import tensorflow as tf
                    self.model = tf.keras.models.load_model(str(model_path))
                    print(f"✓ Loaded model from {model_path}")
                except Exception as e:
                    print(f"⚠ Failed to load model: {e}")
                    print("⚠ Falling back to dummy mode")
                    self.dummy_mode = True
            else:
                print(f"⚠ Model file not found at {model_path}")
                print("⚠ Running in dummy mode")
                self.dummy_mode = True
        else:
            print("ℹ Running in DUMMY_MODEL mode (simulated predictions)")
    
    def preprocess_face(self, face_bgr: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for model input.
        
        Args:
            face_bgr: Face image in BGR format
        
        Returns:
            Preprocessed image ready for model
        """
        # Resize to model input size
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, (224, 224))
        
        # Normalize to [0, 1]
        face_normalized = face_resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        face_batch = np.expand_dims(face_normalized, axis=0)
        
        return face_batch
    
    def predict(self, face_bgr: np.ndarray) -> Tuple[str, float]:
        """
        Predict mask status for a face.
        
        Args:
            face_bgr: Face image in BGR format
        
        Returns:
            Tuple of (label, confidence)
        """
        if face_bgr is None or face_bgr.size == 0:
            return "MASK_ON", 0.0
        
        if self.dummy_mode or self.model is None:
            return self._dummy_predict(face_bgr)
        
        try:
            # Preprocess
            face_input = self.preprocess_face(face_bgr)
            
            # Predict
            predictions = self.model.predict(face_input, verbose=0)[0]
            
            # Handle different output formats
            if len(predictions) == 1:
                # Binary output (sigmoid): 0 = NO_MASK, 1 = MASK_ON
                # For MASK_INCORRECT, use simple heuristic
                confidence = float(predictions[0])
                
                if confidence > 0.7:
                    label = "MASK_ON"
                elif confidence < 0.3:
                    label = "NO_MASK"
                else:
                    # Middle range could be incorrect mask
                    label = "MASK_INCORRECT"
            else:
                # Multi-class output (softmax): [MASK_ON, NO_MASK, MASK_INCORRECT]
                idx = int(np.argmax(predictions))
                confidence = float(predictions[idx])
                label = self.labels[idx] if idx < len(self.labels) else "MASK_ON"
            
            return label, confidence
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._dummy_predict(face_bgr)
    
    def _dummy_predict(self, face_bgr: np.ndarray) -> Tuple[str, float]:
        """
        Generate stable dummy predictions for testing.
        
        Uses mean pixel intensity to generate deterministic predictions
        so results are stable across frames.
        
        Args:
            face_bgr: Face image in BGR format
        
        Returns:
            Tuple of (label, confidence)
        """
        # Use mean intensity to generate stable predictions
        mean_intensity = np.mean(face_bgr)
        
        # Map intensity ranges to different labels (deterministic)
        if mean_intensity < 80:
            label = "NO_MASK"
            confidence = 0.85 + (80 - mean_intensity) / 800
        elif mean_intensity < 120:
            label = "MASK_INCORRECT"
            confidence = 0.75 + (mean_intensity - 80) / 400
        else:
            label = "MASK_ON"
            confidence = 0.88 + (mean_intensity - 120) / 1350
        
        # Clamp confidence to valid range
        confidence = float(np.clip(confidence, 0.0, 1.0))
        
        return label, confidence

# Global classifier instance
mask_classifier = MaskClassifier()
