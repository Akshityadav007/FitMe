from __future__ import annotations

import json
from datetime import date

import openai
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError

from app.ai.client import LLMClient
from app.ai.coach_context import build_coach_context
from app.ai.prompts import (
    WEEKLY_REVIEW_PROMPT,
    system_prompt_with_context,
    weekly_review_user_prompt,
)
from app.ai.tools import TOOL_ARG_MODELS, TOOL_DEFINITIONS
from app.repositories.coach_repository import CoachRepository
from app.repositories.daily_repository import DailyRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.user_repository import UserRepository
from app.schemas.coach import CoachChatRequest, CoachChatResponse, CoachMessageResponse
from app.schemas.recommendation import RecommendationRequest
from app.services.daily_service import DailyService
from app.services.recommendation_service import RecommendationService

MAX_TOOL_ROUNDS = 6
HISTORY_LIMIT = 20


class CoachAIResponse(BaseModel):
    reply: str
    recommendation: str | None = None
    reason: str | None = None
    remaining_calories: int | None = None
    remaining_protein_g: int | None = None
    uncertainty: bool = False
    uncertainty_reason: str | None = None
    suggested_action: str | None = None


class CoachService:
    def __init__(self, session, llm_client: LLMClient) -> None:
        self.session = session
        self.llm_client = llm_client
        self.repository = CoachRepository(session)
        self.user_repository = UserRepository(session)
        self.food_repository = FoodRepository(session)
        self.daily_repository = DailyRepository(session)
        self.menu_repository = MenuRepository(session)

    async def chat(self, *, user_id: str, payload: CoachChatRequest) -> CoachChatResponse:
        conversation = await self._get_or_create_conversation(user_id, payload.conversation_id)
        history = await self.repository.list_messages(conversation_id=conversation.id, limit=HISTORY_LIMIT)

        target_date = date.today()
        context = await build_coach_context(self.session, user_id, target_date)
        system_prompt = system_prompt_with_context(context)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(
            {"role": message.role, "content": message.content} for message in history
        )
        messages.append({"role": "user", "content": payload.message})

        try:
            final_content = await self._run_tool_loop(messages, user_id)
        except openai.AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI coach authentication failed. Check the API key configuration.",
            ) from exc
        except openai.RateLimitError as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI coach is rate limited. Please try again shortly.",
            ) from exc
        except openai.OpenAIError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI coach is temporarily unavailable.",
            ) from exc

        parsed = _parse_ai_response(final_content)
        await self.repository.add_message(
            conversation_id=conversation.id,
            role="user",
            content=payload.message,
        )
        await self.repository.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=parsed.reply,
        )

        if parsed.recommendation:
            await self.repository.create_recommendation(
                user_id=user_id,
                date=target_date,
                meal_type="coach_chat",
                recommendation=parsed.recommendation,
                reason=parsed.reason or "",
                remaining_calories=parsed.remaining_calories or 0,
                remaining_protein_g=parsed.remaining_protein_g or 0,
                uncertainty=parsed.uncertainty,
                suggested_action=parsed.suggested_action or "",
            )

        messages_response = [
            CoachMessageResponse(role=message.role, content=message.content)
            for message in await self.repository.list_messages(
                conversation_id=conversation.id,
                limit=HISTORY_LIMIT,
            )
        ]

        return CoachChatResponse(
            conversation_id=conversation.id,
            reply=parsed.reply,
            recommendation=parsed.recommendation,
            reason=parsed.reason,
            remaining_calories=parsed.remaining_calories,
            remaining_protein_g=parsed.remaining_protein_g,
            uncertainty=parsed.uncertainty,
            uncertainty_reason=parsed.uncertainty_reason,
            suggested_action=parsed.suggested_action,
            messages=messages_response,
        )

    async def review_week(self, *, user_id: str, end_date: date) -> str:
        from app.services.progress_service import WeeklyProgressService

        aggregates = await WeeklyProgressService(self.session).aggregate(
            user_id=user_id, end_date=end_date
        )
        messages = [
            {"role": "system", "content": WEEKLY_REVIEW_PROMPT},
            {
                "role": "user",
                "content": weekly_review_user_prompt(aggregates.model_dump(mode="json")),
            },
        ]
        result = await self.llm_client.complete(messages=messages)
        return result.content or ""

    async def _get_or_create_conversation(self, user_id: str, conversation_id: str | None):
        if conversation_id is not None:
            conversation = await self.repository.get_conversation(conversation_id=conversation_id)
            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )
            if conversation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not own this conversation.",
                )
            return conversation
        return await self.repository.create_conversation(user_id=user_id)

    async def _run_tool_loop(self, messages: list[dict], user_id: str) -> str:
        for _ in range(MAX_TOOL_ROUNDS):
            result = await self.llm_client.complete(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                response_format={"type": "json_object"},
            )
            if not result.tool_calls:
                return result.content or ""

            messages.append(
                {
                    "role": "assistant",
                    "content": result.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.name,
                                "arguments": json.dumps(call.arguments),
                            },
                        }
                        for call in result.tool_calls
                    ],
                }
            )
            for call in result.tool_calls:
                outcome = await self._execute_tool(user_id=user_id, name=call.name, arguments=call.arguments)
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": outcome}
                )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI coach exceeded the maximum number of tool steps.",
        )

    async def _execute_tool(self, *, user_id: str, name: str, arguments: dict) -> str:
        model = TOOL_ARG_MODELS.get(name)
        if model is None:
            return _tool_error(f"Unknown tool '{name}'.")
        try:
            args = model(**arguments)
        except ValidationError as exc:
            return _tool_error(f"Invalid arguments for '{name}': {exc!s}")
        return await self._dispatch_tool(user_id, name, args)

    async def _dispatch_tool(self, user_id: str, name: str, args: BaseModel) -> str:
        from app.services.menu_service import MenuService

        if name == "get_user_profile":
            profile = await self.user_repository.get_profile(user_id)
            target = await self.user_repository.get_nutrition_target(user_id)
            return _tool_result({
                "profile": {
                    "age": profile.age if profile else None,
                    "sex": profile.sex if profile else None,
                    "height_cm": profile.height_cm if profile else None,
                    "weight_kg": profile.weight_kg if profile else None,
                    "goal": profile.goal if profile else None,
                    "activity_level": profile.activity_level if profile else None,
                    "dietary_preferences": profile.dietary_preferences if profile else None,
                },
                "targets": {
                    "calories": target.calories if target else 2200,
                    "protein_g": target.protein_g if target else 150,
                    "carbs_g": target.carbs_g if target else 250,
                    "fat_g": target.fat_g if target else 60,
                    "water_ml": target.water_ml if target else 2500,
                },
            })

        if name == "get_today_summary":
            summary = await DailyService(self.session).get_daily_summary(
                user_id=user_id,
                target_date=_date_arg(args),
            )
            return _tool_result(summary.model_dump(mode="json"))

        if name == "get_remaining_targets":
            return _tool_result(await self._remaining_targets(user_id, _date_arg(args)))

        if name == "get_today_menu":
            service = MenuService(self.session)
            items = await service.list_items_for_date(user_id=user_id, target_date=_date_arg(args))
            return _tool_result([item.model_dump(mode="json") for item in items])

        if name == "get_recent_weight_trend":
            return _tool_result(await self._weight_trend(user_id, _days_arg(args)))

        if name == "get_recent_training":
            return _tool_result(await self._training(user_id, _days_arg(args)))

        if name == "get_recent_sleep":
            return _tool_result(await self._sleep(user_id, _days_arg(args)))

        if name == "log_food":
            row = await self.food_repository.create_food_entry(
                user_id=user_id,
                date=_date_arg(args),
                meal_type=args.meal_type,
                food_name=args.food_name,
                calories=args.calories,
                protein_g=args.protein_g,
                carbs_g=args.carbs_g,
                fat_g=args.fat_g,
                notes=args.notes,
            )
            return _tool_result({"logged": row.food_name, "calories": row.calories})

        if name == "log_water":
            row = await self.daily_repository.upsert_water(
                user_id=user_id,
                target_date=_date_arg(args),
                amount_ml=args.amount_ml,
            )
            return _tool_result({"logged_water_ml": row.amount_ml})

        if name == "log_weight":
            row = await self.daily_repository.upsert_weight(
                user_id=user_id,
                target_date=_date_arg(args),
                weight_kg=args.weight_kg,
            )
            return _tool_result({"logged_weight_kg": row.weight_kg})

        if name == "log_sleep":
            row = await self.daily_repository.upsert_sleep(
                user_id=user_id,
                target_date=_date_arg(args),
                duration_minutes=args.duration_minutes,
                quality=args.quality,
            )
            return _tool_result({"logged_sleep_minutes": row.duration_minutes})

        if name == "log_workout":
            row = await self.daily_repository.create_workout(
                user_id=user_id,
                target_date=_date_arg(args),
                name=args.name,
                duration_minutes=args.duration_minutes,
                notes=args.notes,
            )
            return _tool_result({"logged_workout": row.name})

        if name == "recommend_meal":
            recommendation = await RecommendationService(self.session).recommend(
                user_id=user_id,
                payload=RecommendationRequest(date=_date_arg(args), meal_type=args.meal_type),
            )
            await self.repository.create_recommendation(
                user_id=user_id,
                date=recommendation.date,
                meal_type=recommendation.meal_type,
                recommendation=(
                    recommendation.recommendation.name if recommendation.recommendation else "None"
                ),
                reason=recommendation.reason,
                remaining_calories=recommendation.remaining.calories,
                remaining_protein_g=recommendation.remaining.protein_g,
                uncertainty=recommendation.uncertainty,
                suggested_action=recommendation.suggested_action,
            )
            return _tool_result(recommendation.model_dump(mode="json"))

        return _tool_error(f"Tool '{name}' is not implemented.")

    async def _remaining_targets(self, user_id: str, target_date: date) -> dict:
        target = await self.user_repository.get_nutrition_target(user_id)
        entries = await self.food_repository.list_entries_for_date(user_id=user_id, target_date=target_date)
        consumed = {
            "calories": sum(entry.calories for entry in entries),
            "protein_g": sum(entry.protein_g for entry in entries),
            "carbs_g": sum(entry.carbs_g for entry in entries),
            "fat_g": sum(entry.fat_g for entry in entries),
        }
        targets = {
            "calories": target.calories if target else 2200,
            "protein_g": target.protein_g if target else 150,
            "carbs_g": target.carbs_g if target else 250,
            "fat_g": target.fat_g if target else 60,
        }
        remaining = {
            key: max(0, targets[key] - consumed.get(key, 0)) for key in targets
        }
        return {"targets": targets, "consumed": consumed, "remaining": remaining}

    async def _weight_trend(self, user_id: str, days: int) -> dict:
        from datetime import timedelta

        start = date.today() - timedelta(days=days)
        rows = await self.daily_repository.list_weights_since(user_id=user_id, start_date=start)
        entries = [{"date": str(row.date), "weight_kg": row.weight_kg} for row in rows]
        avg = round(sum(row.weight_kg for row in rows) / len(rows), 2) if rows else None
        return {"days": days, "entries": entries, "seven_day_avg_kg": avg}

    async def _training(self, user_id: str, days: int) -> dict:
        from datetime import timedelta

        start = date.today() - timedelta(days=days)
        rows = await self.daily_repository.list_workouts_since(user_id=user_id, start_date=start)
        return {
            "days": days,
            "sessions": [
                {"date": str(row.date), "name": row.name, "duration_minutes": row.duration_minutes}
                for row in rows
            ],
        }

    async def _sleep(self, user_id: str, days: int) -> dict:
        from datetime import timedelta

        start = date.today() - timedelta(days=days)
        rows = await self.daily_repository.list_sleep_since(user_id=user_id, start_date=start)
        return {
            "days": days,
            "entries": [
                {"date": str(row.date), "duration_minutes": row.duration_minutes, "quality": row.quality}
                for row in rows
            ],
        }


def _date_arg(args) -> date:
    value = getattr(args, "date", None)
    return value or date.today()


def _days_arg(args) -> int:
    return int(getattr(args, "days", 14))


def _tool_result(data: dict) -> str:
    return json.dumps(data, default=str)


def _tool_error(message: str) -> str:
    return json.dumps({"error": message})


def _parse_ai_response(content: str) -> CoachAIResponse:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return CoachAIResponse(reply=content)
    if not isinstance(data, dict):
        return CoachAIResponse(reply=content)
    try:
        return CoachAIResponse(**data)
    except ValidationError:
        return CoachAIResponse(reply=str(data.get("reply") or content))
