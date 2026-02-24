"""
Activity and wellness tracking routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from src.config.database import get_db
from src.models.user_models import User, ActivityLog, MoodLog
from src.models.tracking_models import DailySummary
from src.api.schemas import ActivityLogCreate, ActivityLogResponse, MoodLogCreate, MoodLogResponse, DashboardResponse
from src.api.auth import get_current_active_user
from src.services.health_calculator import HealthCalculator
from src.ai.recommendation_engine import get_recommendation_engine

router = APIRouter()


@router.post("/workout", response_model=ActivityLogResponse, status_code=201)
async def log_workout(
    activity_data: ActivityLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log a workout or exercise activity."""
    # Calculate calories burned
    calc = HealthCalculator()
    calories_burned = calc.calculate_calories_burned(
        activity_data.activity_type,
        activity_data.duration_minutes,
        current_user.profile.weight_kg if current_user.profile else 70,
        activity_data.intensity
    )
    
    activity_log = ActivityLog(
        user_id=current_user.id,
        calories_burned=calories_burned,
        **activity_data.model_dump()
    )
    
    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)
    
    return activity_log


@router.post("/mood", response_model=MoodLogResponse, status_code=201)
async def log_mood(
    mood_data: MoodLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log mood and emotional state."""
    mood_log = MoodLog(
        user_id=current_user.id,
        **mood_data.model_dump()
    )
    
    db.add(mood_log)
    db.commit()
    db.refresh(mood_log)
    
    return mood_log


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard with daily summary and progress."""
    today = datetime.now().date()
    
    # Get today's food logs
    from src.models.user_models import FoodLog
    food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= datetime.combine(today, datetime.min.time())
    ).all()
    
    # Get today's activities
    activity_logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.logged_at >= datetime.combine(today, datetime.min.time())
    ).all()
    
    # Get today's mood logs
    mood_logs = db.query(MoodLog).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.logged_at >= datetime.combine(today, datetime.min.time())
    ).all()
    
    # Calculate totals
    total_calories = sum(log.calories or 0 for log in food_logs)
    total_protein = sum(log.protein_g or 0 for log in food_logs)
    total_carbs = sum(log.carbs_g or 0 for log in food_logs)
    total_fat = sum(log.fat_g or 0 for log in food_logs)
    
    total_exercise_minutes = sum(act.duration_minutes or 0 for act in activity_logs)
    total_calories_burned = sum(act.calories_burned or 0 for act in activity_logs)
    
    avg_mood = sum(m.mood_score for m in mood_logs) / len(mood_logs) if mood_logs else 5
    avg_energy = sum(m.energy_level for m in mood_logs) / len(mood_logs) if mood_logs else 5
    avg_stress = sum(m.stress_level for m in mood_logs) / len(mood_logs) if mood_logs else 5
    
    # Check goals
    profile = current_user.profile
    goals_met = {}
    if profile:
        goals_met = {
            "calorie_goal_met": abs(total_calories - profile.target_calories) < 200,
            "protein_goal_met": total_protein >= profile.target_protein_g * 0.9,
            "exercise_goal_met": total_exercise_minutes >= 30
        }
    
    return {
        "date": datetime.now(),
        "nutrition": {
            "calories": round(total_calories, 1),
            "protein_g": round(total_protein, 1),
            "carbs_g": round(total_carbs, 1),
            "fat_g": round(total_fat, 1),
            "target_calories": profile.target_calories if profile else 2000,
            "remaining_calories": (profile.target_calories if profile else 2000) - total_calories
        },
        "activity": {
            "exercise_minutes": total_exercise_minutes,
            "calories_burned": round(total_calories_burned, 1),
            "activities_count": len(activity_logs)
        },
        "wellness": {
            "avg_mood": round(avg_mood, 1),
            "avg_energy": round(avg_energy, 1),
            "avg_stress": round(avg_stress, 1),
            "mood_logs_count": len(mood_logs)
        },
        "goals_met": goals_met
    }


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated insights and recommendations."""
    rec_engine = get_recommendation_engine(db)
    insights = rec_engine.generate_insights(current_user.id)
    
    meal_recs = rec_engine.generate_meal_recommendations(current_user.id)
    activity_recs = rec_engine.generate_activity_recommendations(current_user.id)
    
    return {
        "insights": insights,
        "meal_recommendations": meal_recs,
        "activity_recommendations": activity_recs
    }


@router.get("/mood-activities")
async def get_mood_activities(
    mood: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood-regulating activity suggestions."""
    rec_engine = get_recommendation_engine(db)
    activities = rec_engine.generate_mood_activities(current_user.id, mood)
    
    return {"activities": activities}


@router.get("/history/activities", response_model=List[ActivityLogResponse])
async def get_activity_history(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get activity log history."""
    start_date = datetime.now() - timedelta(days=days)
    
    logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.logged_at >= start_date
    ).order_by(ActivityLog.logged_at.desc()).all()
    
    return logs


@router.get("/history/mood", response_model=List[MoodLogResponse])
async def get_mood_history(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood log history."""
    start_date = datetime.now() - timedelta(days=days)
    
    logs = db.query(MoodLog).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.logged_at >= start_date
    ).order_by(MoodLog.logged_at.desc()).all()
    
    return logs
