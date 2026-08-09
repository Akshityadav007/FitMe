"""Builds a compact, deterministic CoachContext snapshot for the AI coach.

The context is assembled from backend queries only; the LLM never sees
the entire database. Tools remain available for on-demand fetches.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.repositories.daily_repository import DailyRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.user_repository import UserRepository


async def build_coach_context(session, user_id: str, target_date: date) -> dict:
    user_repository = UserRepository(session)
    food_repository = FoodRepository(session)
    daily_repository = DailyRepository(session)
    menu_repository = MenuRepository(session)

    profile = await user_repository.get_profile(user_id)
    target = await user_repository.get_nutrition_target(user_id)

    entries = await food_repository.list_entries_for_date(user_id=user_id, target_date=target_date)
    consumed = {
        "calories": sum(entry.calories for entry in entries),
        "protein_g": sum(entry.protein_g for entry in entries),
        "carbs_g": sum(entry.carbs_g for entry in entries),
        "fat_g": sum(entry.fat_g for entry in entries),
    }

    targets = {
        "calories": target.calories if target else 2200,
        "protein_g": target.protein_g if target else 150,
        "carbs_g": target.carbs_g if target else 250,
        "fat_g": target.fat_g if target else 60,
        "water_ml": target.water_ml if target else 2500,
    }

    remaining = {
        key: max(0, targets[key] - consumed.get(key, 0))
        for key in ("calories", "protein_g", "carbs_g", "fat_g")
    }

    water = await daily_repository.get_water_for_date(user_id=user_id, target_date=target_date)
    steps = await daily_repository.get_steps_for_date(user_id=user_id, target_date=target_date)
    sleep = await daily_repository.get_sleep_for_date(user_id=user_id, target_date=target_date)
    workouts = await daily_repository.list_workouts_since(
        user_id=user_id,
        start_date=target_date,
    )
    workout_count = sum(1 for session in workouts if session.date == target_date)

    menu_rows = await menu_repository.list_items_for_date(user_id=user_id, target_date=target_date)
    menu = [
        {
            "name": row.name,
            "calories": row.estimated_calories,
            "protein_g": row.estimated_protein_g,
            "carbs_g": row.estimated_carbs_g,
            "fat_g": row.estimated_fat_g,
            "confidence": row.confidence,
        }
        for row in menu_rows
    ]

    start = target_date - timedelta(days=6)
    recent_weights = await daily_repository.list_weights_since(user_id=user_id, start_date=start)
    weight_entries = [{"date": str(row.date), "weight_kg": row.weight_kg} for row in recent_weights]
    weight_avg = round(sum(row.weight_kg for row in recent_weights) / len(recent_weights), 2) if recent_weights else None

    recent_sleep = await daily_repository.list_sleep_since(user_id=user_id, start_date=start)
    recent_training = await daily_repository.list_workouts_since(user_id=user_id, start_date=start)

    return {
        "date": str(target_date),
        "user": {
            "age": profile.age if profile else None,
            "sex": profile.sex if profile else None,
            "height_cm": profile.height_cm if profile else None,
            "weight_kg": profile.weight_kg if profile else None,
            "goal": profile.goal if profile else None,
            "activity_level": profile.activity_level if profile else None,
            "dietary_preferences": profile.dietary_preferences if profile else None,
        },
        "targets": targets,
        "today": {
            **consumed,
            "water_ml": water.amount_ml if water else 0,
            "steps": steps.steps if steps else 0,
            "sleep_minutes": sleep.duration_minutes if sleep else None,
            "workout_sessions": workout_count,
        },
        "remaining": remaining,
        "today_menu": menu,
        "recent_weight": {"entries": weight_entries, "seven_day_avg_kg": weight_avg},
        "recent_sleep": [
            {"date": str(row.date), "duration_minutes": row.duration_minutes, "quality": row.quality}
            for row in recent_sleep
        ],
        "recent_training": [
            {"date": str(row.date), "name": row.name, "duration_minutes": row.duration_minutes}
            for row in recent_training
        ],
    }
