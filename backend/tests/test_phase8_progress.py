from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.main import app

TODAY = date.today()


async def reset_database() -> AsyncEngine:
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url), echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return engine


async def register_user(client: AsyncClient, email: str) -> tuple[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secure-password-123"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return payload["access_token"], payload["user"]["id"]


async def seed_day(
    client: AsyncClient,
    headers: dict,
    day: date,
    *,
    calories: int,
    protein_g: int,
    water_ml: int,
    steps: int,
    sleep_minutes: int,
    workout: bool,
    weight_kg: float | None = None,
) -> None:
    day_iso = day.isoformat()
    food = await client.post(
        "/api/v1/daily/food",
        json={
            "date": day_iso,
            "meal_type": "lunch",
            "food_name": "Test meal",
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": 50,
            "fat_g": 20,
        },
        headers=headers,
    )
    assert food.status_code == 200, food.text

    water = await client.post(
        "/api/v1/daily/water",
        json={"date": day_iso, "amount_ml": water_ml},
        headers=headers,
    )
    assert water.status_code == 200, water.text

    steps_resp = await client.post(
        "/api/v1/daily/steps",
        json={"date": day_iso, "steps": steps},
        headers=headers,
    )
    assert steps_resp.status_code == 200, steps_resp.text

    sleep = await client.post(
        "/api/v1/daily/sleep",
        json={"date": day_iso, "duration_minutes": sleep_minutes, "quality": 4},
        headers=headers,
    )
    assert sleep.status_code == 200, sleep.text

    if workout:
        workout_resp = await client.post(
            "/api/v1/daily/workout",
            json={"date": day_iso, "name": "Upper body", "duration_minutes": 60},
            headers=headers,
        )
        assert workout_resp.status_code == 200, workout_resp.text

    if weight_kg is not None:
        weight = await client.post(
            "/api/v1/daily/weight",
            json={"date": day_iso, "weight_kg": weight_kg},
            headers=headers,
        )
        assert weight.status_code == 200, weight.text


@pytest.mark.asyncio
async def test_weekly_progress_aggregates() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "progress@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            seed_days = [
                (TODAY - timedelta(days=6), 2200, 150, 2500, 10000, 420, True, 73.0),
                (TODAY - timedelta(days=5), 2200, 150, 2500, 8000, 420, True, None),
                (TODAY - timedelta(days=4), 1800, 120, 2000, 6000, 300, False, 72.8),
            ]
            for day, cal, prot, water, steps, sleep_min, workout, weight in seed_days:
                await seed_day(
                    client,
                    headers,
                    day,
                    calories=cal,
                    protein_g=prot,
                    water_ml=water,
                    steps=steps,
                    sleep_minutes=sleep_min,
                    workout=workout,
                    weight_kg=weight,
                )

            response = await client.get(
                "/api/v1/progress/weekly",
                params={"end_date": TODAY.isoformat()},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["days"] == 7
            assert payload["start_date"] == (TODAY - timedelta(days=6)).isoformat()

            nutrition = payload["nutrition"]
            assert nutrition["days_logged"] == 3
            # (2200 + 2200 + 1800) / 3 = 2066.67 -> 2067
            assert nutrition["average_calories"] == 2067
            assert nutrition["average_protein_g"] == 140

            hydration = payload["hydration"]
            assert hydration["days_logged"] == 3
            assert hydration["average_water_ml"] == 2333
            assert hydration["water_adherence_percent"] == 93

            steps_summary = payload["steps"]
            assert steps_summary["days_logged"] == 3
            assert steps_summary["average_steps"] == 8000

            sleep_summary = payload["sleep"]
            assert sleep_summary["days_logged"] == 3
            assert sleep_summary["average_sleep_minutes"] == 380

            training = payload["training"]
            assert training["workout_days"] == 2
            assert training["training_adherence_percent"] == round(2 / 7 * 100)

            weight = payload["weight"]
            assert len(weight["entries"]) == 2
            assert weight["seven_day_average_kg"] == 72.9
            assert weight["trend_kg"] == -0.2
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_weekly_progress_empty_week() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "empty-progress@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.get(
                "/api/v1/progress/weekly",
                params={"end_date": TODAY.isoformat()},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["nutrition"]["days_logged"] == 0
            assert payload["nutrition"]["average_calories"] is None
            assert payload["weight"]["entries"] == []
            assert payload["weight"]["seven_day_average_kg"] is None
            assert payload["training"]["workout_days"] == 0
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
