from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profile import get_current_user_id
from app.db.session import get_db_session
from app.schemas.food import FoodCreate, FoodEntryWithFoodCreate, FoodEntryWithFoodResponse, FoodResponse
from app.services.food_service import FoodService

router = APIRouter(tags=["foods"])


async def get_food_service(
    db: AsyncSession = Depends(get_db_session),
) -> FoodService:
    return FoodService(db)


@router.post("/foods", response_model=FoodResponse)
async def create_food(
    payload: FoodCreate,
    user_id: str = Depends(get_current_user_id),
    service: FoodService = Depends(get_food_service),
) -> FoodResponse:
    response = await service.create_food(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/food-entries", response_model=FoodEntryWithFoodResponse)
async def create_food_entry_from_existing_food(
    payload: FoodEntryWithFoodCreate,
    user_id: str = Depends(get_current_user_id),
    service: FoodService = Depends(get_food_service),
) -> FoodEntryWithFoodResponse:
    try:
        response = await service.create_entry_from_food(user_id=user_id, payload=payload)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    await service.session.commit()
    return response
