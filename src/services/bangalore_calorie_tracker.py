"""Utilities for Bangalore-focused calorie tracking workflows."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class BangaloreFoodItem:
    """Represents a local dish with estimated nutrition per serving."""

    key: str
    name: str
    meal_type: str
    serving_description: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    best_time: str
    local_note: str


BANGALORE_FOOD_CATALOG: Dict[str, BangaloreFoodItem] = {
    "idli_sambar": BangaloreFoodItem(
        key="idli_sambar",
        name="Idli + Sambar",
        meal_type="breakfast",
        serving_description="2 idlis + 1 katori sambar",
        calories=220,
        protein_g=9,
        carbs_g=38,
        fat_g=3,
        fiber_g=5,
        best_time="Morning",
        local_note="A light option common across Bengaluru darshinis.",
    ),
    "set_dosa": BangaloreFoodItem(
        key="set_dosa",
        name="Set Dosa",
        meal_type="breakfast",
        serving_description="2 dosas with chutney",
        calories=330,
        protein_g=8,
        carbs_g=48,
        fat_g=10,
        fiber_g=3,
        best_time="Morning",
        local_note="Popular soft dosa option in Bengaluru tiffin spots.",
    ),
    "ragi_mudde_soppu": BangaloreFoodItem(
        key="ragi_mudde_soppu",
        name="Ragi Mudde + Soppu Saaru",
        meal_type="lunch",
        serving_description="1 mudde + 1 bowl saaru",
        calories=360,
        protein_g=11,
        carbs_g=62,
        fat_g=7,
        fiber_g=8,
        best_time="Lunch",
        local_note="Traditional Karnataka meal with better satiety.",
    ),
    "bisi_bele_bath": BangaloreFoodItem(
        key="bisi_bele_bath",
        name="Bisi Bele Bath",
        meal_type="lunch",
        serving_description="1 medium plate",
        calories=380,
        protein_g=12,
        carbs_g=58,
        fat_g=12,
        fiber_g=6,
        best_time="Lunch",
        local_note="Balanced one-pot Karnataka classic.",
    ),
    "millet_upma": BangaloreFoodItem(
        key="millet_upma",
        name="Millet Upma",
        meal_type="snack",
        serving_description="1 bowl",
        calories=250,
        protein_g=7,
        carbs_g=42,
        fat_g=6,
        fiber_g=5,
        best_time="Evening",
        local_note="A common healthy cafe option in Bengaluru.",
    ),
    "akki_rotti": BangaloreFoodItem(
        key="akki_rotti",
        name="Akki Rotti",
        meal_type="dinner",
        serving_description="2 rotis + chutney",
        calories=310,
        protein_g=7,
        carbs_g=46,
        fat_g=10,
        fiber_g=4,
        best_time="Dinner",
        local_note="Good for a lighter dinner with curd.",
    ),
}


def list_catalog() -> List[Dict[str, str]]:
    """Return the Bangalore dish catalog in a response-ready format."""
    return [
        {
            "key": item.key,
            "name": item.name,
            "meal_type": item.meal_type,
            "serving_description": item.serving_description,
            "calories": item.calories,
            "protein_g": item.protein_g,
            "carbs_g": item.carbs_g,
            "fat_g": item.fat_g,
            "fiber_g": item.fiber_g,
            "best_time": item.best_time,
            "local_note": item.local_note,
        }
        for item in BANGALORE_FOOD_CATALOG.values()
    ]


def get_item(item_key: str) -> BangaloreFoodItem:
    """Get a Bangalore catalog item by key."""
    normalized_key = item_key.lower().strip()
    if normalized_key not in BANGALORE_FOOD_CATALOG:
        valid_keys = ", ".join(BANGALORE_FOOD_CATALOG.keys())
        raise ValueError(f"Unknown item key '{item_key}'. Choose from: {valid_keys}")
    return BANGALORE_FOOD_CATALOG[normalized_key]


def serving_multiplier_to_size(multiplier: float) -> str:
    """Map serving multipliers to a human-friendly portion size label."""
    if multiplier <= 0.75:
        return "small"
    if multiplier <= 1.25:
        return "medium"
    return "large"


def build_daily_message(total_calories: float, target_calories: int) -> str:
    """Create a Bangalore-specific summary line for the user."""
    now = datetime.now()
    remaining = max(target_calories - total_calories, 0)

    if now.hour < 12:
        meal_hint = "Consider an idli-sambar or millet upma start before commute traffic."
    elif now.hour < 17:
        meal_hint = "A balanced lunch like bisi bele bath can keep energy steady for the workday."
    else:
        meal_hint = "For dinner, prefer lighter options like akki rotti with a veggie side."

    return f"{remaining:.0f} kcal left for today. {meal_hint}"
