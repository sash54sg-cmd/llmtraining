"""
Image handling for food photos - camera capture and gallery upload.
"""
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import Image
import logging
from src.config.config import UPLOAD_DIR, MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handle image uploads and storage."""
    
    def __init__(self):
        """Initialize image handler."""
        self.upload_dir = UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_image(self, file_content: bytes, filename: str, user_id: int) -> str:
        """
        Save uploaded image file.
        
        Args:
            file_content: Image file content as bytes
            filename: Original filename
            user_id: User ID for organizing uploads
            
        Returns:
            Path to saved image
        """
        try:
            # Check file size
            if len(file_content) > MAX_UPLOAD_SIZE:
                raise ValueError(f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE / 1024 / 1024}MB")
            
            # Create user directory
            user_dir = self.upload_dir / str(user_id)
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_ext = Path(filename).suffix.lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                file_ext = '.jpg'
            
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = user_dir / unique_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Validate and optimize image
            self._optimize_image(file_path)
            
            logger.info(f"Saved image: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving uploaded image: {e}")
            raise
    
    def _optimize_image(self, image_path: str) -> None:
        """
        Optimize image size and format.
        
        Args:
            image_path: Path to image file
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large (max 1920x1920)
            max_size = 1920
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"Optimized image: {image_path}")
            
        except Exception as e:
            logger.warning(f"Error optimizing image: {e}")
    
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if deleted successfully
        """
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted image: {image_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get image information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image info
        """
        try:
            img = Image.open(image_path)
            file_size = os.path.getsize(image_path)
            
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': file_size,
                'size_mb': round(file_size / 1024 / 1024, 2)
            }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {}


# Global image handler instance
_image_handler = None

def get_image_handler() -> ImageHandler:
    """Get or create the global image handler instance."""
    global _image_handler
    if _image_handler is None:
        _image_handler = ImageHandler()
    return _image_handler
