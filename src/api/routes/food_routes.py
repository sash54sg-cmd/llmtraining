"""
Food and nutrition routes.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from src.config.database import get_db
from src.models.user_models import User, FoodLog
from src.api.schemas import FoodLogCreate, FoodLogResponse, FoodAnalysisResponse
from src.api.auth import get_current_active_user
from src.ai.food_recognition import get_food_model
from src.services.nutrition_calculator import get_nutrition_calculator
from src.services.image_handler import get_image_handler

router = APIRouter()


@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze food image and return predictions with nutrition info."""
    # Save uploaded image
    image_handler = get_image_handler()
    file_content = await file.read()
    image_path = image_handler.save_uploaded_image(file_content, file.filename, current_user.id)
    
    # Recognize food
    food_model = get_food_model()
    predictions = food_model.predict(image_path, top_k=3)
    
    # Estimate portion size
    portion_estimate = food_model.estimate_portion_size(image_path)
    
    # Get nutrition info for top prediction
    nutrition_calc = get_nutrition_calculator()
    nutrition = nutrition_calc.get_nutrition_info(
        predictions[0]['food_name'],
        portion_estimate['portion_multiplier']
    )
    
    return {
        "predictions": predictions,
        "nutrition": nutrition,
        "portion_estimate": portion_estimate
    }


@router.post("/manual", response_model=FoodLogResponse, status_code=201)
async def log_food_manually(
    food_data: FoodLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually log food entry."""
    food_log = FoodLog(
        user_id=current_user.id,
        is_manual_entry=True,
        **food_data.model_dump()
    )
    
    db.add(food_log)
    db.commit()
    db.refresh(food_log)
    
    return food_log


@router.post("/log-from-image", response_model=FoodLogResponse, status_code=201)
async def log_food_from_image(
    file: UploadFile = File(...),
    meal_type: str = Form(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze image and log food automatically."""
    # Save and analyze image
    image_handler = get_image_handler()
    file_content = await file.read()
    image_path = image_handler.save_uploaded_image(file_content, file.filename, current_user.id)
    
    food_model = get_food_model()
    predictions = food_model.predict(image_path, top_k=1)
    portion_estimate = food_model.estimate_portion_size(image_path)
    
    # Get nutrition
    nutrition_calc = get_nutrition_calculator()
    nutrition = nutrition_calc.get_nutrition_info(
        predictions[0]['food_name'],
        portion_estimate['portion_multiplier']
    )
    
    # Create food log
    food_log = FoodLog(
        user_id=current_user.id,
        food_name=predictions[0]['food_name'],
        meal_type=meal_type,
        portion_size=portion_estimate['portion_size'],
        calories=nutrition['calories'],
        protein_g=nutrition['protein'],
        carbs_g=nutrition['carbs'],
        fat_g=nutrition['fat'],
        fiber_g=nutrition.get('fiber', 0),
        sugar_g=nutrition.get('sugar', 0),
        sodium_mg=nutrition.get('sodium', 0),
        image_path=image_path,
        detection_confidence=predictions[0]['confidence'],
        is_manual_entry=False,
        notes=notes
    )
    
    db.add(food_log)
    db.commit()
    db.refresh(food_log)
    
    return food_log


@router.get("/search")
async def search_food(query: str, db: Session = Depends(get_db)):
    """Search for food in nutrition database."""
    nutrition_calc = get_nutrition_calculator()
    nutrition = nutrition_calc.get_nutrition_info(query)
    
    return {
        "food_name": query,
        "nutrition": nutrition
    }


@router.get("/history", response_model=List[FoodLogResponse])
async def get_food_history(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get food log history."""
    start_date = datetime.now() - timedelta(days=days)
    
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_date
    ).order_by(FoodLog.logged_at.desc()).all()
    
    return logs


@router.delete("/{log_id}")
async def delete_food_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a food log entry."""
    log = db.query(FoodLog).filter(
        FoodLog.id == log_id,
        FoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    # Delete image if exists
    if log.image_path:
        image_handler = get_image_handler()
        image_handler.delete_image(log.image_path)
    
    db.delete(log)
    db.commit()
    
    return {"message": "Food log deleted successfully"}
