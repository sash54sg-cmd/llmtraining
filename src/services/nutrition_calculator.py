"""
Nutrition calculation and database lookup.
"""
import requests
import logging
from typing import Dict, Optional
from src.config.config import USDA_API_KEY, USDA_API_URL

logger = logging.getLogger(__name__)


# Comprehensive nutrition database for common foods (per 100g)
# This is a fallback when USDA API is not available
NUTRITION_DATABASE = {
    # Proteins
    'chicken breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0, 'sugar': 0, 'sodium': 74},
    'salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'sugar': 0, 'sodium': 59},
    'eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'fiber': 0, 'sugar': 1.1, 'sodium': 124},
    'beef': {'calories': 250, 'protein': 26, 'carbs': 0, 'fat': 15, 'fiber': 0, 'sugar': 0, 'sodium': 72},
    'tofu': {'calories': 76, 'protein': 8, 'carbs': 1.9, 'fat': 4.8, 'fiber': 0.3, 'sugar': 0.7, 'sodium': 7},
    
    # Carbs
    'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4, 'sugar': 0.1, 'sodium': 1},
    'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1, 'fiber': 1.8, 'sugar': 0.6, 'sodium': 6},
    'bread': {'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2, 'fiber': 2.7, 'sugar': 5, 'sodium': 491},
    'potato': {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.1, 'sugar': 0.8, 'sodium': 6},
    'oatmeal': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4, 'fiber': 1.7, 'sugar': 0.5, 'sodium': 49},
    
    # Fruits
    'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4, 'sugar': 10, 'sodium': 1},
    'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'fiber': 2.6, 'sugar': 12, 'sodium': 1},
    'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1, 'fiber': 2.4, 'sugar': 9, 'sodium': 0},
    'strawberry': {'calories': 32, 'protein': 0.7, 'carbs': 7.7, 'fat': 0.3, 'fiber': 2, 'sugar': 4.9, 'sodium': 1},
    
    # Vegetables
    'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'sugar': 1.7, 'sodium': 33},
    'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'fiber': 2.2, 'sugar': 0.4, 'sodium': 79},
    'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'sugar': 4.7, 'sodium': 69},
    'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2, 'sugar': 2.6, 'sodium': 5},
    
    # Prepared foods
    'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2.5, 'sugar': 3.8, 'sodium': 598},
    'burger': {'calories': 295, 'protein': 17, 'carbs': 24, 'fat': 14, 'fiber': 1.5, 'sugar': 4, 'sodium': 497},
    'salad': {'calories': 33, 'protein': 2.5, 'carbs': 6.3, 'fat': 0.3, 'fiber': 2.1, 'sugar': 2.4, 'sodium': 65},
    'sandwich': {'calories': 250, 'protein': 12, 'carbs': 30, 'fat': 9, 'fiber': 2, 'sugar': 4, 'sodium': 450},
    
    # Snacks
    'chips': {'calories': 536, 'protein': 6.6, 'carbs': 53, 'fat': 34, 'fiber': 4.4, 'sugar': 0.4, 'sodium': 525},
    'chocolate': {'calories': 546, 'protein': 4.9, 'carbs': 61, 'fat': 31, 'fiber': 7, 'sugar': 48, 'sodium': 24},
    'yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4, 'fiber': 0, 'sugar': 3.2, 'sodium': 36},
    'nuts': {'calories': 607, 'protein': 20, 'carbs': 21, 'fat': 54, 'fiber': 8, 'sugar': 4, 'sodium': 18},

    # Bangalore / Karnataka dishes
    'idli sambar': {'calories': 110, 'protein': 4.5, 'carbs': 19, 'fat': 1.5, 'fiber': 2.5, 'sugar': 1, 'sodium': 90},
    'set dosa': {'calories': 165, 'protein': 4, 'carbs': 24, 'fat': 5, 'fiber': 1.5, 'sugar': 1.2, 'sodium': 120},
    'bisi bele bath': {'calories': 190, 'protein': 6, 'carbs': 29, 'fat': 6, 'fiber': 3, 'sugar': 1.5, 'sodium': 180},
    'ragi mudde': {'calories': 130, 'protein': 3.5, 'carbs': 26, 'fat': 0.8, 'fiber': 2.2, 'sugar': 0.3, 'sodium': 8},
    'akki rotti': {'calories': 155, 'protein': 3.5, 'carbs': 23, 'fat': 5, 'fiber': 2, 'sugar': 0.8, 'sodium': 110},
}


