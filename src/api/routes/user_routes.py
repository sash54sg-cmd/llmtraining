"""
User profile routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user_models import User, UserProfile
from src.api.schemas import UserProfileCreate, UserProfileResponse
from src.api.auth import get_current_active_user
from src.services.health_calculator import HealthCalculator

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user profile."""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return current_user.profile


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update basic fields
    for key, value in profile_data.model_dump().items():
        setattr(profile, key, value)
    
    # Calculate health metrics
    calc = HealthCalculator()
    profile.bmr = calc.calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
    profile.tdee = calc.calculate_tdee(profile.bmr, profile.activity_level)
    profile.target_calories = calc.calculate_target_calories(profile.tdee, profile.goal_type)
    
    macros = calc.calculate_macro_targets(profile.target_calories, profile.goal_type)
    profile.target_protein_g = macros['protein_g']
    profile.target_carbs_g = macros['carbs_g']
    profile.target_fat_g = macros['fat_g']
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/health-metrics")
async def get_health_metrics(current_user: User = Depends(get_current_active_user)):
    """Get calculated health metrics."""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = current_user.profile
    calc = HealthCalculator()
    bmi_data = calc.calculate_bmi(profile.weight_kg, profile.height_cm)
    
    return {
        "bmr": profile.bmr,
        "tdee": profile.tdee,
        "bmi": bmi_data['bmi'],
        "bmi_category": bmi_data['category'],
        "target_calories": profile.target_calories,
        "target_macros": {
            "protein_g": profile.target_protein_g,
            "carbs_g": profile.target_carbs_g,
            "fat_g": profile.target_fat_g
        }
    }
