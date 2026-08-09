from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, UserSummary
from app.schemas.nutrition_target import NutritionTargetResponse, NutritionTargetUpdate
from app.schemas.profile import UserProfileResponse, UserProfileUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)

    async def register_user(self, *, email: str, password: str, **profile_data: object) -> AuthResponse:
        existing = await self.repository.get_by_email(email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        user = await self.repository.create_user(
            email=email,
            password_hash=hash_password(password),
        )

        profile = await self.repository.create_profile(user_id=user.id, **profile_data)
        self.session.add(profile)
        await self.session.flush()

        target = await self.repository.create_nutrition_target(
            user_id=user.id,
            calories=2200,
            protein_g=150,
            carbs_g=250,
            fat_g=60,
            water_ml=2500,
            fiber_g=30,
            sodium_mg=2000,
        )
        self.session.add(target)
        await self.session.flush()

        access_token = create_access_token(user.id)
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserSummary(
                id=user.id,
                email=user.email,
                first_name=profile.first_name,
                last_name=profile.last_name,
                goal=profile.goal,
                activity_level=profile.activity_level,
                dietary_preferences=profile.dietary_preferences,
            ),
        )

    async def login_user(self, *, email: str, password: str) -> AuthResponse:
        user = await self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        profile = await self.repository.get_profile(user.id)
        access_token = create_access_token(user.id)
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserSummary(
                id=user.id,
                email=user.email,
                first_name=profile.first_name if profile else None,
                last_name=profile.last_name if profile else None,
                goal=profile.goal if profile else None,
                activity_level=profile.activity_level if profile else None,
                dietary_preferences=profile.dietary_preferences if profile else None,
            ),
        )

    async def get_current_user(self, user_id: str) -> User:
        user = await self.repository.get_user_with_profile(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def get_profile(self, user_id: str) -> UserProfileResponse:
        user = await self.get_current_user(user_id)
        profile = user.profile
        if profile is None:
            profile = await self.repository.create_profile(user_id=user.id)

        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            age=profile.age,
            sex=profile.sex,
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            goal=profile.goal,
            activity_level=profile.activity_level,
            dietary_preferences=profile.dietary_preferences,
            notes=profile.notes,
        )

    async def update_profile(self, user_id: str, payload: UserProfileUpdate) -> UserProfileResponse:
        profile_data = payload.model_dump(exclude_unset=True)
        profile = await self.repository.upsert_profile(user_id=user_id, **profile_data)

        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            age=profile.age,
            sex=profile.sex,
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            goal=profile.goal,
            activity_level=profile.activity_level,
            dietary_preferences=profile.dietary_preferences,
            notes=profile.notes,
        )

    async def get_nutrition_targets(self, user_id: str) -> NutritionTargetResponse:
        target = await self.repository.get_nutrition_target(user_id)
        if target is None:
            target = await self.repository.create_nutrition_target(
                user_id=user_id,
                calories=2200,
                protein_g=150,
                carbs_g=250,
                fat_g=60,
                water_ml=2500,
                fiber_g=30,
                sodium_mg=2000,
            )

        return NutritionTargetResponse(
            id=target.id,
            user_id=target.user_id,
            calories=target.calories,
            protein_g=target.protein_g,
            carbs_g=target.carbs_g,
            fat_g=target.fat_g,
            water_ml=target.water_ml,
            fiber_g=target.fiber_g,
            sodium_mg=target.sodium_mg,
        )

    async def update_nutrition_targets(
        self,
        user_id: str,
        payload: NutritionTargetUpdate,
    ) -> NutritionTargetResponse:
        target_data = payload.model_dump(exclude_unset=True)
        target = await self.repository.upsert_nutrition_target(user_id=user_id, **target_data)

        return NutritionTargetResponse(
            id=target.id,
            user_id=target.user_id,
            calories=target.calories,
            protein_g=target.protein_g,
            carbs_g=target.carbs_g,
            fat_g=target.fat_g,
            water_ml=target.water_ml,
            fiber_g=target.fiber_g,
            sodium_mg=target.sodium_mg,
        )
