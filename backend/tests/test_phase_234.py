from datetime import date, datetime, timedelta, timezone

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
async def test_daily_logging_and_summary() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "daily@example.com",
                    "password": "secure-password-123",
                    "first_name": "Daily",
                    "last_name": "Logger",
                },
            )
            token = register.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            today = date.today().isoformat()

            weight = await client.post(
                "/api/v1/daily/weight",
                json={"date": today, "weight_kg": 73.2},
                headers=headers,
            )
            assert weight.status_code == 200, weight.text

            water = await client.post(
                "/api/v1/daily/water",
                json={"date": today, "amount_ml": 750},
                headers=headers,
            )
            assert water.status_code == 200, water.text

            food = await client.post(
                "/api/v1/daily/food",
                json={
                    "date": today,
                    "meal_type": "lunch",
                    "food_name": "Chicken rice bowl",
                    "calories": 620,
                    "protein_g": 45,
                    "carbs_g": 55,
                    "fat_g": 20,
                },
                headers=headers,
            )
            assert food.status_code == 200, food.text

            summary = await client.get(
                "/api/v1/daily/summary",
                params={"date": today},
                headers=headers,
            )
            assert summary.status_code == 200, summary.text
            payload = summary.json()
            assert payload["water_ml"] == 750
            assert payload["food_calories"] == 620
            assert payload["steps"] == 0
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_food_database_and_menu_extraction_round_trip() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "menu@example.com",
                    "password": "secure-password-123",
                    "first_name": "Menu",
                    "last_name": "Test",
                },
            )
            token = register.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            food = await client.post(
                "/api/v1/foods",
                json={
                    "name": "Greek yogurt",
                    "serving_size_g": 170,
                    "calories": 150,
                    "protein_g": 17,
                    "carbs_g": 8,
                    "fat_g": 5,
                },
                headers=headers,
            )
            assert food.status_code == 200, food.text
            food_id = food.json()["id"]

            entry = await client.post(
                "/api/v1/food-entries",
                json={
                    "food_id": food_id,
                    "date": date.today().isoformat(),
                    "meal_type": "breakfast",
                    "quantity_g": 170,
                    "notes": "plain greek yogurt",
                },
                headers=headers,
            )
            assert entry.status_code == 200, entry.text

            menu_image = await client.post(
                "/api/v1/menu-images",
                json={
                    "source": "camera",
                    "status": "pending",
                    "image_url": "https://example.com/menu.png",
                },
                headers=headers,
            )
            assert menu_image.status_code == 200, menu_image.text
            menu_id = menu_image.json()["id"]

            item = await client.post(
                f"/api/v1/menu-images/{menu_id}/items",
                json={
                    "name": "Chicken wrap",
                    "estimated_calories": 420,
                    "estimated_protein_g": 30,
                    "estimated_carbs_g": 40,
                    "estimated_fat_g": 15,
                    "confidence": 0.86,
                },
                headers=headers,
            )
            assert item.status_code == 200, item.text
            assert item.json()["name"] == "Chicken wrap"
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
