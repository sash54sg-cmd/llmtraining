"""
Audio handling: saving audio uploads and transcribing with Whisper.
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
import logging
import torch

from typing import Optional

try:
    import whisper
except Exception:
    whisper = None

from src.config.config import UPLOAD_DIR, MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)


class AudioHandler:
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_audio(self, file_content: bytes, filename: str, user_id: int) -> str:
        """Save uploaded audio bytes to disk and return path."""
        if len(file_content) > MAX_UPLOAD_SIZE:
            raise ValueError("Audio file too large")

        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(filename).suffix.lower() or '.wav'
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{suffix}"
        file_path = user_dir / unique_name

        with open(file_path, 'wb') as f:
            f.write(file_content)

        logger.info(f"Saved audio: {file_path}")
        return str(file_path)

    def transcribe(self, audio_path: str, model_size: str = "small") -> str:
        """Transcribe audio using Whisper if available. Returns transcription text."""
        if whisper is None:
            logger.warning("whisper package not available; returning empty transcription")
            return ""

        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            model = whisper.load_model(model_size, device=device)
            result = model.transcribe(audio_path)
            return result.get('text', '').strip()
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""


# Global instance
_audio_handler = None

def get_audio_handler() -> AudioHandler:
    global _audio_handler
    if _audio_handler is None:
        _audio_handler = AudioHandler()
    return _audio_handler
