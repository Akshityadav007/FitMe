from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.models.menu_image import MenuImage, MenuImageItem
from app.schemas.recommendation import MacroTotals, RecommendedItem
from app.services.recommendation_service import (
    parse_dietary_preferences,
    score_menu_item,
)


def _item(name: str, calories: int, protein_g: int, carbs_g: int, fat_g: int, confidence: float = 0.9) -> RecommendedItem:
    return RecommendedItem(
        menu_item_id=f"id-{name}",
        name=name,
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        confidence=confidence,
    )


def test_parse_dietary_preferences_eggetarian_chicken_not_spicy() -> None:
    prefs = parse_dietary_preferences("Eggetarian + chicken; Spicy food not preferred")
    assert prefs.avoids_spicy is True
    assert prefs.is_vegetarian is False
    assert prefs.avoids_eggs is False
    assert prefs.avoids_chicken is False


def test_parse_dietary_preferences_vegetarian_no_eggs() -> None:
    prefs = parse_dietary_preferences("Vegetarian, no eggs")
    assert prefs.is_vegetarian is True
    assert prefs.avoids_eggs is True
    assert prefs.avoids_chicken is True


def test_parse_dietary_preferences_empty() -> None:
    prefs = parse_dietary_preferences(None)
    assert not prefs.avoids_spicy
    assert not prefs.is_vegetarian
    assert not prefs.avoids_eggs
    assert not prefs.avoids_chicken


def test_score_prefers_high_protein_non_spicy() -> None:
    remaining = MacroTotals(calories=1000, protein_g=50, carbs_g=150, fat_g=40)
    prefs = parse_dietary_preferences("Eggetarian + chicken; Spicy food not preferred")

    chicken = score_menu_item(_item("Chicken wrap", 450, 35, 40, 15), remaining, prefs)
    spicy = score_menu_item(_item("Spicy noodles", 450, 12, 80, 15), remaining, prefs)

    assert chicken.score > spicy.score
    assert any("may be spicy" in reason for reason in spicy.reasons)
    assert all("may be spicy" not in reason for reason in chicken.reasons)


def test_score_prefers_balanced_item_over_macro_overshoot() -> None:
    remaining = MacroTotals(calories=500, protein_g=10, carbs_g=30, fat_g=10)
    prefs = parse_dietary_preferences(None)

    balanced = score_menu_item(_item("Balanced", 450, 10, 25, 8), remaining, prefs)
    heavy = score_menu_item(_item("Heavy carbs", 450, 10, 120, 40), remaining, prefs)

    assert balanced.score > heavy.score


def test_score_is_deterministic() -> None:
    remaining = MacroTotals(calories=1000, protein_g=50, carbs_g=150, fat_g=40)
    prefs = parse_dietary_preferences(None)

    first = score_menu_item(_item("Paneer rice", 500, 22, 60, 20), remaining, prefs)
    second = score_menu_item(_item("Paneer rice", 500, 22, 60, 20), remaining, prefs)

    assert first.score == second.score
    assert first.reasons == second.reasons


def test_score_penalizes_items_when_target_met() -> None:
    remaining = MacroTotals(calories=0, protein_g=10, carbs_g=20, fat_g=5)
    prefs = parse_dietary_preferences(None)

    scored = score_menu_item(_item("Chicken wrap", 420, 30, 40, 15), remaining, prefs)

    assert scored.score < 0
    assert any("already met today's calorie target" in reason for reason in scored.reasons)


def test_penalty_for_vegetarian_avoids_meat() -> None:
    remaining = MacroTotals(calories=1000, protein_g=50, carbs_g=150, fat_g=40)
    prefs = parse_dietary_preferences("Vegetarian")

    paneer = score_menu_item(_item("Paneer rice", 450, 22, 60, 20), remaining, prefs)
    chicken = score_menu_item(_item("Chicken rice", 450, 35, 40, 15), remaining, prefs)

    assert paneer.score > chicken.score
    assert any("outside your vegetarian preference" in reason for reason in chicken.reasons)


async def reset_database() -> AsyncEngine:
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url), echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return engine


async def _register_user(client: AsyncClient, email: str) -> tuple[str, str, dict]:
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secure-password-123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert register.status_code == 200, register.text
    body = register.json()
    return body["user"]["id"], body["access_token"], {"Authorization": f"Bearer {body['access_token']}"}


