"""
Health calculations including BMR, TDEE, and macro targets.
"""
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthCalculator:
    """Calculate health metrics and targets."""
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            age: Age in years
            gender: 'male' or 'female'
            
        Returns:
            BMR in calories per day
        """
        # Mifflin-St Jeor Equation
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
        
        if gender.lower() == 'male':
            bmr += 5
        else:  # female
            bmr -= 161
        
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure.
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level (sedentary, light, moderate, active, very_active)
            
        Returns:
            TDEE in calories per day
        """
        activity_multipliers = {
            'sedentary': 1.2,      # Little or no exercise
            'light': 1.375,        # Light exercise 1-3 days/week
            'moderate': 1.55,      # Moderate exercise 3-5 days/week
            'active': 1.725,       # Heavy exercise 6-7 days/week
            'very_active': 1.9     # Very heavy exercise, physical job
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        tdee = bmr * multiplier
        
        return round(tdee, 2)
    
    @staticmethod
    def calculate_target_calories(tdee: float, goal_type: str) -> int:
        """
        Calculate target daily calories based on goal.
        
        Args:
            tdee: Total Daily Energy Expenditure
            goal_type: Goal type (weight_loss, muscle_gain, maintenance, health)
            
        Returns:
            Target calories per day
        """
        adjustments = {
            'weight_loss': -500,      # 500 calorie deficit for ~0.5kg/week loss
            'muscle_gain': 300,       # 300 calorie surplus for muscle building
            'maintenance': 0,         # Maintain current weight
            'health': 0               # General health maintenance
        }
        
        adjustment = adjustments.get(goal_type.lower(), 0)
        target = tdee + adjustment
        
        return int(round(target, 0))
    
    @staticmethod
    def calculate_macro_targets(target_calories: int, goal_type: str) -> Dict[str, int]:
        """
        Calculate macronutrient targets.
        
        Args:
            target_calories: Target daily calories
            goal_type: Goal type (weight_loss, muscle_gain, maintenance, health)
            
        Returns:
            Dictionary with protein, carbs, and fat targets in grams
        """
        # Macro ratios based on goal (protein%, carbs%, fat%)
        macro_ratios = {
            'weight_loss': (0.35, 0.35, 0.30),    # Higher protein, moderate carbs
            'muscle_gain': (0.30, 0.45, 0.25),    # High carbs for energy
            'maintenance': (0.25, 0.45, 0.30),    # Balanced
            'health': (0.25, 0.45, 0.30)          # Balanced
        }
        
        protein_ratio, carbs_ratio, fat_ratio = macro_ratios.get(goal_type.lower(), (0.25, 0.45, 0.30))
        
        # Calculate grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
        protein_g = int((target_calories * protein_ratio) / 4)
        carbs_g = int((target_calories * carbs_ratio) / 4)
        fat_g = int((target_calories * fat_ratio) / 9)
        
        return {
            'protein_g': protein_g,
            'carbs_g': carbs_g,
            'fat_g': fat_g
        }
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, any]:
        """
        Calculate Body Mass Index.
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            
        Returns:
            Dictionary with BMI value and category
        """
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Determine category
        if bmi < 18.5:
            category = 'underweight'
        elif bmi < 25:
            category = 'normal'
        elif bmi < 30:
            category = 'overweight'
        else:
            category = 'obese'
        
        return {
            'bmi': round(bmi, 2),
            'category': category
        }
    
    @staticmethod
    def calculate_calories_burned(activity_type: str, duration_minutes: int, 
                                 weight_kg: float, intensity: str = 'moderate') -> float:
        """
        Estimate calories burned during activity.
        
        Args:
            activity_type: Type of activity
            duration_minutes: Duration in minutes
            weight_kg: User weight in kilograms
            intensity: Activity intensity (low, moderate, high)
            
        Returns:
            Estimated calories burned
        """
        # MET (Metabolic Equivalent of Task) values for different activities
        met_values = {
            'cardio': {'low': 3.5, 'moderate': 7.0, 'high': 10.0},
            'strength': {'low': 3.0, 'moderate': 5.0, 'high': 6.0},
            'yoga': {'low': 2.5, 'moderate': 3.0, 'high': 4.0},
            'sports': {'low': 5.0, 'moderate': 8.0, 'high': 10.0},
            'walking': {'low': 2.5, 'moderate': 3.5, 'high': 5.0},
            'running': {'low': 7.0, 'moderate': 9.0, 'high': 11.0},
            'cycling': {'low': 4.0, 'moderate': 8.0, 'high': 12.0},
            'swimming': {'low': 6.0, 'moderate': 8.0, 'high': 10.0},
        }
        
        # Get MET value
        activity_mets = met_values.get(activity_type.lower(), met_values['cardio'])
        met = activity_mets.get(intensity.lower(), activity_mets['moderate'])
        
        # Calculate calories: MET * weight_kg * duration_hours
        duration_hours = duration_minutes / 60
        calories_burned = met * weight_kg * duration_hours
        
        return round(calories_burned, 2)
    
    @staticmethod
    def update_profile_calculations(profile_data: Dict) -> Dict:
        """
        Calculate all health metrics for a user profile.
        
        Args:
            profile_data: Dictionary with user profile data
            
        Returns:
            Updated profile data with calculated values
        """
        # Calculate BMR
        bmr = HealthCalculator.calculate_bmr(
            profile_data['weight_kg'],
            profile_data['height_cm'],
            profile_data['age'],
            profile_data['gender']
        )
        
        # Calculate TDEE
        tdee = HealthCalculator.calculate_tdee(
            bmr,
            profile_data['activity_level']
        )
        
        # Calculate target calories
        target_calories = HealthCalculator.calculate_target_calories(
            tdee,
            profile_data['goal_type']
        )
        
        # Calculate macro targets
        macros = HealthCalculator.calculate_macro_targets(
            target_calories,
            profile_data['goal_type']
        )
        
        # Calculate BMI
        bmi_data = HealthCalculator.calculate_bmi(
            profile_data['weight_kg'],
            profile_data['height_cm']
        )
        
        # Update profile data
        profile_data.update({
            'bmr': bmr,
            'tdee': tdee,
            'target_calories': target_calories,
            'target_protein_g': macros['protein_g'],
            'target_carbs_g': macros['carbs_g'],
            'target_fat_g': macros['fat_g'],
            'bmi': bmi_data['bmi'],
            'bmi_category': bmi_data['category']
        })
        
        return profile_data


# Global calculator instance
_health_calculator = None

def get_health_calculator() -> HealthCalculator:
    """Get or create the global health calculator instance."""
    global _health_calculator
    if _health_calculator is None:
        _health_calculator = HealthCalculator()
    return _health_calculator
