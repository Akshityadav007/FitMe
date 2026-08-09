from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.auth import AuthResponse, UserLoginRequest, UserRegisterRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(db)


@router.post("/register", response_model=AuthResponse)
async def register_user(
    payload: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
) -> AuthResponse:
    profile_data = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "goal": payload.goal,
        "activity_level": payload.activity_level,
        "dietary_preferences": payload.dietary_preferences,
    }
    response = await service.register_user(
        email=payload.email,
        password=payload.password,
        **profile_data,
    )
    await service.session.commit()
    return response


@router.post("/login", response_model=AuthResponse)
async def login_user(
    payload: UserLoginRequest,
    service: UserService = Depends(get_user_service),
) -> AuthResponse:
    response = await service.login_user(email=payload.email, password=payload.password)
    await service.session.commit()
    return response
