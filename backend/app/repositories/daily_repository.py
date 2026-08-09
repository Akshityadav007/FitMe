from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_log import DailyWaterEntry, DailyWeightEntry


class DailyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_weight_for_date(self, *, user_id: str, target_date: date) -> DailyWeightEntry | None:
        result = await self.session.execute(
            select(DailyWeightEntry).where(
                DailyWeightEntry.user_id == user_id,
                DailyWeightEntry.date == target_date,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_weight(self, *, user_id: str, target_date: date, weight_kg: float) -> DailyWeightEntry:
        row = await self.get_weight_for_date(user_id=user_id, target_date=target_date)
        if row is None:
            row = DailyWeightEntry(user_id=user_id, date=target_date, weight_kg=weight_kg)
            self.session.add(row)
            await self.session.flush()
            return row

        row.weight_kg = weight_kg
        await self.session.flush()
        return row

    async def get_water_for_date(self, *, user_id: str, target_date: date) -> DailyWaterEntry | None:
        result = await self.session.execute(
            select(DailyWaterEntry).where(
                DailyWaterEntry.user_id == user_id,
                DailyWaterEntry.date == target_date,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_water(self, *, user_id: str, target_date: date, amount_ml: int) -> DailyWaterEntry:
        row = await self.get_water_for_date(user_id=user_id, target_date=target_date)
        if row is None:
            row = DailyWaterEntry(user_id=user_id, date=target_date, amount_ml=amount_ml)
            self.session.add(row)
            await self.session.flush()
            return row

        row.amount_ml = amount_ml
        await self.session.flush()
        return row
