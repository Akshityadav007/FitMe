from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.coach import get_coach_service
from app.api.v1.profile import get_current_user_id
from app.db.session import get_db_session
from app.schemas.progress import (
    WeeklyProgressResponse,
    WeeklyReviewRequest,
    WeeklyReviewResponse,
)
from app.services.coach_service import CoachService
from app.services.progress_service import WeeklyProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


async def get_progress_service(
    db: AsyncSession = Depends(get_db_session),
) -> WeeklyProgressService:
    return WeeklyProgressService(db)


@router.get("/weekly", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    end_date: date = Query(..., alias="end_date"),
    user_id: str = Depends(get_current_user_id),
    service: WeeklyProgressService = Depends(get_progress_service),
) -> WeeklyProgressResponse:
    return await service.aggregate(user_id=user_id, end_date=end_date)


@router.post("/weekly/review", response_model=WeeklyReviewResponse)
async def review_week(
    payload: WeeklyReviewRequest,
    user_id: str = Depends(get_current_user_id),
    service: CoachService = Depends(get_coach_service),
) -> WeeklyReviewResponse:
    review = await service.review_week(user_id=user_id, end_date=payload.end_date)
    await service.session.commit()
    return WeeklyReviewResponse(end_date=payload.end_date, review=review)
