import cv2
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.face_detector import face_detector
from app.models.classifier import mask_classifier
from app.services.logger import event_logger
from app.services.storage import storage_service
from app.config import VIDEO_PROCESS_FPS, LABELS

class JobStatus:
    """Job status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoJob:
    """Represents a video processing job."""
    
    def __init__(self, job_id: str, input_path: str):
        self.job_id = job_id
        self.input_path = input_path
        self.output_path: Optional[str] = None
        self.status = JobStatus.PENDING
        self.progress = 0
        self.error: Optional[str] = None
        self.summary: Dict[str, Any] = {}
        self.detections_count = 0
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None

class JobManager:
    """
    Manages video processing jobs.
    
    Note: Jobs are stored in-memory and will be lost on server restart.
    This is acceptable for single-instance deployments on free tiers.
    """
    
    def __init__(self):
        self.jobs: Dict[str, VideoJob] = {}
    
    def create_job(self, input_path: str) -> str:
        """
        Create a new video processing job.
        
        Args:
            input_path: Path to input video file
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = VideoJob(job_id, input_path)
        self.jobs[job_id] = job
        return job_id
    
    def get_job(self, job_id: str) -> Optional[VideoJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID
        
        Returns:
            VideoJob or None if not found
        """
        return self.jobs.get(job_id)
    
    def update_progress(self, job_id: str, progress: int):
        """
        Update job progress.
        
        Args:
            job_id: Job ID
            progress: Progress percentage (0-100)
        """
        if job_id in self.jobs:
            self.jobs[job_id].progress = min(100, max(0, progress))
    
    def complete_job(
        self,
        job_id: str,
        output_path: str,
        summary: Dict[str, Any],
        detections_count: int
    ):
        """
        Mark job as completed.
        
        Args:
            job_id: Job ID
            output_path: Path to output video
            summary: Detection summary
            detections_count: Total number of detections
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.output_path = output_path
            job.summary = summary
            job.detections_count = detections_count
            job.completed_at = datetime.utcnow().isoformat()
    
    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed.
        
        Args:
            job_id: Job ID
            error: Error message
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = JobStatus.FAILED
            job.error = error
            job.completed_at = datetime.utcnow().isoformat()

# Global job manager
job_manager = JobManager()

def process_video(job_id: str):
    """
    Process a video file for mask detection.
    
    This function runs in the background and processes the video frame by frame.
    
    Args:
        job_id: Job ID to process
    """
    job = job_manager.get_job(job_id)
    if not job:
        return
    
    try:
        job.status = JobStatus.PROCESSING
        
        # Open input video
        cap = cv2.VideoCapture(job.input_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps <= 0:
            fps = VIDEO_PROCESS_FPS

        if total_frames <= 0:
            total_frames = 1
        
        # Calculate frame sampling rate
        frame_skip = max(1, int(fps / VIDEO_PROCESS_FPS))
        
        # Generate output path
        output_filename = storage_service.generate_unique_filename(
            Path(job.input_path).name,
            prefix="annotated"
        )
        output_path = storage_service.get_output_path(output_filename, "output")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, VIDEO_PROCESS_FPS, (width, height))
        
        # Detection statistics
        label_counts = {label: 0 for label in LABELS}
        total_detections = 0
        
        frame_idx = 0
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every Nth frame
            if frame_idx % frame_skip == 0:
                # Detect faces
                boxes = face_detector.detect_faces(frame)
                
                # Classify each face and draw results
                for box in boxes:
                    x1, y1, x2, y2 = box
                    
                    # Extract face
                    face = frame[y1:y2, x1:x2]
                    if face.size == 0:
                        continue
                    
                    # Classify
                    label, confidence = mask_classifier.predict(face)
                    
                    # Update statistics
                    label_counts[label] += 1
                    total_detections += 1
                    
                    # Log event
                    event_logger.log_detection(
                        source="video",
                        label=label,
                        confidence=confidence,
                        meta={
                            "frame": frame_idx,
                            "box": [int(x1), int(y1), int(x2), int(y2)]
                        }
                    )
                    
                    # Draw box and label
                    color = (0, 255, 0) if label == "MASK_ON" else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label background
                    label_text = f"{label}: {confidence:.2f}"
                    (text_w, text_h), _ = cv2.getTextSize(
                        label_text,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        2
                    )
                    cv2.rectangle(
                        frame,
                        (x1, y1 - text_h - 10),
                        (x1 + text_w, y1),
                        color,
                        -1
                    )
                    cv2.putText(
                        frame,
                        label_text,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2
                    )
                
                # Write annotated frame
                out.write(frame)
                processed_frames += 1
                
                # Update progress
                progress = int((frame_idx / total_frames) * 100)
                job_manager.update_progress(job_id, progress)
            
            frame_idx += 1
        
        # Release resources
        cap.release()
        out.release()
        
        # Prepare summary
        summary = {
            "total_frames": total_frames,
            "processed_frames": processed_frames,
            "total_detections": total_detections,
            "label_counts": label_counts
        }
        
        # Complete job
        job_manager.complete_job(job_id, output_path, summary, total_detections)
        
    except Exception as e:
        error_msg = f"Video processing error: {str(e)}"
        print(error_msg)
        job_manager.fail_job(job_id, error_msg)
