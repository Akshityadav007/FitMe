from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MenuImageCreate(BaseModel):
    source: str = "camera"
    status: str = "pending"
    image_url: str


class MenuImageResponse(MenuImageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class MenuImageDetailResponse(MenuImageResponse):
    items: list[MenuImageItemResponse] = []


class MenuImageItemCreate(BaseModel):
    name: str
    estimated_calories: int = Field(ge=0)
    estimated_protein_g: int = Field(ge=0)
    estimated_carbs_g: int = Field(ge=0)
    estimated_fat_g: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class MenuImageItemResponse(MenuImageItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    menu_image_id: str


class MenuItemConfirmCreate(BaseModel):
    date: date
    meal_type: str = "meal"
    quantity_g: float = Field(gt=0)
    notes: str | None = None


class MenuImageProcessResponse(BaseModel):
    id: str
    status: str
    items: list[MenuImageItemResponse]
