from src.services.bangalore_calorie_tracker import (
    get_item,
    list_catalog,
    serving_multiplier_to_size,
    build_daily_message,
)
from src.services.nutrition_calculator import NutritionCalculator


def test_catalog_contains_local_dishes():
    catalog = list_catalog()
    keys = {item["key"] for item in catalog}

    assert "idli_sambar" in keys
    assert "bisi_bele_bath" in keys


def test_get_item_raises_for_unknown_key():
    try:
        get_item("unknown_dish")
        assert False, "Expected ValueError for unknown key"
    except ValueError as exc:
        assert "Unknown item key" in str(exc)


def test_portion_label_mapping():
    assert serving_multiplier_to_size(0.5) == "small"
    assert serving_multiplier_to_size(1.0) == "medium"
    assert serving_multiplier_to_size(1.8) == "large"


def test_local_database_has_bangalore_foods():
    calc = NutritionCalculator()
    nutrition = calc.get_nutrition_info("idli sambar")

    assert nutrition["calories"] > 0
    assert nutrition["source"].startswith("local_database")


def test_daily_message_mentions_remaining_calories():
    message = build_daily_message(total_calories=1400, target_calories=2000)
    assert "kcal left" in message
