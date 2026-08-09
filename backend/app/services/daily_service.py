from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status

from app.repositories.daily_repository import DailyRepository
from app.schemas.daily import (
    DailySummaryResponse,
    FoodEntryCreate,
    FoodEntryResponse,
    SleepEntryCreate,
    SleepEntryResponse,
    StepsEntryCreate,
    StepsEntryResponse,
    WaterEntryCreate,
    WaterEntryResponse,
    WeightEntryCreate,
    WeightEntryResponse,
    WorkoutSessionCreate,
    WorkoutSessionResponse,
)


class DailyService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = DailyRepository(session)

    async def record_weight(self, *, user_id: str, payload: WeightEntryCreate) -> WeightEntryResponse:
        row = await self.repository.upsert_weight(user_id=user_id, target_date=payload.date, weight_kg=payload.weight_kg)
        return WeightEntryResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            weight_kg=row.weight_kg,
        )

    async def record_water(self, *, user_id: str, payload: WaterEntryCreate) -> WaterEntryResponse:
        row = await self.repository.upsert_water(user_id=user_id, target_date=payload.date, amount_ml=payload.amount_ml)
        return WaterEntryResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            amount_ml=row.amount_ml,
        )

    async def get_daily_summary(self, *, user_id: str, target_date: date) -> DailySummaryResponse:
        weight = await self.repository.get_weight_for_date(user_id=user_id, target_date=target_date)
        water = await self.repository.get_water_for_date(user_id=user_id, target_date=target_date)
        steps = await self.repository.get_steps_for_date(user_id=user_id, target_date=target_date)
        sleep = await self.repository.get_sleep_for_date(user_id=user_id, target_date=target_date)
        workouts = await self.repository.list_workouts_since(user_id=user_id, start_date=target_date)
        workout_count = sum(1 for w in workouts if w.date == target_date)

        food_entries = await self._get_food_entries(user_id=user_id, target_date=target_date)
        total_calories = sum(entry.calories for entry in food_entries)
        total_protein = sum(entry.protein_g for entry in food_entries)
        total_carbs = sum(entry.carbs_g for entry in food_entries)
        total_fat = sum(entry.fat_g for entry in food_entries)

        return DailySummaryResponse(
            date=target_date,
            weight_kg=weight.weight_kg if weight else None,
            water_ml=water.amount_ml if water else 0,
            food_calories=total_calories,
            protein_g=total_protein,
            carbs_g=total_carbs,
            fat_g=total_fat,
            steps=steps.steps if steps else 0,
            sleep_minutes=sleep.duration_minutes if sleep else None,
            workout_sessions=workout_count,
        )

    async def _get_food_entries(self, *, user_id: str, target_date: date):
        from app.repositories.food_repository import FoodRepository

        repo = FoodRepository(self.session)
        return await repo.list_entries_for_date(user_id=user_id, target_date=target_date)

    async def add_food_entry(self, *, user_id: str, payload: FoodEntryCreate) -> FoodEntryResponse:
        repo = self._food_repository()
        row = await repo.create_food_entry(
            user_id=user_id,
            date=payload.date,
            meal_type=payload.meal_type,
            food_name=payload.food_name,
            calories=payload.calories,
            protein_g=payload.protein_g,
            carbs_g=payload.carbs_g,
            fat_g=payload.fat_g,
            notes=payload.notes,
        )
        return FoodEntryResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            meal_type=row.meal_type,
            food_name=row.food_name,
            calories=row.calories,
            protein_g=row.protein_g,
            carbs_g=row.carbs_g,
            fat_g=row.fat_g,
            notes=row.notes,
            food_id=row.food_id,
            quantity_g=row.quantity_g,
        )

    def _food_repository(self):
        from app.repositories.food_repository import FoodRepository

        return FoodRepository(self.session)

    async def record_steps(self, *, user_id: str, payload: StepsEntryCreate) -> StepsEntryResponse:
        row = await self.repository.upsert_steps(user_id=user_id, target_date=payload.date, steps=payload.steps)
        return StepsEntryResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            steps=row.steps,
        )

    async def record_sleep(self, *, user_id: str, payload: SleepEntryCreate) -> SleepEntryResponse:
        row = await self.repository.upsert_sleep(
            user_id=user_id,
            target_date=payload.date,
            bed_time=payload.bed_time,
            wake_time=payload.wake_time,
            duration_minutes=payload.duration_minutes,
            quality=payload.quality,
        )
        return SleepEntryResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            bed_time=row.bed_time,
            wake_time=row.wake_time,
            duration_minutes=row.duration_minutes,
            quality=row.quality,
            source=row.source,
        )

    async def record_workout(self, *, user_id: str, payload: WorkoutSessionCreate) -> WorkoutSessionResponse:
        row = await self.repository.create_workout(
            user_id=user_id,
            target_date=payload.date,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            duration_minutes=payload.duration_minutes,
            notes=payload.notes,
        )
        return WorkoutSessionResponse(
            id=row.id,
            user_id=row.user_id,
            date=row.date,
            name=row.name,
            start_time=row.start_time,
            end_time=row.end_time,
            duration_minutes=row.duration_minutes,
            notes=row.notes,
        )
