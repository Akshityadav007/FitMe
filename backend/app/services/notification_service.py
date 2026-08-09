from __future__ import annotations

from datetime import UTC, datetime, time

from app.repositories.food_repository import FoodRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
)

DEFAULT_PREFERENCES = {
    "hydration_enabled": True,
    "protein_enabled": True,
    "meal_enabled": True,
    "end_of_day_enabled": True,
    "quiet_hours_start": time(22, 0),
    "quiet_hours_end": time(7, 0),
}

HYDRATION_WINDOW_START = time(8, 0)
HYDRATION_WINDOW_END = time(21, 0)
PROTEIN_WINDOW_END = time(20, 0)
MEAL_WINDOW_START = time(11, 0)
MEAL_WINDOW_END = time(14, 30)
END_OF_DAY_TIME = time(21, 0)

MIN_PROTEIN_GAP_G = 20


def _is_quiet(now: datetime, start: time, end: time) -> bool:
    current = now.time()
    if start <= end:
        return start <= current < end
    return current >= start or current < end


class NotificationService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = NotificationRepository(session)
        self.user_repository = UserRepository(session)
        self.food_repository = FoodRepository(session)
        self.menu_repository = MenuRepository(session)

    async def get_preferences(self, user_id: str) -> NotificationPreferencesResponse:
        preferences = await self.repository.get_preferences(user_id)
        if preferences is None:
            return NotificationPreferencesResponse(user_id=user_id, **DEFAULT_PREFERENCES)
        return self._to_response(preferences)

    async def update_preferences(
        self,
        user_id: str,
        payload: NotificationPreferencesUpdate,
    ) -> NotificationPreferencesResponse:
        data = payload.model_dump(exclude_unset=True)
        preferences = await self.repository.upsert_preferences(user_id=user_id, **data)
        return self._to_response(preferences)

    async def check(self, *, user_id: str, now: datetime | None = None) -> list[NotificationResponse]:
        """Generate due notifications for the user, respecting preferences, quiet
        hours, and per-day deduplication so notifications never spam the user."""
        now = now or datetime.now(UTC)
        preferences = await self.repository.get_preferences(user_id)
        if preferences is None:
            preferences = await self.repository.upsert_preferences(user_id=user_id, **DEFAULT_PREFERENCES)

        if _is_quiet(now, preferences.quiet_hours_start, preferences.quiet_hours_end):
            return []

        day_key = now.strftime("%Y-%m-%d")
        target_date = now.date()
        created: list[NotificationResponse] = []

        if preferences.hydration_enabled and await self._hydration_due(user_id, now, target_date, day_key):
            created.append(await self._send_hydration(user_id, target_date, day_key))

        if preferences.protein_enabled and await self._protein_due(user_id, now, target_date, day_key):
            created.append(await self._send_protein(user_id, target_date, day_key))

        if preferences.meal_enabled and await self._meal_due(user_id, now, target_date, day_key):
            created.append(await self._send_meal(user_id, target_date, day_key))

        if preferences.end_of_day_enabled and await self._end_of_day_due(user_id, now, day_key):
            created.append(await self._send_end_of_day(user_id, target_date, day_key))

        return created

    async def list(self, *, user_id: str, limit: int = 30) -> list[NotificationResponse]:
        rows = await self.repository.list_notifications(user_id=user_id, limit=limit)
        return [self._notification_response(row) for row in rows]

    async def mark_read(self, *, notification_id: str, user_id: str) -> NotificationResponse | None:
        row = await self.repository.mark_read(notification_id=notification_id, user_id=user_id)
        if row is None:
            return None
        return self._notification_response(row)

    async def _hydration_due(self, user_id: str, now: datetime, target_date, day_key: str) -> bool:
        if not (HYDRATION_WINDOW_START <= now.time() < HYDRATION_WINDOW_END):
            return False
        if await self.repository.has_sent_today(user_id=user_id, category="hydration", day_key=day_key):
            return False
        from app.repositories.daily_repository import DailyRepository

        daily = DailyRepository(self.session)
        water = await daily.get_water_for_date(user_id=user_id, target_date=target_date)
        target = await self.user_repository.get_nutrition_target(user_id)
        target_ml = target.water_ml if target else 2500
        consumed_ml = water.amount_ml if water else 0
        return consumed_ml < target_ml

    async def _send_hydration(self, user_id: str, target_date, day_key: str) -> NotificationResponse:
        from app.repositories.daily_repository import DailyRepository

        daily = DailyRepository(self.session)
        water = await daily.get_water_for_date(user_id=user_id, target_date=target_date)
        target = await self.user_repository.get_nutrition_target(user_id)
        target_ml = target.water_ml if target else 2500
        consumed_ml = water.amount_ml if water else 0
        remaining_ml = max(0, target_ml - consumed_ml)
        suggested_ml = min(remaining_ml, 500)
        row = await self.repository.create_notification(
            user_id=user_id,
            category="hydration",
            title="Hydration",
            body=f"You've had {consumed_ml} ml against a {target_ml} ml target. Have another {suggested_ml} ml.",
            day_key=day_key,
        )
        return self._notification_response(row)

    async def _protein_due(self, user_id: str, now: datetime, target_date, day_key: str) -> bool:
        if now.time() >= PROTEIN_WINDOW_END:
            return False
        if await self.repository.has_sent_today(user_id=user_id, category="protein", day_key=day_key):
            return False
        return await self._remaining_protein(user_id, target_date) >= MIN_PROTEIN_GAP_G

    async def _send_protein(self, user_id: str, target_date, day_key: str) -> NotificationResponse:
        target = await self.user_repository.get_nutrition_target(user_id)
        target_protein = target.protein_g if target else 150
        consumed = await self._protein_consumed(user_id, target_date)
        remaining = max(0, target_protein - consumed)
        row = await self.repository.create_notification(
            user_id=user_id,
            category="protein",
            title="Protein status",
            body=f"You're at {consumed} g protein and need about {remaining} g more. Make your next meal protein-heavy.",
            day_key=day_key,
        )
        return self._notification_response(row)

    async def _meal_due(self, user_id: str, now: datetime, target_date, day_key: str) -> bool:
        if not (MEAL_WINDOW_START <= now.time() < MEAL_WINDOW_END):
            return False
        if await self.repository.has_sent_today(user_id=user_id, category="meal", day_key=day_key):
            return False
        target = await self.user_repository.get_nutrition_target(user_id)
        consumed = await self._calories_consumed(user_id, target_date)
        target_calories = target.calories if target else 2200
        if target_calories - consumed <= 0:
            return False
        menu = await self.menu_repository.list_items_for_date(user_id=user_id, target_date=target_date)
        return len(menu) > 0

    async def _send_meal(self, user_id: str, target_date, day_key: str) -> NotificationResponse:
        target = await self.user_repository.get_nutrition_target(user_id)
        consumed = await self._calories_consumed(user_id, target_date)
        remaining = max(0, (target.calories if target else 2200) - consumed)
        row = await self.repository.create_notification(
            user_id=user_id,
            category="meal",
            title="Lunch recommendation",
            body=f"You have about {remaining} kcal left today. Ask the coach what to eat from today's menu.",
            day_key=day_key,
        )
        return self._notification_response(row)

    async def _end_of_day_due(self, user_id: str, now: datetime, day_key: str) -> bool:
        if now.time() < END_OF_DAY_TIME:
            return False
        return not await self.repository.has_sent_today(
            user_id=user_id, category="end_of_day", day_key=day_key
        )

    async def _send_end_of_day(self, user_id: str, target_date, day_key: str) -> NotificationResponse:
        from app.repositories.daily_repository import DailyRepository

        daily = DailyRepository(self.session)
        target = await self.user_repository.get_nutrition_target(user_id)
        calories = await self._calories_consumed(user_id, target_date)
        protein = await self._protein_consumed(user_id, target_date)
        water_row = await daily.get_water_for_date(user_id=user_id, target_date=target_date)
        water = water_row.amount_ml if water_row else 0

        target_calories = target.calories if target else 2200
        target_protein = target.protein_g if target else 150
        target_water = target.water_ml if target else 2500
        row = await self.repository.create_notification(
            user_id=user_id,
            category="end_of_day",
            title="End of day",
            body=(
                f"Calories: {calories}/{target_calories}. "
                f"Protein: {protein}/{target_protein} g. "
                f"Water: {water}/{target_water} ml."
            ),
            day_key=day_key,
        )
        return self._notification_response(row)

    async def _calories_consumed(self, user_id: str, target_date) -> int:
        entries = await self.food_repository.list_entries_for_date(
            user_id=user_id, target_date=target_date
        )
        return sum(entry.calories for entry in entries)

    async def _protein_consumed(self, user_id: str, target_date) -> int:
        entries = await self.food_repository.list_entries_for_date(
            user_id=user_id, target_date=target_date
        )
        return sum(entry.protein_g for entry in entries)

    async def _remaining_protein(self, user_id: str, target_date) -> int:
        target = await self.user_repository.get_nutrition_target(user_id)
        target_protein = target.protein_g if target else 150
        return max(0, target_protein - await self._protein_consumed(user_id, target_date))

    def _to_response(self, preferences) -> NotificationPreferencesResponse:
        return NotificationPreferencesResponse(
            user_id=preferences.user_id,
            hydration_enabled=preferences.hydration_enabled,
            protein_enabled=preferences.protein_enabled,
            meal_enabled=preferences.meal_enabled,
            end_of_day_enabled=preferences.end_of_day_enabled,
            quiet_hours_start=preferences.quiet_hours_start,
            quiet_hours_end=preferences.quiet_hours_end,
        )

    def _notification_response(self, row) -> NotificationResponse:
        return NotificationResponse(
            id=row.id,
            user_id=row.user_id,
            category=row.category,
            title=row.title,
            body=row.body,
            created_at=row.created_at,
            read_at=row.read_at,
        )
