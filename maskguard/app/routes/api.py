import cv2
import io
import csv
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from datetime import datetime
from app.models.face_detector import face_detector
from app.models.classifier import mask_classifier
from app.services.logger import event_logger
from app.services.storage import storage_service
from app.services.video_worker import job_manager, process_video
from app.db import query_events, get_stats_summary
from app.config import LABELS, SNAPSHOTS_ENABLED, VIOLATION_LABELS

router = APIRouter(prefix="/api")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Detect masks in an uploaded image.
    
    Returns annotated image and detection results.
    """
    try:
        # Save upload
        input_path = await storage_service.save_image_upload(file)
        
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Detect faces
        boxes = face_detector.detect_faces(image)
        
        # Process detections
        detections = []
        label_counts = {label: 0 for label in LABELS}
        
        for box in boxes:
            x1, y1, x2, y2 = box
            
            # Extract face
            face = image[y1:y2, x1:x2]
            if face.size == 0:
                continue
            
            # Classify
            label, confidence = mask_classifier.predict(face)
            
            # Update counts
            label_counts[label] += 1
            
            # Save snapshot for violations if enabled
            snapshot_path = None
            if SNAPSHOTS_ENABLED and label in VIOLATION_LABELS:
                try:
                    snapshot_path = storage_service.save_snapshot(
                        face,
                        f"image_{Path(file.filename).stem}"
                    )
                except Exception as e:
                    print(f"Snapshot save error: {e}")

            # Log event
            event_logger.log_detection(
                source="image",
                label=label,
                confidence=confidence,
                snapshot_path=snapshot_path,
                meta={"box": [int(x1), int(y1), int(x2), int(y2)]}
            )
            
            # Store detection
            detections.append({
                "box": [int(x1), int(y1), int(x2), int(y2)],
                "label": label,
                "confidence": float(confidence)
            })
            
            # Draw on image
            color = (0, 255, 0) if label == "MASK_ON" else (0, 0, 255)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label_text = f"{label}: {confidence:.2f}"
            (text_w, text_h), _ = cv2.getTextSize(
                label_text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                2
            )
            cv2.rectangle(
                image,
                (x1, y1 - text_h - 10),
                (x1 + text_w, y1),
                color,
                -1
            )
            cv2.putText(
                image,
                label_text,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        # Save annotated image
        output_filename = storage_service.generate_unique_filename(
            file.filename,
            prefix="annotated"
        )
        output_path = storage_service.get_output_path(output_filename, "output")
        cv2.imwrite(output_path, image)
        
        # Get relative path for serving
        output_url = storage_service.get_relative_path(output_path)
        
        return {
            "success": True,
            "annotated_image_url": output_url,
            "detections": detections,
            "summary": {
                "total_faces": len(boxes),
                "label_counts": label_counts
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/video")
async def create_video_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Create a video processing job.
    
    Returns job ID for status polling.
    """
    try:
        # Save upload
        input_path = await storage_service.save_video_upload(file)
        
        # Create job
        job_id = job_manager.create_job(input_path)
        
        # Schedule background processing
        background_tasks.add_task(process_video, job_id)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Video processing job created"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/video/{job_id}")
async def get_video_job_status(job_id: str):
    """
    Get status of a video processing job.
    
    Returns job status, progress, and results when completed.
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "created_at": job.created_at
    }
    
    if job.status == "completed":
        response["completed_at"] = job.completed_at
        response["output_video_url"] = storage_service.get_relative_path(job.output_path)
        response["summary"] = job.summary
        response["detections_count"] = job.detections_count
    elif job.status == "failed":
        response["error"] = job.error
    
    return response

@router.get("/logs/export.csv")
async def export_logs(
    source: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Export logs as CSV.
    
    Supports filtering by source, label, and date range.
    """
    try:
        # Query events
        events = query_events(
            source=source,
            label=label,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID",
            "Timestamp",
            "Source",
            "Label",
            "Confidence",
            "Track ID",
            "Snapshot Path"
        ])
        
        # Write data
        for event in events:
            writer.writerow([
                event['id'],
                event['ts'],
                event['source'],
                event['label'],
                f"{event['confidence']:.4f}",
                event['track_id'] or '',
                event['snapshot_path'] or ''
            ])
        
        # Prepare response
        output.seek(0)
        filename = f"maskguard_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get summary statistics."""
    try:
        stats = get_stats_summary(start_date=start_date, end_date=end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
