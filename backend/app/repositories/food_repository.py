from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Food, FoodEntry


class FoodRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_food(self, *, user_id: str, **data: object) -> Food:
        food = Food(user_id=user_id, **data)
        self.session.add(food)
        await self.session.flush()
        return food

    async def get_food_by_id(self, *, food_id: str) -> Food | None:
        result = await self.session.execute(select(Food).where(Food.id == food_id))
        return result.scalar_one_or_none()

    async def create_food_entry(self, *, user_id: str, **data: object) -> FoodEntry:
        entry = FoodEntry(user_id=user_id, **data)
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_entries_for_date(self, *, user_id: str, target_date: date) -> list[FoodEntry]:
        result = await self.session.execute(
            select(FoodEntry)
            .where(FoodEntry.user_id == user_id, FoodEntry.date == target_date)
            .order_by(FoodEntry.created_at.desc())
        )
        return list(result.scalars().all())
