"""
Food recognition using pre-trained Food-101 model.
"""
import torch
import torchvision.transforms as transforms
from PIL import Image
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from src.config.config import FOOD_MODEL_NAME, FOOD_MODEL_PATH

logger = logging.getLogger(__name__)


class FoodRecognitionModel:
    """Food recognition using pre-trained Food-101 model."""
    
    def __init__(self):
        """Initialize the food recognition model."""
        self.model = None
        self.feature_extractor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the pre-trained Food-101 model."""
        try:
            logger.info(f"Loading food recognition model: {FOOD_MODEL_NAME}")
            
            # Load feature extractor and model
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(
                FOOD_MODEL_NAME,
                cache_dir=FOOD_MODEL_PATH
            )
            self.model = AutoModelForImageClassification.from_pretrained(
                FOOD_MODEL_NAME,
                cache_dir=FOOD_MODEL_PATH
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Food recognition model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading food recognition model: {e}")
            raise
    
    def predict(self, image_path: str, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Predict food items from an image.
        
        Args:
            image_path: Path to the image file
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions with food names and confidence scores
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Extract features
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top-k predictions
            top_probs, top_indices = torch.topk(probabilities[0], top_k)
            
            predictions = []
            for prob, idx in zip(top_probs, top_indices):
                food_name = self.model.config.id2label[idx.item()]
                # Clean up food name (remove underscores, capitalize)
                food_name = food_name.replace('_', ' ').title()
                
                predictions.append({
                    'food_name': food_name,
                    'confidence': float(prob.item()),
                    'confidence_percent': round(float(prob.item()) * 100, 2)
                })
            
            logger.info(f"Predicted food: {predictions[0]['food_name']} "
                       f"(confidence: {predictions[0]['confidence_percent']}%)")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting food from image: {e}")
            raise
    
    def estimate_portion_size(self, image_path: str) -> Dict[str, any]:
        """
        Estimate portion size from image.
        This is a simplified version - in production, you'd use depth estimation
        or reference object detection.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with portion size estimate
        """
        try:
            image = Image.open(image_path)
            width, height = image.size
            
            # Simple heuristic based on image size and food coverage
            # In production, use more sophisticated methods
            area = width * height
            
            # Estimate portion as small/medium/large based on image analysis
            # This is a placeholder - real implementation would use object detection
            if area < 500000:
                portion = "small"
                multiplier = 0.75
            elif area < 1000000:
                portion = "medium"
                multiplier = 1.0
            else:
                portion = "large"
                multiplier = 1.5
            
            return {
                'portion_size': portion,
                'portion_multiplier': multiplier,
                'confidence': 0.6,  # Lower confidence for simple estimation
                'method': 'heuristic'
            }
            
        except Exception as e:
            logger.error(f"Error estimating portion size: {e}")
            return {
                'portion_size': 'medium',
                'portion_multiplier': 1.0,
                'confidence': 0.5,
                'method': 'default'
            }


# Global model instance
_food_model = None

def get_food_model() -> FoodRecognitionModel:
    """Get or create the global food recognition model instance."""
    global _food_model
    if _food_model is None:
        _food_model = FoodRecognitionModel()
    return _food_model