class NutritionCalculator:
    """Calculate nutritional values for food items."""
    
    def __init__(self):
        """Initialize nutrition calculator."""
        self.use_usda_api = bool(USDA_API_KEY)
        if self.use_usda_api:
            logger.info("USDA API key found, will use API for nutrition data")
        else:
            logger.info("No USDA API key, using local nutrition database")
    
    def get_nutrition_info(self, food_name: str, portion_multiplier: float = 1.0) -> Dict[str, any]:
        """
        Get nutrition information for a food item.
        
        Args:
            food_name: Name of the food item
            portion_multiplier: Multiplier for portion size (1.0 = standard serving)
            
        Returns:
            Dictionary with nutrition information
        """
        # Try USDA API first if available
        if self.use_usda_api:
            nutrition = self._get_from_usda_api(food_name)
            if nutrition:
                return self._apply_portion_multiplier(nutrition, portion_multiplier)
        
        # Fallback to local database
        nutrition = self._get_from_local_database(food_name)
        return self._apply_portion_multiplier(nutrition, portion_multiplier)
    
    def _get_from_usda_api(self, food_name: str) -> Optional[Dict[str, any]]:
        """Get nutrition data from USDA FoodData Central API."""
        try:
            # Search for food
            search_url = f"{USDA_API_URL}/foods/search"
            params = {
                'api_key': USDA_API_KEY,
                'query': food_name,
                'pageSize': 1
            }
            
            response = requests.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('foods'):
                return None
            
            food = data['foods'][0]
            nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}
            
            # Map USDA nutrients to our format
            return {
                'calories': nutrients.get('Energy', 0),
                'protein': nutrients.get('Protein', 0),
                'carbs': nutrients.get('Carbohydrate, by difference', 0),
                'fat': nutrients.get('Total lipid (fat)', 0),
                'fiber': nutrients.get('Fiber, total dietary', 0),
                'sugar': nutrients.get('Sugars, total including NLEA', 0),
                'sodium': nutrients.get('Sodium, Na', 0),
                'source': 'usda_api'
            }
            
        except Exception as e:
            logger.warning(f"Error fetching from USDA API: {e}")
            return None
    
    def _get_from_local_database(self, food_name: str) -> Dict[str, any]:
        """Get nutrition data from local database."""
        # Normalize food name
        food_name_lower = food_name.lower().strip()
        
        # Try exact match first
        if food_name_lower in NUTRITION_DATABASE:
            nutrition = NUTRITION_DATABASE[food_name_lower].copy()
            nutrition['source'] = 'local_database'
            nutrition['food_name'] = food_name
            return nutrition
        
        # Try partial match
        for key in NUTRITION_DATABASE:
            if key in food_name_lower or food_name_lower in key:
                nutrition = NUTRITION_DATABASE[key].copy()
                nutrition['source'] = 'local_database_partial'
                nutrition['food_name'] = food_name
                logger.info(f"Partial match: {food_name} -> {key}")
                return nutrition
        
        # Default fallback (average meal)
        logger.warning(f"No nutrition data found for: {food_name}, using default values")
        return {
            'calories': 200,
            'protein': 10,
            'carbs': 25,
            'fat': 8,
            'fiber': 2,
            'sugar': 3,
            'sodium': 200,
            'source': 'default',
            'food_name': food_name
        }
    
    def _apply_portion_multiplier(self, nutrition: Dict[str, any], multiplier: float) -> Dict[str, any]:
        """Apply portion size multiplier to nutrition values."""
        result = nutrition.copy()
        
        # Multiply all numeric values except source
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
            if key in result:
                result[key] = round(result[key] * multiplier, 2)
        
        result['portion_multiplier'] = multiplier
        return result
    
    def calculate_daily_totals(self, food_logs: list) -> Dict[str, float]:
        """
        Calculate daily nutrition totals from food logs.
        
        Args:
            food_logs: List of food log entries
            
        Returns:
            Dictionary with daily totals
        """
        totals = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0
        }
        
        for log in food_logs:
            for key in totals:
                totals[key] += getattr(log, f'{key}' if key == 'calories' else f'{key}_g' if key != 'sodium' else f'{key}_mg', 0) or 0
        
        return {k: round(v, 2) for k, v in totals.items()}


# Global calculator instance
_nutrition_calculator = None

def get_nutrition_calculator() -> NutritionCalculator:
    """Get or create the global nutrition calculator instance."""
    global _nutrition_calculator
    if _nutrition_calculator is None:
        _nutrition_calculator = NutritionCalculator()
    return _nutrition_calculator
