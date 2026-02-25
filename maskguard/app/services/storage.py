import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
import aiofiles
from fastapi import UploadFile
from app.config import UPLOADS_DIR, OUTPUTS_DIR, CAPTURES_DIR, MAX_VIDEO_MB, MAX_IMAGE_MB

class StorageService:
    """Service for managing file uploads and storage."""
    
    @staticmethod
    def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
        """
        Generate a unique filename.
        
        Args:
            original_filename: Original file name
            prefix: Optional prefix
        
        Returns:
            Unique filename with timestamp and UUID
        """
        ext = Path(original_filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        return f"{timestamp}_{unique_id}{ext}"
    
    @staticmethod
    async def save_upload(
        file: UploadFile,
        directory: str,
        max_size_mb: Optional[int] = None
    ) -> str:
        """
        Save an uploaded file.
        
        Args:
            file: Uploaded file
            directory: Target directory
            max_size_mb: Maximum file size in MB
        
        Returns:
            Path to saved file
        
        Raises:
            ValueError: If file is too large
        """
        # Generate unique filename
        filename = StorageService.generate_unique_filename(file.filename)
        filepath = Path(directory) / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file with size check
        total_size = 0
        async with aiofiles.open(filepath, 'wb') as f:
            while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
                total_size += len(chunk)
                
                # Check size limit
                if max_size_mb and total_size > max_size_mb * 1024 * 1024:
                    # Delete partial file
                    await f.close()
                    filepath.unlink(missing_ok=True)
                    raise ValueError(f"File size exceeds {max_size_mb}MB limit")
                
                await f.write(chunk)
        
        return str(filepath)
    
    @staticmethod
    async def save_image_upload(file: UploadFile) -> str:
        """
        Save an uploaded image file.
        
        Args:
            file: Uploaded image file
        
        Returns:
            Path to saved file
        """
        return await StorageService.save_upload(
            file,
            UPLOADS_DIR,
            max_size_mb=MAX_IMAGE_MB
        )
    
    @staticmethod
    async def save_video_upload(file: UploadFile) -> str:
        """
        Save an uploaded video file.
        
        Args:
            file: Uploaded video file
        
        Returns:
            Path to saved file
        """
        return await StorageService.save_upload(
            file,
            UPLOADS_DIR,
            max_size_mb=MAX_VIDEO_MB
        )
    
    @staticmethod
    def get_output_path(filename: str, output_type: str = "output") -> str:
        """
        Generate path for output file.
        
        Args:
            filename: Base filename
            output_type: Type of output (output, capture)
        
        Returns:
            Full path to output file
        """
        if output_type == "capture":
            directory = CAPTURES_DIR
        else:
            directory = OUTPUTS_DIR
        
        filepath = Path(directory) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        return str(filepath)
    
    @staticmethod
    def save_snapshot(image_data, source_name: str) -> str:
        """
        Save a snapshot image for a violation.
        
        Args:
            image_data: Image data (numpy array)
            source_name: Source identifier
        
        Returns:
            Path to saved snapshot
        """
        import cv2
        
        filename = StorageService.generate_unique_filename(
            f"{source_name}.jpg",
            prefix="snapshot"
        )
        filepath = StorageService.get_output_path(filename, "capture")
        
        cv2.imwrite(filepath, image_data)
        
        return filepath
    
    @staticmethod
    def get_relative_path(absolute_path: str) -> str:
        """
        Convert absolute path to relative path for serving.
        
        Args:
            absolute_path: Absolute file path
        
        Returns:
            Relative path for web serving
        """
        path = Path(absolute_path)
        
        # Try to make relative to data directory
        try:
            rel_path = path.relative_to(Path.cwd() / "data")
            return f"/files/{rel_path}"
        except ValueError:
            # Fallback: return just the filename
            return f"/files/outputs/{path.name}"

# Global storage service instance
storage_service = StorageService()
