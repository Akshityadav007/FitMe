from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MenuImageCreate(BaseModel):
    source: str = "camera"
    status: str = "pending"
    image_url: str


class MenuImageResponse(MenuImageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


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
