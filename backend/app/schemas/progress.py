from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class WeightEntry(BaseModel):
    date: date
    weight_kg: float


class WeightSummary(BaseModel):
    entries: list[WeightEntry] = Field(default_factory=list)
    seven_day_average_kg: float | None = None
    trend_kg: float | None = None
    rate_of_change_kg_per_week: float | None = None


class NutritionSummary(BaseModel):
    days_logged: int = 0
    average_calories: int | None = None
    average_protein_g: int | None = None
    protein_adherence_percent: int | None = None


class HydrationSummary(BaseModel):
    days_logged: int = 0
    average_water_ml: int | None = None
    water_adherence_percent: int | None = None


class StepsSummary(BaseModel):
    days_logged: int = 0
    average_steps: int | None = None


class SleepSummary(BaseModel):
    days_logged: int = 0
    average_sleep_minutes: int | None = None


class TrainingSummary(BaseModel):
    workout_days: int = 0
    training_adherence_percent: int | None = None


class WeeklyProgressResponse(BaseModel):
    end_date: date
    start_date: date
    days: int
    weight: WeightSummary
    nutrition: NutritionSummary
    hydration: HydrationSummary
    steps: StepsSummary
    sleep: SleepSummary
    training: TrainingSummary


class WeeklyReviewRequest(BaseModel):
    end_date: date


class WeeklyReviewResponse(BaseModel):
    end_date: date
    review: str
