"""
AI-powered recommendation engine for personalized insights.
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.user_models import User, UserProfile, FoodLog, ActivityLog, MoodLog
from src.models.tracking_models import DailySummary

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate personalized recommendations based on user data."""
    
    def __init__(self, db: Session):
        """Initialize recommendation engine."""
        self.db = db
    
    def generate_meal_recommendations(self, user_id: int) -> List[Dict]:
        """
        Generate meal recommendations based on user preferences and goals.
        
        Args:
            user_id: User ID
            
        Returns:
            List of meal recommendations
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.profile:
            return []
        
        profile = user.profile
        recommendations = []
        
        # Get today's food logs to calculate remaining calories
        today = datetime.now().date()
        today_logs = self.db.query(FoodLog).filter(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= datetime.combine(today, datetime.min.time())
        ).all()
        
        consumed_calories = sum(log.calories or 0 for log in today_logs)
        remaining_calories = profile.target_calories - consumed_calories
        
        # Generate recommendations based on dietary preferences
        dietary_type = profile.dietary_type or 'omnivore'
        
        if remaining_calories > 500:
            recommendations.append({
                'meal_type': 'dinner',
                'suggestion': self._get_meal_suggestion(dietary_type, 'dinner'),
                'calories_target': min(remaining_calories, 700),
                'reason': f'You have {int(remaining_calories)} calories remaining for today'
            })
        elif remaining_calories > 200:
            recommendations.append({
                'meal_type': 'snack',
                'suggestion': self._get_meal_suggestion(dietary_type, 'snack'),
                'calories_target': remaining_calories,
                'reason': 'A healthy snack to reach your calorie goal'
            })
        else:
            recommendations.append({
                'meal_type': 'light_option',
                'suggestion': 'Consider a light salad or vegetable soup',
                'calories_target': remaining_calories,
                'reason': 'You\'re close to your calorie goal for today'
            })
        
        return recommendations
    
    def _get_meal_suggestion(self, dietary_type: str, meal_type: str) -> str:
        """Get meal suggestion based on dietary type."""
        suggestions = {
            'vegetarian': {
                'breakfast': 'Oatmeal with fruits and nuts',
                'lunch': 'Quinoa bowl with roasted vegetables',
                'dinner': 'Vegetable stir-fry with tofu and brown rice',
                'snack': 'Greek yogurt with berries'
            },
            'vegan': {
                'breakfast': 'Smoothie bowl with chia seeds and banana',
                'lunch': 'Lentil curry with quinoa',
                'dinner': 'Buddha bowl with chickpeas and tahini',
                'snack': 'Hummus with carrot sticks'
            },
            'keto': {
                'breakfast': 'Scrambled eggs with avocado',
                'lunch': 'Grilled chicken salad with olive oil',
                'dinner': 'Salmon with asparagus and butter',
                'snack': 'Cheese and nuts'
            },
            'omnivore': {
                'breakfast': 'Eggs with whole grain toast and avocado',
                'lunch': 'Grilled chicken with quinoa and vegetables',
                'dinner': 'Baked salmon with sweet potato and broccoli',
                'snack': 'Apple with almond butter'
            }
        }
        
        return suggestions.get(dietary_type, suggestions['omnivore']).get(meal_type, 'Balanced meal')
    
    def generate_activity_recommendations(self, user_id: int) -> List[Dict]:
        """
        Generate workout recommendations based on activity history.
        
        Args:
            user_id: User ID
            
        Returns:
            List of activity recommendations
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.profile:
            return []
        
        # Get recent activity logs
        week_ago = datetime.now() - timedelta(days=7)
        recent_activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.logged_at >= week_ago
        ).all()
        
        total_minutes = sum(act.duration_minutes or 0 for act in recent_activities)
        recommendations = []
        
        # Recommend based on activity level
        if total_minutes < 150:  # Less than recommended 150 min/week
            recommendations.append({
                'activity_type': 'cardio',
                'suggestion': '30-minute brisk walk or light jog',
                'duration_minutes': 30,
                'reason': 'Increase weekly cardio to meet health guidelines'
            })
        
        # Check for variety
        activity_types = set(act.activity_type for act in recent_activities)
        if 'strength' not in activity_types:
            recommendations.append({
                'activity_type': 'strength',
                'suggestion': 'Bodyweight exercises or light weights',
                'duration_minutes': 20,
                'reason': 'Add strength training for balanced fitness'
            })
        
        if 'yoga' not in activity_types and 'stretching' not in activity_types:
            recommendations.append({
                'activity_type': 'flexibility',
                'suggestion': 'Yoga or stretching session',
                'duration_minutes': 15,
                'reason': 'Improve flexibility and reduce injury risk'
            })
        
        return recommendations
    
    def generate_mood_activities(self, user_id: int, current_mood: str = None) -> List[Dict]:
        """
        Suggest mood-regulating activities.
        
        Args:
            user_id: User ID
            current_mood: Current mood state
            
        Returns:
            List of activity suggestions
        """
        # Get recent mood logs to understand patterns
        week_ago = datetime.now() - timedelta(days=7)
        recent_moods = self.db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.logged_at >= week_ago
        ).all()
        
        avg_stress = sum(m.stress_level or 5 for m in recent_moods) / max(len(recent_moods), 1)
        avg_energy = sum(m.energy_level or 5 for m in recent_moods) / max(len(recent_moods), 1)
        
        recommendations = []
        
        # Stress management
        if avg_stress > 6 or (current_mood and current_mood.lower() in ['stressed', 'anxious']):
            recommendations.extend([
                {
                    'activity': 'Deep Breathing Exercise',
                    'duration_minutes': 5,
                    'description': '4-7-8 breathing technique: Inhale for 4, hold for 7, exhale for 8',
                    'benefit': 'Reduces stress and anxiety quickly'
                },
                {
                    'activity': 'Meditation',
                    'duration_minutes': 10,
                    'description': 'Guided mindfulness meditation',
                    'benefit': 'Calms the mind and improves focus'
                }
            ])
        
        # Energy boost
        if avg_energy < 5 or (current_mood and current_mood.lower() in ['tired', 'low']):
            recommendations.extend([
                {
                    'activity': 'Light Cardio',
                    'duration_minutes': 15,
                    'description': 'Quick walk or light jogging',
                    'benefit': 'Increases energy and improves mood'
                },
                {
                    'activity': 'Stretching',
                    'duration_minutes': 10,
                    'description': 'Full body stretching routine',
                    'benefit': 'Releases tension and boosts circulation'
                }
            ])
        
        # General wellness
        recommendations.append({
            'activity': 'Yoga',
            'duration_minutes': 20,
            'description': 'Gentle yoga flow for mind-body connection',
            'benefit': 'Improves flexibility, reduces stress, enhances well-being'
        })
        
        return recommendations
    
    def generate_insights(self, user_id: int) -> Dict:
        """
        Generate personalized insights from user data.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with insights
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.profile:
            return {}
        
        # Analyze last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        
        # Food insights
        food_logs = self.db.query(FoodLog).filter(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= week_ago
        ).all()
        
        avg_daily_calories = sum(log.calories or 0 for log in food_logs) / 7
        target_calories = user.profile.target_calories
        
        # Activity insights
        activity_logs = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.logged_at >= week_ago
        ).all()
        
        total_exercise_minutes = sum(act.duration_minutes or 0 for act in activity_logs)
        
        # Mood insights
        mood_logs = self.db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.logged_at >= week_ago
        ).all()
        
        avg_mood = sum(m.mood_score or 5 for m in mood_logs) / max(len(mood_logs), 1)
        
        insights = {
            'nutrition': {
                'avg_daily_calories': round(avg_daily_calories, 0),
                'target_calories': target_calories,
                'status': 'on_track' if abs(avg_daily_calories - target_calories) < 200 else 'needs_adjustment',
                'message': self._get_nutrition_message(avg_daily_calories, target_calories)
            },
            'activity': {
                'total_minutes': total_exercise_minutes,
                'weekly_goal': 150,
                'status': 'excellent' if total_exercise_minutes >= 150 else 'needs_improvement',
                'message': self._get_activity_message(total_exercise_minutes)
            },
            'wellness': {
                'avg_mood_score': round(avg_mood, 1),
                'status': 'good' if avg_mood >= 6 else 'needs_attention',
                'message': self._get_wellness_message(avg_mood)
            }
        }
        
        return insights
    
    def _get_nutrition_message(self, avg_calories: float, target: int) -> str:
        """Generate nutrition insight message."""
        diff = avg_calories - target
        if abs(diff) < 100:
            return "Perfect! You're hitting your calorie target consistently."
        elif diff > 200:
            return f"You're consuming about {int(diff)} calories above your target. Consider smaller portions or lighter meals."
        else:
            return f"You're about {int(abs(diff))} calories below your target. Make sure you're eating enough to fuel your body."
    
    def _get_activity_message(self, total_minutes: int) -> str:
        """Generate activity insight message."""
        if total_minutes >= 150:
            return f"Excellent! You've completed {total_minutes} minutes of exercise this week."
        elif total_minutes >= 75:
            return f"Good progress with {total_minutes} minutes. Try to add a bit more to reach the 150-minute goal."
        else:
            return f"You've exercised for {total_minutes} minutes. Aim for at least 150 minutes per week for optimal health."
    
    def _get_wellness_message(self, avg_mood: float) -> str:
        """Generate wellness insight message."""
        if avg_mood >= 7:
            return "Your mood has been great! Keep up the good habits."
        elif avg_mood >= 5:
            return "Your mood is stable. Consider adding stress-relief activities for even better well-being."
        else:
            return "Your mood scores suggest you might benefit from wellness activities. Try meditation, yoga, or talking to someone."


def get_recommendation_engine(db: Session) -> RecommendationEngine:
    """Get recommendation engine instance."""
    return RecommendationEngine(db)
