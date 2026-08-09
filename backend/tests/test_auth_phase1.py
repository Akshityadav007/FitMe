import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.main import app


async def reset_database() -> AsyncEngine:
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url), echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return engine


@pytest.mark.asyncio
async def test_register_login_and_profile_flow() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "alice@example.com",
                    "password": "secure-password-123",
                    "first_name": "Alice",
                    "last_name": "Jones",
                    "goal": "recomp",
                    "activity_level": "moderate",
                    "dietary_preferences": "high-protein",
                },
            )

            assert register_response.status_code == 200, register_response.text
            register_body = register_response.json()
            assert register_body["user"]["email"] == "alice@example.com"
            assert "access_token" in register_body

            token = register_body["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            me_response = await client.get("/api/v1/profile/me", headers=headers)
            assert me_response.status_code == 200, me_response.text
            me_body = me_response.json()
            assert me_body["first_name"] == "Alice"
            assert me_body["goal"] == "recomp"

            update_response = await client.put(
                "/api/v1/profile/me",
                json={
                    "first_name": "Alicia",
                    "goal": "fat_loss",
                    "weight_kg": 66.5,
                    "height_cm": 168.0,
                },
                headers=headers,
            )
            assert update_response.status_code == 200, update_response.text
            updated = update_response.json()
            assert updated["first_name"] == "Alicia"
            assert updated["goal"] == "fat_loss"
            assert updated["weight_kg"] == 66.5

            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "alice@example.com",
                    "password": "secure-password-123",
                },
            )
            assert login_response.status_code == 200, login_response.text
            assert login_response.json()["user"]["email"] == "alice@example.com"
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_nutrition_targets_round_trip() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "bobby@example.com",
                    "password": "secure-password-123",
                    "first_name": "Bobby",
                    "last_name": "Dev",
                },
            )
            token = register_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            target_response = await client.get(
                "/api/v1/nutrition-targets/me",
                headers=headers,
            )
            assert target_response.status_code == 200, target_response.text
            assert target_response.json()["calories"] > 0

            update_response = await client.put(
                "/api/v1/nutrition-targets/me",
                json={
                    "calories": 2400,
                    "protein_g": 180,
                    "carbs_g": 260,
                    "fat_g": 70,
                    "water_ml": 3200,
                },
                headers=headers,
            )
            assert update_response.status_code == 200, update_response.text
            payload = update_response.json()
            assert payload["calories"] == 2400
            assert payload["protein_g"] == 180
            assert payload["water_ml"] == 3200
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
