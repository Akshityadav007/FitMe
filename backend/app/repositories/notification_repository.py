from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationPreference


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_preferences(self, user_id: str) -> NotificationPreference | None:
        result = await self.session.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert_preferences(
        self,
        *,
        user_id: str,
        **preference_data: object,
    ) -> NotificationPreference:
        preferences = await self.get_preferences(user_id)
        if preferences is None:
            preferences = NotificationPreference(user_id=user_id, **preference_data)
            self.session.add(preferences)
            await self.session.flush()
            return preferences

        for key, value in preference_data.items():
            if value is not None:
                setattr(preferences, key, value)
        await self.session.flush()
        return preferences

    async def create_notification(
        self,
        *,
        user_id: str,
        category: str,
        title: str,
        body: str,
        day_key: str,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            category=category,
            title=title,
            body=body,
            day_key=day_key,
        )
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def has_sent_today(self, *, user_id: str, category: str, day_key: str) -> bool:
        result = await self.session.execute(
            select(Notification.id)
            .where(
                Notification.user_id == user_id,
                Notification.category == category,
                Notification.day_key == day_key,
            )
            .limit(1)
        )
        return result.first() is not None

    async def list_notifications(self, *, user_id: str, limit: int = 30) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_read(self, *, notification_id: str, user_id: str) -> Notification | None:
        from datetime import datetime, timezone

        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification is not None:
            notification.read_at = datetime.now(timezone.utc)
            await self.session.flush()
        return notification