@pytest.mark.asyncio
async def test_recommendation_grounded_in_daily_state() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            _, token, headers = await _register_user(client, "recommend@example.com")
            profile = await client.put(
                "/api/v1/profile/me",
                json={"dietary_preferences": "Eggetarian + chicken; Spicy food not preferred"},
                headers=headers,
            )
            assert profile.status_code == 200, profile.text

            targets = await client.put(
                "/api/v1/nutrition-targets/me",
                json={
                    "calories": 2350,
                    "protein_g": 175,
                    "carbs_g": 260,
                    "fat_g": 70,
                    "water_ml": 3000,
                    "fiber_g": 30,
                    "sodium_mg": 2000,
                },
                headers=headers,
            )
            assert targets.status_code == 200, targets.text

            today = date.today().isoformat()

            food = await client.post(
                "/api/v1/daily/food",
                json={
                    "date": today,
                    "meal_type": "breakfast",
                    "food_name": "Oats and eggs",
                    "calories": 620,
                    "protein_g": 35,
                    "carbs_g": 55,
                    "fat_g": 18,
                },
                headers=headers,
            )
            assert food.status_code == 200, food.text

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

            for item in (
                {"name": "Chicken wrap", "estimated_calories": 450, "estimated_protein_g": 35, "estimated_carbs_g": 40, "estimated_fat_g": 15, "confidence": 0.9},
                {"name": "Spicy chili noodles", "estimated_calories": 480, "estimated_protein_g": 12, "estimated_carbs_g": 80, "estimated_fat_g": 15, "confidence": 0.9},
            ):
                created = await client.post(
                    f"/api/v1/menu-images/{menu_id}/items",
                    json=item,
                    headers=headers,
                )
                assert created.status_code == 200, created.text

            available = await client.get(
                "/api/v1/menu-items",
                params={"date": today},
                headers=headers,
            )
            assert available.status_code == 200, available.text
            assert len(available.json()) == 2

            resp = await client.post(
                "/api/v1/recommendations",
                json={"date": today, "meal_type": "lunch"},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            payload = resp.json()

            assert payload["remaining"]["calories"] == 2350 - 620
            assert payload["remaining"]["protein_g"] == 175 - 35
            assert payload["remaining"]["carbs_g"] == 260 - 55
            assert payload["remaining"]["fat_g"] == 70 - 18
            assert payload["recommendation"]["name"] == "Chicken wrap"
            assert payload["recommendation"]["confidence"] == 0.9
            assert payload["uncertainty"] is False
            assert payload["uncertainty_reason"] is None
            assert "Chicken wrap" in payload["suggested_action"]
            assert "1730 kcal" in payload["reason"]
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_recommendation_no_menu_returns_uncertain_response() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            _, token, headers = await _register_user(client, "nomenu@example.com")
            today = date.today().isoformat()

            resp = await client.post(
                "/api/v1/recommendations",
                json={"date": today, "meal_type": "lunch"},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            payload = resp.json()
            assert payload["recommendation"] is None
            assert payload["uncertainty"] is True
            assert "No office menu is available" in payload["reason"]
            assert payload["remaining"]["calories"] == 2200
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_recommendation_at_or_over_calorie_target() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            _, token, headers = await _register_user(client, "overtarget@example.com")

            targets = await client.put(
                "/api/v1/nutrition-targets/me",
                json={"calories": 500, "protein_g": 150, "carbs_g": 250, "fat_g": 60},
                headers=headers,
            )
            assert targets.status_code == 200, targets.text

            today = date.today().isoformat()
            food = await client.post(
                "/api/v1/daily/food",
                json={
                    "date": today,
                    "meal_type": "lunch",
                    "food_name": "Large lunch",
                    "calories": 600,
                    "protein_g": 40,
                    "carbs_g": 60,
                    "fat_g": 20,
                },
                headers=headers,
            )
            assert food.status_code == 200, food.text

            resp = await client.post(
                "/api/v1/recommendations",
                json={"date": today, "meal_type": "lunch"},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            payload = resp.json()
            assert payload["remaining"]["calories"] == 0
            assert payload["recommendation"] is None
            assert payload["uncertainty"] is True
            assert "calorie target" in payload["reason"]
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_recommendation_ignores_menu_from_other_days() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            user_id, _, headers = await _register_user(client, "stale@example.com")

            today = date.today().isoformat()
            async with AsyncSession(engine) as session:
                stale = MenuImage(
                    user_id=user_id,
                    source="camera",
                    status="pending",
                    image_url="https://example.com/stale.png",
                    created_at=datetime.now(timezone.utc) - timedelta(days=1),
                )
                session.add(stale)
                await session.flush()
                session.add(
                    MenuImageItem(
                        menu_image_id=stale.id,
                        name="Yesterday's curry",
                        estimated_calories=500,
                        estimated_protein_g=30,
                        estimated_carbs_g=50,
                        estimated_fat_g=15,
                        confidence=0.9,
                    )
                )
                await session.commit()

            resp = await client.post(
                "/api/v1/recommendations",
                json={"date": today, "meal_type": "lunch"},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            payload = resp.json()
            assert payload["recommendation"] is None
            assert payload["uncertainty"] is True
            assert "No office menu is available" in payload["reason"]
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
