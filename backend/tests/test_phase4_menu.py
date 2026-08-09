from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.ai.vision import VisionMenuItem
from app.api.v1.menu_images import get_vision_extractor
from app.core.config import get_settings
from app.db.base import Base
from app.main import app

today_iso = date.today().isoformat()


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


def fake_extractor(items: list[VisionMenuItem]):
    async def extract(image_bytes, content_type):
        return items

    return extract


@pytest.mark.asyncio
async def test_vision_parse_clamps_and_validates() -> None:
    from app.ai.vision import parse_vision_response

    parsed = parse_vision_response(
        '{"items": [{"name": "Chicken wrap", "estimated_calories": 420,'
        '"estimated_protein_g": 30, "estimated_carbs_g": -5, "estimated_fat_g": 15,'
        '"confidence": 1.7}]}'
    )
    assert len(parsed) == 1
    item = parsed[0]
    assert item.name == "Chicken wrap"
    assert item.estimated_calories == 420
    assert item.estimated_carbs_g == 0
    assert item.confidence == 1.0

    assert parse_vision_response("not json") == []
    assert parse_vision_response('{"items": "nope"}') == []
    assert parse_vision_response('{"items": [{"name": "  "}]}') == []


@pytest.mark.asyncio
async def test_menu_upload_process_and_confirm_flow() -> None:
    engine = await reset_database()
    app.dependency_overrides[get_vision_extractor] = lambda: fake_extractor(
        [
            VisionMenuItem(
                name="Chicken wrap",
                estimated_calories=420,
                estimated_protein_g=30,
                estimated_carbs_g=40,
                estimated_fat_g=15,
                confidence=0.86,
            )
        ]
    )
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "menuflow@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            upload = await client.post(
                "/api/v1/menu-images/upload",
                headers={**headers, "Content-Type": "image/jpeg"},
                content=b"\xff\xd8\xff\xe0fake-jpeg-data",
            )
            assert upload.status_code == 200, upload.text
            menu_image = upload.json()
            menu_id = menu_image["id"]
            assert menu_image["status"] == "pending"
            assert menu_image["image_url"].startswith("/uploads/")

            process = await client.post(
                f"/api/v1/menu-images/{menu_id}/process",
                headers=headers,
            )
            assert process.status_code == 200, process.text
            payload = process.json()
            assert payload["status"] == "extracted"
            assert len(payload["items"]) == 1
            item = payload["items"][0]
            assert item["name"] == "Chicken wrap"

            confirm = await client.post(
                f"/api/v1/menu-items/{item['id']}/confirm",
                headers=headers,
                json={"date": today_iso, "meal_type": "lunch", "quantity_g": 100},
            )
            assert confirm.status_code == 200, confirm.text
            entry = confirm.json()
            assert entry["food_name"] == "Chicken wrap"
            assert entry["calories"] == 420
            assert entry["protein_g"] == 30

            detail = await client.get(f"/api/v1/menu-images/{menu_id}", headers=headers)
            assert detail.status_code == 200
            assert len(detail.json()["items"]) == 1
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_confirm_reuses_trusted_food_for_repeated_item() -> None:
    engine = await reset_database()
    app.dependency_overrides[get_vision_extractor] = lambda: fake_extractor(
        [
            VisionMenuItem(
                name="Greek yogurt",
                estimated_calories=50,
                estimated_protein_g=1,
                estimated_carbs_g=1,
                estimated_fat_g=0,
                confidence=0.4,
            )
        ]
    )
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "reuse@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            food = await client.post(
                "/api/v1/foods",
                headers=headers,
                json={
                    "name": "Greek yogurt",
                    "serving_size_g": 170,
                    "calories": 150,
                    "protein_g": 17,
                    "carbs_g": 8,
                    "fat_g": 5,
                },
            )
            assert food.status_code == 200, food.text
            food_id = food.json()["id"]

            upload = await client.post(
                "/api/v1/menu-images/upload",
                headers={**headers, "Content-Type": "image/jpeg"},
                content=b"fake-jpeg-data",
            )
            menu_id = upload.json()["id"]

            process = await client.post(f"/api/v1/menu-images/{menu_id}/process", headers=headers)
            item = process.json()["items"][0]
            assert item["name"] == "Greek yogurt"

            confirm = await client.post(
                f"/api/v1/menu-items/{item['id']}/confirm",
                headers=headers,
                json={"date": today_iso, "meal_type": "breakfast", "quantity_g": 170},
            )
            assert confirm.status_code == 200, confirm.text
            entry = confirm.json()
            # Trusted nutrition must win over the low-confidence extraction.
            assert entry["calories"] == 150
            assert entry["protein_g"] == 17
            assert entry["food_id"] == food_id
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_content_type() -> None:
    engine = await reset_database()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "badupload@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            upload = await client.post(
                "/api/v1/menu-images/upload",
                headers={**headers, "Content-Type": "text/html"},
                content=b"<html></html>",
            )
            assert upload.status_code == 422
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
