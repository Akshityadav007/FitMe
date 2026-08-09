"""Tool definitions and server-side argument validation for the AI coach.

Every tool call made by the model is validated against a Pydantic model
before any repository or service method runs.
"""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, Field


class EmptyArgs(BaseModel):
    pass


class DateArgs(BaseModel):
    date: date_type | None = None


class DaysArgs(BaseModel):
    days: int = Field(default=14, ge=1, le=90)


class FoodLogArgs(BaseModel):
    date: date_type | None = None
    meal_type: str = "meal"
    food_name: str = Field(min_length=1, max_length=255)
    calories: int = Field(ge=0)
    protein_g: int = Field(ge=0)
    carbs_g: int = Field(ge=0)
    fat_g: int = Field(ge=0)
    notes: str | None = None


class WaterLogArgs(BaseModel):
    date: date_type | None = None
    amount_ml: int = Field(ge=0)


class WeightLogArgs(BaseModel):
    date: date_type | None = None
    weight_kg: float = Field(gt=0)


class SleepLogArgs(BaseModel):
    date: date_type | None = None
    duration_minutes: int = Field(ge=0)
    quality: int | None = Field(default=None, ge=1, le=5)


class WorkoutLogArgs(BaseModel):
    date: date_type | None = None
    name: str = Field(min_length=1, max_length=120)
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class RecommendMealArgs(BaseModel):
    date: date_type | None = None
    meal_type: str = "lunch"


TOOL_ARG_MODELS: dict[str, type[BaseModel]] = {
    "get_user_profile": EmptyArgs,
    "get_today_summary": DateArgs,
    "get_remaining_targets": DateArgs,
    "get_today_menu": DateArgs,
    "get_recent_weight_trend": DaysArgs,
    "get_recent_training": DaysArgs,
    "get_recent_sleep": DaysArgs,
    "log_food": FoodLogArgs,
    "log_water": WaterLogArgs,
    "log_weight": WeightLogArgs,
    "log_sleep": SleepLogArgs,
    "log_workout": WorkoutLogArgs,
    "recommend_meal": RecommendMealArgs,
}


def _tool_definition(name: str, description: str, model: type[BaseModel]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": model.model_json_schema(),
        },
    }


TOOL_DEFINITIONS: list[dict] = [
    _tool_definition(
        "get_user_profile",
        "Fetch the user's profile: age, sex, height, current weight, goal, activity level, and dietary preferences.",
        EmptyArgs,
    ),
    _tool_definition(
        "get_today_summary",
        "Fetch a deterministic daily summary for a date: calories, protein, carbs, fat, water, steps, sleep, and workout count.",
        DateArgs,
    ),
    _tool_definition(
        "get_remaining_targets",
        "Fetch today's nutrition targets, consumed totals, and remaining calories/protein/carbs/fat for a date.",
        DateArgs,
    ),
    _tool_definition(
        "get_today_menu",
        "Fetch the office menu items available for a date, with estimated nutrition and confidence.",
        DateArgs,
    ),
    _tool_definition(
        "get_recent_weight_trend",
        "Fetch recent daily weight entries and the 7-day average for the last N days.",
        DaysArgs,
    ),
    _tool_definition(
        "get_recent_training",
        "Fetch recent workout sessions (date, name, duration) for the last N days.",
        DaysArgs,
    ),
    _tool_definition(
        "get_recent_sleep",
        "Fetch recent sleep entries (date, duration, quality) for the last N days.",
        DaysArgs,
    ),
    _tool_definition(
        "log_food",
        "Log a food entry with meal type and nutrition values for a date.",
        FoodLogArgs,
    ),
    _tool_definition(
        "log_water",
        "Log a water entry (ml) for a date.",
        WaterLogArgs,
    ),
    _tool_definition(
        "log_weight",
        "Log a body weight entry (kg) for a date.",
        WeightLogArgs,
    ),
    _tool_definition(
        "log_sleep",
        "Log a sleep entry with duration in minutes for a date.",
        SleepLogArgs,
    ),
    _tool_definition(
        "log_workout",
        "Log a workout session with a name and optional duration for a date.",
        WorkoutLogArgs,
    ),
    _tool_definition(
        "recommend_meal",
        "Get a deterministic meal recommendation grounded in remaining targets, dietary preferences, and the available menu for a date.",
        RecommendMealArgs,
    ),
]
