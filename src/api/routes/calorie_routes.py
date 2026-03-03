"""Bangalore-focused calorie tracker routes."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.auth import get_current_active_user
from src.api.schemas import BangaloreQuickLogRequest, BangaloreDailySummaryResponse
from src.config.database import get_db
from src.models.user_models import FoodLog, User
from src.services.bangalore_calorie_tracker import (
    build_daily_message,
    get_item,
    list_catalog,
    serving_multiplier_to_size,
)
from src.services.nutrition_calculator import get_nutrition_calculator


router = APIRouter()


@router.get("/catalog")
async def get_bangalore_catalog():
    """List curated Bengaluru-friendly dishes with nutrition estimates."""
    return {"city": "Bengaluru", "items": list_catalog()}


@router.post("/quick-log", status_code=201)
async def quick_log_bangalore_food(
    request: BangaloreQuickLogRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Log a meal by selecting a known Bangalore dish and serving size."""
    try:
        item = get_item(request.item_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    nutrition_calc = get_nutrition_calculator()
    nutrition = nutrition_calc._apply_portion_multiplier(
        {
            "calories": item.calories,
            "protein": item.protein_g,
            "carbs": item.carbs_g,
            "fat": item.fat_g,
            "fiber": item.fiber_g,
            "sugar": 2,
            "sodium": 180,
            "source": "bangalore_catalog",
        },
        request.servings,
    )

    food_log = FoodLog(
        user_id=current_user.id,
        food_name=item.name,
        meal_type=request.meal_type or item.meal_type,
        portion_size=serving_multiplier_to_size(request.servings),
        calories=nutrition["calories"],
        protein_g=nutrition["protein"],
        carbs_g=nutrition["carbs"],
        fat_g=nutrition["fat"],
        fiber_g=nutrition["fiber"],
        sugar_g=nutrition["sugar"],
        sodium_mg=nutrition["sodium"],
        is_manual_entry=True,
        notes=request.notes,
    )

    db.add(food_log)
    db.commit()
    db.refresh(food_log)

    return {
        "message": "Meal logged successfully",
        "city": "Bengaluru",
        "food_log_id": food_log.id,
        "nutrition": nutrition,
    }


@router.get("/daily-summary", response_model=BangaloreDailySummaryResponse)
async def get_bangalore_daily_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return today's calories summary and Bangalore-aware food guidance."""
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_of_day,
        FoodLog.logged_at < end_of_day,
    ).all()

    total_calories = round(sum(log.calories or 0 for log in logs), 2)
    total_protein = round(sum(log.protein_g or 0 for log in logs), 2)
    target = getattr(current_user.profile, "target_calories", None) or 2000
    remaining = round(max(target - total_calories, 0), 2)

    return {
        "city": "Bengaluru",
        "date": start_of_day,
        "total_calories": total_calories,
        "target_calories": target,
        "remaining_calories": remaining,
        "total_protein_g": total_protein,
        "meal_count": len(logs),
        "tip": build_daily_message(total_calories, target),
    }
