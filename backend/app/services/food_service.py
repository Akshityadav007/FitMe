from __future__ import annotations

from app.repositories.food_repository import FoodRepository
from app.schemas.food import (
    FoodCreate,
    FoodEntryWithFoodCreate,
    FoodEntryWithFoodResponse,
    FoodResponse,
)


class FoodService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = FoodRepository(session)

    async def create_food(self, *, user_id: str, payload: FoodCreate) -> FoodResponse:
        row = await self.repository.create_food(
            user_id=user_id,
            name=payload.name,
            serving_size_g=payload.serving_size_g,
            calories=payload.calories,
            protein_g=payload.protein_g,
            carbs_g=payload.carbs_g,
            fat_g=payload.fat_g,
        )
        return FoodResponse(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            serving_size_g=row.serving_size_g,
            calories=row.calories,
            protein_g=row.protein_g,
            carbs_g=row.carbs_g,
            fat_g=row.fat_g,
        )

    async def create_entry_from_food(self, *, user_id: str, payload: FoodEntryWithFoodCreate) -> FoodEntryWithFoodResponse:
        food = await self.repository.get_food_by_id(food_id=payload.food_id)
        if food is None:
            raise ValueError("Food not found")

        entry = await self.repository.create_food_entry(
            user_id=user_id,
            food_id=food.id,
            date=payload.date,
            meal_type=payload.meal_type,
            food_name=food.name,
            calories=int(food.calories * (payload.quantity_g / food.serving_size_g)),
            protein_g=int(food.protein_g * (payload.quantity_g / food.serving_size_g)),
            carbs_g=int(food.carbs_g * (payload.quantity_g / food.serving_size_g)),
            fat_g=int(food.fat_g * (payload.quantity_g / food.serving_size_g)),
            quantity_g=payload.quantity_g,
            notes=payload.notes,
        )
        return FoodEntryWithFoodResponse(
            id=entry.id,
            user_id=entry.user_id,
            food_id=entry.food_id,
            date=entry.date,
            meal_type=entry.meal_type,
            quantity_g=entry.quantity_g,
            notes=entry.notes,
            food_name=entry.food_name,
            calories=entry.calories,
            protein_g=entry.protein_g,
            carbs_g=entry.carbs_g,
            fat_g=entry.fat_g,
        )
