"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Authentication schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# User profile schemas
class UserProfileCreate(BaseModel):
    age: int = Field(..., gt=0, lt=150)
    gender: str
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    goal_type: str
    activity_level: str
    dietary_type: Optional[str] = "omnivore"
    allergies: Optional[List[str]] = []
    food_preferences: Optional[dict] = {}
    cuisines: Optional[List[str]] = []
    medical_notes: Optional[str] = None


class UserProfileResponse(UserProfileCreate):
    id: int
    user_id: int
    bmr: Optional[float]
    tdee: Optional[float]
    target_calories: Optional[int]
    target_protein_g: Optional[int]
    target_carbs_g: Optional[int]
    target_fat_g: Optional[int]
    
    class Config:
        from_attributes = True


# Food logging schemas
class FoodLogCreate(BaseModel):
    food_name: str
    meal_type: str
    portion_size: Optional[str] = "medium"
    calories: float
    protein_g: Optional[float] = 0
    carbs_g: Optional[float] = 0
    fat_g: Optional[float] = 0
    fiber_g: Optional[float] = 0
    sugar_g: Optional[float] = 0
    sodium_mg: Optional[float] = 0
    notes: Optional[str] = None


class FoodLogResponse(FoodLogCreate):
    id: int
    user_id: int
    image_path: Optional[str]
    detection_confidence: Optional[float]
    is_manual_entry: bool
    logged_at: datetime
    
    class Config:
        from_attributes = True


class FoodAnalysisResponse(BaseModel):
    predictions: List[dict]
    nutrition: dict
    portion_estimate: dict


# Activity logging schemas
class ActivityLogCreate(BaseModel):
    activity_type: str
    activity_name: str
    duration_minutes: int = Field(..., gt=0)
    intensity: str = "moderate"
    notes: Optional[str] = None


class ActivityLogResponse(ActivityLogCreate):
    id: int
    user_id: int
    calories_burned: Optional[float]
    logged_at: datetime
    
    class Config:
        from_attributes = True


# Mood logging schemas
class MoodLogCreate(BaseModel):
    mood_state: str
    mood_score: int = Field(..., ge=1, le=10)
    energy_level: int = Field(..., ge=1, le=10)
    stress_level: int = Field(..., ge=1, le=10)
    triggers: Optional[List[str]] = []
    activities_done: Optional[List[str]] = []
    notes: Optional[str] = None


class MoodLogResponse(MoodLogCreate):
    id: int
    user_id: int
    logged_at: datetime
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    context: Optional[dict] = None


class MultiModalResponse(BaseModel):
    response: str
    context: Optional[dict] = None
    image_analysis: Optional[FoodAnalysisResponse] = None
    transcription: Optional[str] = None


# Dashboard schemas


class BangaloreQuickLogRequest(BaseModel):
    item_key: str
    servings: float = Field(1.0, gt=0, le=4)
    meal_type: Optional[str] = None
    notes: Optional[str] = None


class BangaloreDailySummaryResponse(BaseModel):
    city: str
    date: datetime
    total_calories: float
    target_calories: int
    remaining_calories: float
    total_protein_g: float
    meal_count: int
    tip: str


class DashboardResponse(BaseModel):
    date: datetime
    nutrition: dict
    activity: dict
    wellness: dict
    goals_met: dict
