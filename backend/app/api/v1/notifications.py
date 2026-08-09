from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profile import get_current_user_id
from app.db.session import get_db_session
from app.schemas.notification import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def get_notification_service(
    db: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(db)


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_preferences(
    user_id: str = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferencesResponse:
    return await service.get_preferences(user_id)


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_preferences(
    payload: NotificationPreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferencesResponse:
    response = await service.update_preferences(user_id, payload)
    await service.session.commit()
    return response


@router.post("/check", response_model=list[NotificationResponse])
async def check_notifications(
    user_id: str = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationResponse]:
    response = await service.check(user_id=user_id)
    await service.session.commit()
    return response


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = Query(default=30, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationResponse]:
    return await service.list(user_id=user_id, limit=limit)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    response = await service.mark_read(notification_id=notification_id, user_id=user_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )
    await service.session.commit()
    return response
