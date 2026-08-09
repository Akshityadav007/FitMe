from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.daily import (
    DailySummaryResponse,
    FoodEntryCreate,
    FoodEntryResponse,
    SleepEntryCreate,
    SleepEntryResponse,
    StepsEntryCreate,
    StepsEntryResponse,
    WaterEntryCreate,
    WaterEntryResponse,
    WeightEntryCreate,
    WeightEntryResponse,
    WorkoutSessionCreate,
    WorkoutSessionResponse,
)
from app.services.daily_service import DailyService
from app.api.v1.profile import get_current_user_id

router = APIRouter(prefix="/daily", tags=["daily"])


async def get_daily_service(
    db: AsyncSession = Depends(get_db_session),
) -> DailyService:
    return DailyService(db)


@router.post("/weight", response_model=WeightEntryResponse)
async def create_weight(
    payload: WeightEntryCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> WeightEntryResponse:
    response = await service.record_weight(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/water", response_model=WaterEntryResponse)
async def create_water(
    payload: WaterEntryCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> WaterEntryResponse:
    response = await service.record_water(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/food", response_model=FoodEntryResponse)
async def create_food_entry(
    payload: FoodEntryCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> FoodEntryResponse:
    response = await service.add_food_entry(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.get("/summary", response_model=DailySummaryResponse)
async def get_summary(
    date: date = Query(..., alias="date"),
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> DailySummaryResponse:
    return await service.get_daily_summary(user_id=user_id, target_date=date)


@router.post("/steps", response_model=StepsEntryResponse)
async def create_steps(
    payload: StepsEntryCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> StepsEntryResponse:
    response = await service.record_steps(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/sleep", response_model=SleepEntryResponse)
async def create_sleep(
    payload: SleepEntryCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> SleepEntryResponse:
    response = await service.record_sleep(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/workout", response_model=WorkoutSessionResponse)
async def create_workout(
    payload: WorkoutSessionCreate,
    user_id: str = Depends(get_current_user_id),
    service: DailyService = Depends(get_daily_service),
) -> WorkoutSessionResponse:
    response = await service.record_workout(user_id=user_id, payload=payload)
    await service.session.commit()
    return response
