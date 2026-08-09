from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class MacroTotals(BaseModel):
    calories: int = Field(ge=0)
    protein_g: int = Field(ge=0)
    carbs_g: int = Field(ge=0)
    fat_g: int = Field(ge=0)


class RecommendationRequest(BaseModel):
    date: date
    meal_type: str = "lunch"


class RecommendedItem(BaseModel):
    menu_item_id: str
    name: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    confidence: float = Field(ge=0, le=1)


class StructuredCoachResponse(BaseModel):
    date: date
    meal_type: str
    targets: MacroTotals
    consumed: MacroTotals
    remaining: MacroTotals
    recommendation: RecommendedItem | None = None
    alternatives: list[RecommendedItem] = Field(default_factory=list)
    reason: str
    uncertainty: bool = False
    uncertainty_reason: str | None = None
    suggested_action: str
