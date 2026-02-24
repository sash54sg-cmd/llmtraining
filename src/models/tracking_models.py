"""
Database models for activity and wellness tracking.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base


class PhysicalActivityPlan(Base):
    """Personalized physical activity plans."""
    __tablename__ = "activity_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Plan details
    plan_name = Column(String)
    plan_type = Column(String)  # weekly, monthly, custom
    goal = Column(String)  # fitness, weight_loss, strength, flexibility
    
    # Schedule
    activities = Column(JSON)  # List of planned activities with schedule
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Progress
    is_active = Column(Boolean, default=True)
    completion_rate = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WellnessActivity(Base):
    """Mood-regulating and wellness activities."""
    __tablename__ = "wellness_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Activity details
    activity_type = Column(String)  # yoga, meditation, breathing, stretching, mindfulness
    activity_name = Column(String)
    duration_minutes = Column(Integer)
    
    # Effectiveness
    mood_before = Column(Integer)  # 1-10 scale
    mood_after = Column(Integer)  # 1-10 scale
    effectiveness_rating = Column(Integer)  # 1-5 scale
    
    # Metadata
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)


class DailySummary(Base):
    """Daily summary of nutrition and activity."""
    __tablename__ = "daily_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, nullable=False)
    
    # Nutrition totals
    total_calories = Column(Float, default=0)
    total_protein_g = Column(Float, default=0)
    total_carbs_g = Column(Float, default=0)
    total_fat_g = Column(Float, default=0)
    
    # Activity totals
    total_exercise_minutes = Column(Integer, default=0)
    total_calories_burned = Column(Float, default=0)
    
    # Net calories
    net_calories = Column(Float)  # intake - burned
    
    # Wellness
    average_mood = Column(Float)
    average_energy = Column(Float)
    average_stress = Column(Float)
    
    # Goals met
    calorie_goal_met = Column(Boolean, default=False)
    protein_goal_met = Column(Boolean, default=False)
    exercise_goal_met = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
