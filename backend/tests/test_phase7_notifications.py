from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.services.notification_service import NotificationService


async def reset_database() -> AsyncEngine:
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url), echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return engine


async def register_user(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secure-password-123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["user"]["id"]


@pytest.mark.asyncio
async def test_notification_preferences_defaults_and_update() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register = await client.post(
                "/api/v1/auth/register",
                json={"email": "prefs@example.com", "password": "secure-password-123"},
            )
            token = register.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            defaults = await client.get("/api/v1/notifications/preferences", headers=headers)
            assert defaults.status_code == 200, defaults.text
            payload = defaults.json()
            assert payload["hydration_enabled"] is True
            assert payload["quiet_hours_start"] == "22:00:00"
            assert payload["quiet_hours_end"] == "07:00:00"

            updated = await client.put(
                "/api/v1/notifications/preferences",
                json={"hydration_enabled": False, "end_of_day_enabled": False},
                headers=headers,
            )
            assert updated.status_code == 200, updated.text
            assert updated.json()["hydration_enabled"] is False
            assert updated.json()["end_of_day_enabled"] is False
            assert updated.json()["protein_enabled"] is True

            persisted = await client.get("/api/v1/notifications/preferences", headers=headers)
            assert persisted.json()["hydration_enabled"] is False
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_quiet_hours_suppresses_notifications() -> None:
    engine = await reset_database()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        user_id = "quiet-user"
        from app.models.user import User

        session.add(User(id=user_id, email="quiet@example.com", password_hash="x"))
        await session.flush()

        service = NotificationService(session)
        now = datetime(2026, 1, 15, 23, 30, tzinfo=UTC)
        created = await service.check(user_id=user_id, now=now)
        assert created == []
    await engine.dispose()


@pytest.mark.asyncio
async def test_hydration_notification_and_dedupe() -> None:
    engine = await reset_database()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        from app.models.user import User

        user_id = "hyd-user"
        session.add(User(id=user_id, email="hyd@example.com", password_hash="x"))
        await session.flush()

        service = NotificationService(session)
        now = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)

        first = await service.check(user_id=user_id, now=now)
        assert any(notification.category == "hydration" for notification in first)

        second = await service.check(user_id=user_id, now=now)
        hydration_again = [
            notification for notification in second if notification.category == "hydration"
        ]
        assert hydration_again == []
    await engine.dispose()


@pytest.mark.asyncio
async def test_end_of_day_notification_generation() -> None:
    engine = await reset_database()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        from app.models.user import User

        user_id = "eod-user"
        session.add(User(id=user_id, email="eod@example.com", password_hash="x"))
        await session.flush()

        service = NotificationService(session)
        now = datetime(2026, 1, 15, 21, 30, tzinfo=UTC)
        created = await service.check(user_id=user_id, now=now)
        categories = [notification.category for notification in created]
        assert "end_of_day" in categories
    await engine.dispose()


@pytest.mark.asyncio
async def test_notifications_list_and_mark_read() -> None:
    engine = await reset_database()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        from app.models.user import User

        user_id = "list-user"
        session.add(User(id=user_id, email="list@example.com", password_hash="x"))
        await session.flush()

        service = NotificationService(session)
        now = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
        created = await service.check(user_id=user_id, now=now)
        assert created, "expected some notifications"
        notification_id = created[0].id

        listed = await service.list(user_id=user_id)
        assert any(notification.id == notification_id for notification in listed)

        read = await service.mark_read(notification_id=notification_id, user_id=user_id)
        assert read is not None
        assert read.read_at is not None

        not_found = await service.mark_read(
            notification_id="does-not-exist", user_id=user_id
        )
        assert not_found is None
    await engine.dispose()
