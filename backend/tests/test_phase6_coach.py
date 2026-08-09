import json
from datetime import date

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.ai.client import LLMResult, ToolCall
from app.api.v1.coach import get_llm_client
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


class FakeLLMClient:
    def __init__(self, script):
        self.model = "test-model"
        self.script = list(script)
        self.seen_messages: list[list[dict]] = []

    async def complete(self, *, messages, tools=None, response_format=None):
        self.seen_messages.append(messages)
        if not self.script:
            return LLMResult(content="No more scripted steps.")
        return self.script.pop(0)


def final_result_json() -> str:
    return json.dumps(
        {
            "reply": "Chicken salad is the best pick for your remaining targets.",
            "recommendation": "Chicken salad",
            "reason": "High protein, fits your remaining calories.",
            "remaining_calories": 350,
            "remaining_protein_g": 20,
            "uncertainty": False,
            "uncertainty_reason": None,
            "suggested_action": "Order the chicken salad for lunch.",
        }
    )


async def register_user(client: AsyncClient, email: str) -> tuple[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secure-password-123"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return payload["access_token"], payload["user"]["id"]


@pytest.mark.asyncio
async def test_get_llm_client_requires_api_key(monkeypatch) -> None:
    class FakeSettings:
        openai_api_key: str | None = None
        openai_model: str = "test-model"

    monkeypatch.setattr("app.api.v1.coach.get_settings", lambda: FakeSettings())
    with pytest.raises(HTTPException) as exc:
        await get_llm_client()
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_coach_chat_tool_loop_and_persistence() -> None:
    engine = await reset_database()
    fake = FakeLLMClient(
        [
            LLMResult(
                content=None,
                tool_calls=[
                    ToolCall(id="call-1", name="get_today_summary", arguments={"date": today_iso})
                ],
            ),
            LLMResult(content=final_result_json()),
        ]
    )
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "coach1@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.post(
                "/api/v1/coach/chat",
                json={"message": "What should I eat for lunch?"},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["conversation_id"]
            assert payload["reply"] == "Chicken salad is the best pick for your remaining targets."
            assert payload["recommendation"] == "Chicken salad"
            assert payload["remaining_calories"] == 350
            roles = [message["role"] for message in payload["messages"]]
            assert roles == ["user", "assistant"]

            assert fake.seen_messages, "LLM was never called"
            first_user_prompt = fake.seen_messages[0]
            assert first_user_prompt[0]["role"] == "system"
            assert "Current application state" in first_user_prompt[0]["content"]
            tool_message = fake.seen_messages[1]
            roles_in_loop = [message["role"] for message in tool_message]
            assert "tool" in roles_in_loop

            second = await client.post(
                "/api/v1/coach/chat",
                json={
                    "message": "What should I eat for lunch?",
                    "conversation_id": payload["conversation_id"],
                },
                headers=headers,
            )
            assert second.status_code == 200, second.text
            second_payload = second.json()
            assert second_payload["conversation_id"] == payload["conversation_id"]
            assert len(second_payload["messages"]) == 4
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_coach_chat_persists_recommendation() -> None:
    engine = await reset_database()
    fake = FakeLLMClient(
        [
            LLMResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="log_food",
                        arguments={
                            "date": today_iso,
                            "meal_type": "lunch",
                            "food_name": "Chicken rice bowl",
                            "calories": 620,
                            "protein_g": 45,
                            "carbs_g": 55,
                            "fat_g": 20,
                        },
                    )
                ],
            ),
            LLMResult(content=final_result_json()),
        ]
    )
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "coach2@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.post(
                "/api/v1/coach/chat",
                json={"message": "Log my lunch and recommend something for dinner."},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            payload = response.json()
            assert payload["recommendation"] == "Chicken salad"

            summary = await client.get(
                "/api/v1/daily/summary",
                params={"date": today_iso},
                headers=headers,
            )
            assert summary.status_code == 200, summary.text
            assert summary.json()["food_calories"] == 620
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_coach_chat_invalid_tool_arguments_are_rejected() -> None:
    engine = await reset_database()
    fake = FakeLLMClient(
        [
            LLMResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="log_food",
                        arguments={"date": today_iso, "food_name": "Missing values"},
                    )
                ],
            ),
            LLMResult(content=final_result_json()),
        ]
    )
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "coach3@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.post(
                "/api/v1/coach/chat",
                json={"message": "Log food without all values."},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            error_message = fake.seen_messages[1]
            tool_contents = [
                message["content"]
                for message in error_message
                if message["role"] == "tool"
            ]
            assert any("Invalid arguments" in content for content in tool_contents)
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_coach_chat_exceeds_max_tool_rounds() -> None:
    engine = await reset_database()
    fake = FakeLLMClient(
        [
            LLMResult(content=None, tool_calls=[ToolCall(id=f"call-{i}", name="get_user_profile", arguments={})])
            for i in range(10)
        ]
    )
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "coach4@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.post(
                "/api/v1/coach/chat",
                json={"message": "Keep calling tools forever."},
                headers=headers,
            )
            assert response.status_code == 502
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_coach_chat_rejects_foreign_conversation() -> None:
    engine = await reset_database()
    fake = FakeLLMClient([LLMResult(content=final_result_json())])
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token_a, _ = await register_user(client, "coach5a@example.com")
            headers_a = {"Authorization": f"Bearer {token_a}"}
            token_b, _ = await register_user(client, "coach5b@example.com")
            headers_b = {"Authorization": f"Bearer {token_b}"}

            first = await client.post(
                "/api/v1/coach/chat",
                json={"message": "hi"},
                headers=headers_a,
            )
            conversation_id = first.json()["conversation_id"]

            second = await client.post(
                "/api/v1/coach/chat",
                json={"message": "hi", "conversation_id": conversation_id},
                headers=headers_b,
            )
            assert second.status_code == 403
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.asyncio
async def test_weekly_review_uses_mocked_llm() -> None:
    engine = await reset_database()
    fake = FakeLLMClient([LLMResult(content="Solid week overall. Keep it up.")])
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            token, _ = await register_user(client, "coach6@example.com")
            headers = {"Authorization": f"Bearer {token}"}

            end_date = date.today().isoformat()
            response = await client.post(
                "/api/v1/progress/weekly/review",
                json={"end_date": end_date},
                headers=headers,
            )
            assert response.status_code == 200, response.text
            assert response.json()["review"] == "Solid week overall. Keep it up."
            assert fake.seen_messages[0][0]["content"].startswith("You are FitMe's weekly review coach")
    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
