from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_log import (
    DailyStepsEntry,
    DailyWaterEntry,
    DailyWeightEntry,
    SleepEntry,
    WorkoutSession,
)


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

    async def list_weights_since(self, *, user_id: str, start_date: date) -> list[DailyWeightEntry]:
        result = await self.session.execute(
            select(DailyWeightEntry)
            .where(DailyWeightEntry.user_id == user_id, DailyWeightEntry.date >= start_date)
            .order_by(DailyWeightEntry.date.asc())
        )
        return list(result.scalars().all())

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

    async def get_steps_for_date(self, *, user_id: str, target_date: date) -> DailyStepsEntry | None:
        result = await self.session.execute(
            select(DailyStepsEntry).where(
                DailyStepsEntry.user_id == user_id,
                DailyStepsEntry.date == target_date,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_steps(self, *, user_id: str, target_date: date, steps: int) -> DailyStepsEntry:
        row = await self.get_steps_for_date(user_id=user_id, target_date=target_date)
        if row is None:
            row = DailyStepsEntry(user_id=user_id, date=target_date, steps=steps)
            self.session.add(row)
            await self.session.flush()
            return row

        row.steps = steps
        await self.session.flush()
        return row

    async def get_sleep_for_date(self, *, user_id: str, target_date: date) -> SleepEntry | None:
        result = await self.session.execute(
            select(SleepEntry).where(
                SleepEntry.user_id == user_id,
                SleepEntry.date == target_date,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_sleep(
        self,
        *,
        user_id: str,
        target_date: date,
        bed_time=None,
        wake_time=None,
        duration_minutes: int,
        quality: int | None = None,
        source: str = "manual",
    ) -> SleepEntry:
        row = await self.get_sleep_for_date(user_id=user_id, target_date=target_date)
        if row is None:
            row = SleepEntry(
                user_id=user_id,
                date=target_date,
                bed_time=bed_time,
                wake_time=wake_time,
                duration_minutes=duration_minutes,
                quality=quality,
                source=source,
            )
            self.session.add(row)
            await self.session.flush()
            return row

        row.bed_time = bed_time
        row.wake_time = wake_time
        row.duration_minutes = duration_minutes
        row.quality = quality
        await self.session.flush()
        return row

    async def list_sleep_since(self, *, user_id: str, start_date: date) -> list[SleepEntry]:
        result = await self.session.execute(
            select(SleepEntry)
            .where(SleepEntry.user_id == user_id, SleepEntry.date >= start_date)
            .order_by(SleepEntry.date.asc())
        )
        return list(result.scalars().all())

    async def create_workout(
        self,
        *,
        user_id: str,
        target_date: date,
        name: str,
        start_time=None,
        end_time=None,
        duration_minutes: int | None = None,
        notes: str | None = None,
    ) -> WorkoutSession:
        session = WorkoutSession(
            user_id=user_id,
            date=target_date,
            name=name,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            notes=notes,
        )
        self.session.add(session)
        await self.session.flush()
        return session

    async def list_workouts_since(self, *, user_id: str, start_date: date) -> list[WorkoutSession]:
        result = await self.session.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id, WorkoutSession.date >= start_date)
            .order_by(WorkoutSession.date.asc())
        )
        return list(result.scalars().all())

    async def list_weights_between(self, *, user_id: str, start_date: date, end_date: date) -> list[DailyWeightEntry]:
        result = await self.session.execute(
            select(DailyWeightEntry)
            .where(
                DailyWeightEntry.user_id == user_id,
                DailyWeightEntry.date >= start_date,
                DailyWeightEntry.date <= end_date,
            )
            .order_by(DailyWeightEntry.date.asc())
        )
        return list(result.scalars().all())

    async def list_water_between(self, *, user_id: str, start_date: date, end_date: date) -> list[DailyWaterEntry]:
        result = await self.session.execute(
            select(DailyWaterEntry)
            .where(
                DailyWaterEntry.user_id == user_id,
                DailyWaterEntry.date >= start_date,
                DailyWaterEntry.date <= end_date,
            )
            .order_by(DailyWaterEntry.date.asc())
        )
        return list(result.scalars().all())

    async def list_steps_between(self, *, user_id: str, start_date: date, end_date: date) -> list[DailyStepsEntry]:
        result = await self.session.execute(
            select(DailyStepsEntry)
            .where(
                DailyStepsEntry.user_id == user_id,
                DailyStepsEntry.date >= start_date,
                DailyStepsEntry.date <= end_date,
            )
            .order_by(DailyStepsEntry.date.asc())
        )
        return list(result.scalars().all())

    async def list_sleep_between(self, *, user_id: str, start_date: date, end_date: date) -> list[SleepEntry]:
        result = await self.session.execute(
            select(SleepEntry)
            .where(
                SleepEntry.user_id == user_id,
                SleepEntry.date >= start_date,
                SleepEntry.date <= end_date,
            )
            .order_by(SleepEntry.date.asc())
        )
        return list(result.scalars().all())

    async def list_workouts_between(self, *, user_id: str, start_date: date, end_date: date) -> list[WorkoutSession]:
        result = await self.session.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= start_date,
                WorkoutSession.date <= end_date,
            )
            .order_by(WorkoutSession.date.asc())
        )
        return list(result.scalars().all())
