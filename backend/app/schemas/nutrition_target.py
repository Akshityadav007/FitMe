from pydantic import BaseModel, ConfigDict, Field


class NutritionTargetBase(BaseModel):
    calories: int = Field(default=2200, ge=0)
    protein_g: int = Field(default=150, ge=0)
    carbs_g: int = Field(default=250, ge=0)
    fat_g: int = Field(default=60, ge=0)
    water_ml: int = Field(default=2500, ge=0)
    fiber_g: int = Field(default=30, ge=0)
    sodium_mg: int = Field(default=2000, ge=0)


class NutritionTargetUpdate(NutritionTargetBase):
    pass


class NutritionTargetResponse(NutritionTargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
