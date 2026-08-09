from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.client import LLMClient
from app.ai.provider import AICapability, build_provider_registry
from app.api.v1.profile import get_current_user_id
from app.core.config import get_settings
from app.db.session import get_db_session
from app.schemas.coach import CoachChatRequest, CoachChatResponse
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["coach"])


async def get_llm_client() -> LLMClient:
    settings = get_settings()
    provider = build_provider_registry(settings).get(
        AICapability.COACH,
        preferred=getattr(settings, "ai_coach_provider", "auto"),
    )
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI coach is not configured. Set FITME_OPENAI_API_KEY or "
                "FITME_OPENROUTER_API_KEY in the backend environment."
            ),
        )
    return provider


async def get_coach_service(
    db: AsyncSession = Depends(get_db_session),
    llm_client: LLMClient = Depends(get_llm_client),
) -> CoachService:
    return CoachService(session=db, llm_client=llm_client)


@router.post("/chat", response_model=CoachChatResponse)
async def coach_chat(
    payload: CoachChatRequest,
    user_id: str = Depends(get_current_user_id),
    service: CoachService = Depends(get_coach_service),
) -> CoachChatResponse:
    response = await service.chat(user_id=user_id, payload=payload)
    await service.session.commit()
    return response
