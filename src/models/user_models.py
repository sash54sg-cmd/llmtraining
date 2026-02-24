"""
Database models for user profiles and health tracking.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base


class User(Base):
    """User account and profile."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    food_logs = relationship("FoodLog", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    mood_logs = relationship("MoodLog", back_populates="user")


class UserProfile(Base):
    """User health profile and preferences."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Basic info
    age = Column(Integer)
    gender = Column(String)  # male, female, other
    height_cm = Column(Float)
    weight_kg = Column(Float)
    
    # Health goals
    goal_type = Column(String)  # weight_loss, muscle_gain, maintenance, health
    target_weight_kg = Column(Float)
    activity_level = Column(String)  # sedentary, light, moderate, active, very_active
    
    # Dietary preferences
    dietary_type = Column(String)  # omnivore, vegetarian, vegan, pescatarian, keto, etc.
    allergies = Column(JSON)  # List of allergies
    food_preferences = Column(JSON)  # Liked/disliked foods
    cuisines = Column(JSON)  # Preferred cuisines
    
    # Medical considerations (non-diagnostic)
    medical_notes = Column(Text)  # General health notes
    
    # Calculated values
    bmr = Column(Float)  # Basal Metabolic Rate
    tdee = Column(Float)  # Total Daily Energy Expenditure
    target_calories = Column(Integer)
    target_protein_g = Column(Integer)
    target_carbs_g = Column(Integer)
    target_fat_g = Column(Integer)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class FoodLog(Base):
    """Daily food intake records."""
    __tablename__ = "food_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Food details
    food_name = Column(String, nullable=False)
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    portion_size = Column(String)
    
    # Nutrition info
    calories = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    fiber_g = Column(Float)
    sugar_g = Column(Float)
    sodium_mg = Column(Float)
    
    # Image and detection
    image_path = Column(String)
    detection_confidence = Column(Float)
    is_manual_entry = Column(Boolean, default=False)
    
    # Metadata
    logged_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="food_logs")


class ActivityLog(Base):
    """Workout and exercise activity tracking."""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Activity details
    activity_type = Column(String)  # cardio, strength, yoga, sports, etc.
    activity_name = Column(String)
    duration_minutes = Column(Integer)
    intensity = Column(String)  # low, moderate, high
    
    # Calories burned
    calories_burned = Column(Float)
    
    # Metadata
    logged_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


class MoodLog(Base):
    """Mood and emotional state tracking."""
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Mood details
    mood_state = Column(String)  # happy, sad, anxious, stressed, energetic, tired, etc.
    mood_score = Column(Integer)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    
    # Context
    triggers = Column(JSON)  # List of potential triggers
    activities_done = Column(JSON)  # Activities that helped
    notes = Column(Text)
    
    # Metadata
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mood_logs")


class Conversation(Base):
    """AI conversation history."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Message details
    user_message = Column(Text)
    ai_response = Column(Text)
    context = Column(JSON)  # Additional context used for response
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
