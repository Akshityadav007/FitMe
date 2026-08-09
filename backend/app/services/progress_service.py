from __future__ import annotations

from datetime import date, timedelta

from app.repositories.daily_repository import DailyRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.user_repository import UserRepository
from app.schemas.progress import (
    HydrationSummary,
    NutritionSummary,
    SleepSummary,
    StepsSummary,
    TrainingSummary,
    WeeklyProgressResponse,
    WeightEntry,
    WeightSummary,
)


class WeeklyProgressService:
    def __init__(self, session) -> None:
        self.session = session
        self.daily_repository = DailyRepository(session)
        self.food_repository = FoodRepository(session)
        self.user_repository = UserRepository(session)

    async def aggregate(self, *, user_id: str, end_date: date) -> WeeklyProgressResponse:
        start_date = end_date - timedelta(days=6)

        target = await self.user_repository.get_nutrition_target(user_id)
        target_calories = target.calories if target else 2200
        target_protein = target.protein_g if target else 150
        target_water = target.water_ml if target else 2500

        weights = await self.daily_repository.list_weights_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        entries = await self.food_repository.list_entries_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        water_rows = await self.daily_repository.list_water_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        steps_rows = await self.daily_repository.list_steps_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        sleep_rows = await self.daily_repository.list_sleep_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        workout_rows = await self.daily_repository.list_workouts_between(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        period_days = (end_date - start_date).days + 1

        return WeeklyProgressResponse(
            end_date=end_date,
            start_date=start_date,
            days=period_days,
            weight=self._weight_summary(weights),
            nutrition=self._nutrition_summary(entries, target_calories, target_protein),
            hydration=self._hydration_summary(water_rows, target_water),
            steps=self._steps_summary(steps_rows),
            sleep=self._sleep_summary(sleep_rows),
            training=self._training_summary(workout_rows, period_days),
        )

    def _weight_summary(self, rows) -> WeightSummary:
        entries = [WeightEntry(date=row.date, weight_kg=row.weight_kg) for row in rows]
        if not entries:
            return WeightSummary(entries=entries)

        values = [entry.weight_kg for entry in entries]
        average = round(sum(values) / len(values), 2)
        trend = round(values[-1] - values[0], 2)
        return WeightSummary(
            entries=entries,
            seven_day_average_kg=average,
            trend_kg=trend,
            rate_of_change_kg_per_week=round(trend, 2),
        )

    def _nutrition_summary(self, entries, target_calories: int, target_protein: int) -> NutritionSummary:
        logged_days = {entry.date for entry in entries}
        if not logged_days:
            return NutritionSummary()
        average_calories = round(sum(entry.calories for entry in entries) / len(logged_days))
        average_protein = round(sum(entry.protein_g for entry in entries) / len(logged_days))
        return NutritionSummary(
            days_logged=len(logged_days),
            average_calories=average_calories,
            average_protein_g=average_protein,
            protein_adherence_percent=_adherence_percent(average_protein, target_protein),
        )

    def _hydration_summary(self, rows, target_water: int) -> HydrationSummary:
        if not rows:
            return HydrationSummary()
        average_water = round(sum(row.amount_ml for row in rows) / len(rows))
        return HydrationSummary(
            days_logged=len(rows),
            average_water_ml=average_water,
            water_adherence_percent=_adherence_percent(average_water, target_water),
        )

    def _steps_summary(self, rows) -> StepsSummary:
        if not rows:
            return StepsSummary()
        average_steps = round(sum(row.steps for row in rows) / len(rows))
        return StepsSummary(days_logged=len(rows), average_steps=average_steps)

    def _sleep_summary(self, rows) -> SleepSummary:
        if not rows:
            return SleepSummary()
        average_minutes = round(sum(row.duration_minutes for row in rows) / len(rows))
        return SleepSummary(days_logged=len(rows), average_sleep_minutes=average_minutes)

    def _training_summary(self, rows, period_days: int) -> TrainingSummary:
        workout_days = {row.date for row in rows}
        if not workout_days:
            return TrainingSummary()
        return TrainingSummary(
            workout_days=len(workout_days),
            training_adherence_percent=round(len(workout_days) / period_days * 100),
        )


def _adherence_percent(actual: int, target: int) -> int:
    if target <= 0:
        return 0
    return round(min(actual, target) / target * 100)
