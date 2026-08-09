from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WeightEntryCreate(BaseModel):
    date: date
    weight_kg: float = Field(gt=0)


class WeightEntryResponse(WeightEntryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class WaterEntryCreate(BaseModel):
    date: date
    amount_ml: int = Field(ge=0)


class WaterEntryResponse(WaterEntryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class FoodEntryCreate(BaseModel):
    date: date
    meal_type: str = "meal"
    food_name: str
    calories: int = Field(ge=0)
    protein_g: int = Field(ge=0)
    carbs_g: int = Field(ge=0)
    fat_g: int = Field(ge=0)
    notes: str | None = None


class FoodEntryResponse(FoodEntryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    food_id: str | None = None
    quantity_g: float | None = None


class DailySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    weight_kg: float | None = None
    water_ml: int = 0
    food_calories: int = 0
    protein_g: int = 0
    carbs_g: int = 0
    fat_g: int = 0
    steps: int = 0
    sleep_minutes: int | None = None
    workout_sessions: int = 0


class StepsEntryCreate(BaseModel):
    date: date
    steps: int = Field(ge=0)


class StepsEntryResponse(StepsEntryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class SleepEntryCreate(BaseModel):
    date: date
    bed_time: datetime | None = None
    wake_time: datetime | None = None
    duration_minutes: int = Field(ge=0)
    quality: int | None = Field(default=None, ge=1, le=5)


class SleepEntryResponse(SleepEntryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    source: str


class WorkoutSessionCreate(BaseModel):
    date: date
    name: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class WorkoutSessionResponse(WorkoutSessionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
