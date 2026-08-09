from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profile import get_current_user_id
from app.db.session import get_db_session
from app.schemas.recommendation import RecommendationRequest, StructuredCoachResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


async def get_recommendation_service(
    db: AsyncSession = Depends(get_db_session),
) -> RecommendationService:
    return RecommendationService(db)


@router.post("", response_model=StructuredCoachResponse)
async def recommend_meal(
    payload: RecommendationRequest,
    user_id: str = Depends(get_current_user_id),
    service: RecommendationService = Depends(get_recommendation_service),
) -> StructuredCoachResponse:
    response = await service.recommend(user_id=user_id, payload=payload)
    await service.session.commit()
    return response
