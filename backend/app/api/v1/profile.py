from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.schemas.profile import UserProfileResponse, UserProfileUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/profile", tags=["profile"])
security = HTTPBearer()


async def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(db)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> str:
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    user = await UserService(db).repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user_id


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    response = await service.get_profile(user_id)
    await service.session.commit()
    return response


@router.put("/me", response_model=UserProfileResponse)
async def update_profile(
    payload: UserProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    response = await service.update_profile(user_id, payload)
    await service.session.commit()
    return response
