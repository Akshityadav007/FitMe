from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.nutrition_target import NutritionTarget
from app.models.profile import UserProfile
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, *, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_profile(self, user_id: str) -> UserProfile | None:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_profile(self, *, user_id: str, **profile_data: object) -> UserProfile:
        profile = UserProfile(user_id=user_id, **profile_data)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def upsert_profile(self, *, user_id: str, **profile_data: object) -> UserProfile:
        profile = await self.get_profile(user_id)
        if profile is None:
            return await self.create_profile(user_id=user_id, **profile_data)

        for key, value in profile_data.items():
            if value is not None:
                setattr(profile, key, value)
        await self.session.flush()
        return profile

    async def get_nutrition_target(self, user_id: str) -> NutritionTarget | None:
        result = await self.session.execute(
            select(NutritionTarget).where(NutritionTarget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_nutrition_target(
        self,
        *,
        user_id: str,
        **target_data: object,
    ) -> NutritionTarget:
        target = NutritionTarget(user_id=user_id, **target_data)
        self.session.add(target)
        await self.session.flush()
        return target

    async def upsert_nutrition_target(
        self,
        *,
        user_id: str,
        **target_data: object,
    ) -> NutritionTarget:
        target = await self.get_nutrition_target(user_id)
        if target is None:
            return await self.create_nutrition_target(user_id=user_id, **target_data)

        for key, value in target_data.items():
            if value is not None:
                setattr(target, key, value)
        await self.session.flush()
        return target

    async def get_user_with_profile(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile), selectinload(User.nutrition_target))
        )
        return result.scalar_one_or_none()
