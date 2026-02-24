"""
Configuration management for the nutrition and wellness tracking system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/user_data/nutrition_wellness.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Food Recognition Model
FOOD_MODEL_NAME = "nateraw/food"  # Pre-trained Food-101 model from HuggingFace
FOOD_MODEL_PATH = BASE_DIR / "data" / "models" / "food_recognition"

# Conversational AI Model (Dynamic)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "microsoft/DialoGPT-medium")


# Nutrition API
USDA_API_KEY = os.getenv("USDA_API_KEY", "")  # Optional: Get from https://fdc.nal.usda.gov/api-key-signup.html
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"

# File Upload
UPLOAD_DIR = BASE_DIR / "data" / "user_data" / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
FOOD_MODEL_PATH.mkdir(parents=True, exist_ok=True)
