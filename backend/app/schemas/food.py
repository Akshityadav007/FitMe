from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class FoodCreate(BaseModel):
    name: str
    serving_size_g: float = Field(gt=0)
    calories: int = Field(ge=0)
    protein_g: int = Field(ge=0)
    carbs_g: int = Field(ge=0)
    fat_g: int = Field(ge=0)


class FoodResponse(FoodCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class FoodEntryWithFoodCreate(BaseModel):
    food_id: str
    date: date
    meal_type: str = "meal"
    quantity_g: float = Field(gt=0)
    notes: str | None = None


class FoodEntryWithFoodResponse(FoodEntryWithFoodCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    food_name: str
    calories: int = 0
    protein_g: int = 0
    carbs_g: int = 0
    fat_g: int = 0
