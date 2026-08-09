from __future__ import annotations

from dataclasses import dataclass

from app.repositories.food_repository import FoodRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.user_repository import UserRepository
from app.schemas.recommendation import (
    MacroTotals,
    RecommendationRequest,
    RecommendedItem,
    StructuredCoachResponse,
)

DEFAULT_TARGETS = MacroTotals(calories=2200, protein_g=150, carbs_g=250, fat_g=60)
CONFIDENCE_THRESHOLD = 0.6
MAX_ALTERNATIVES = 3

SPICY_KEYWORDS = ("spicy", "chili", "chilli")
MEAT_KEYWORDS = ("chicken", "mutton", "beef", "pork", "fish", "lamb", "prawn")
EGG_KEYWORDS = ("egg", "omelet", "omelette")


@dataclass
class DietaryPreferences:
    avoids_spicy: bool = False
    is_vegetarian: bool = False
    avoids_eggs: bool = False
    avoids_chicken: bool = False


@dataclass(frozen=True)
class ScoredCandidate:
    item: RecommendedItem
    score: float
    reasons: tuple[str, ...]


def parse_dietary_preferences(text: str | None) -> DietaryPreferences:
    lowered = (text or "").lower()
    prefs = DietaryPreferences()
    spicy_markers = (
        "spicy food not preferred",
        "not prefer spicy",
        "no spicy",
        "avoid spicy",
        "dislike spicy",
        "dont like spicy",
        "don't like spicy",
    )
    prefs.avoids_spicy = any(marker in lowered for marker in spicy_markers) or (
        "spicy" in lowered and "not" in lowered
    )
    prefs.is_vegetarian = "vegetarian" in lowered or "vegan" in lowered
    prefs.avoids_eggs = any(
        marker in lowered for marker in ("no eggs", "no egg", "eggless", "without egg")
    )
    prefs.avoids_chicken = "no chicken" in lowered or prefs.is_vegetarian
    if "vegan" in lowered:
        prefs.avoids_eggs = True
    return prefs


def _preference_penalty(name: str, prefs: DietaryPreferences) -> tuple[float, tuple[str, ...]]:
    lowered = name.lower()
    penalty = 0.0
    reasons: list[str] = []
    if prefs.avoids_spicy and any(keyword in lowered for keyword in SPICY_KEYWORDS):
        penalty -= 10.0
        reasons.append("It may be spicy, which you prefer to avoid.")
    if prefs.is_vegetarian and any(keyword in lowered for keyword in MEAT_KEYWORDS):
        penalty -= 20.0
        reasons.append("It contains meat, outside your vegetarian preference.")
    if prefs.avoids_chicken and "chicken" in lowered:
        penalty -= 20.0
        reasons.append("It contains chicken, outside your dietary preference.")
    if prefs.avoids_eggs and any(keyword in lowered for keyword in EGG_KEYWORDS):
        penalty -= 20.0
        reasons.append("It contains egg, outside your dietary preference.")
    return penalty, tuple(reasons)


def score_menu_item(
    item: RecommendedItem,
    remaining: MacroTotals,
    prefs: DietaryPreferences,
) -> ScoredCandidate:
    score = 0.0
    reasons: list[str] = []

    if remaining.calories <= 0:
        if item.calories > 0:
            score -= min(40.0, item.calories / 25.0)
            reasons.append("You have already met today's calorie target.")
    else:
        cal_ratio = item.calories / remaining.calories
        if cal_ratio <= 1.0:
            score += cal_ratio * 40.0
            if cal_ratio >= 0.7:
                reasons.append("It is close to your remaining calories.")
        else:
            overshoot = cal_ratio - 1.0
            score += max(0.0, 40.0 - overshoot * 100.0)
            if overshoot <= 0.15:
                reasons.append("It is only slightly above your remaining calories.")

    if remaining.protein_g > 0:
        protein_ratio = min(item.protein_g, remaining.protein_g) / remaining.protein_g
        score += protein_ratio * 30.0
        density = item.protein_g / max(item.calories, 1)
        score += min(density, 0.3) * 20.0
        if protein_ratio >= 0.5:
            reasons.append("It helps close your remaining protein.")

    if item.carbs_g > remaining.carbs_g:
        overshoot = (item.carbs_g - remaining.carbs_g) / max(remaining.carbs_g, 1)
        score -= overshoot * 10.0
    if item.fat_g > remaining.fat_g:
        overshoot = (item.fat_g - remaining.fat_g) / max(remaining.fat_g, 1)
        score -= overshoot * 10.0

    pref_penalty, pref_reasons = _preference_penalty(item.name, prefs)
    score += pref_penalty
    reasons.extend(pref_reasons)

    score -= (1.0 - item.confidence) * 3.0

    if not reasons:
        reasons.append("It fits today's remaining targets.")

    return ScoredCandidate(item=item, score=round(score, 4), reasons=tuple(reasons))


class RecommendationService:
    def __init__(self, session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.food_repository = FoodRepository(session)
        self.menu_repository = MenuRepository(session)

    async def recommend(
        self,
        *,
        user_id: str,
        payload: RecommendationRequest,
    ) -> StructuredCoachResponse:
        targets = await self._targets(user_id)

        entries = await self.food_repository.list_entries_for_date(
            user_id=user_id,
            target_date=payload.date,
        )
        consumed = MacroTotals(
            calories=sum(entry.calories for entry in entries),
            protein_g=sum(entry.protein_g for entry in entries),
            carbs_g=sum(entry.carbs_g for entry in entries),
            fat_g=sum(entry.fat_g for entry in entries),
        )
        remaining = MacroTotals(
            calories=max(0, targets.calories - consumed.calories),
            protein_g=max(0, targets.protein_g - consumed.protein_g),
            carbs_g=max(0, targets.carbs_g - consumed.carbs_g),
            fat_g=max(0, targets.fat_g - consumed.fat_g),
        )

        if remaining.calories <= 0:
            return _at_target_response(payload, targets, consumed, remaining)

        menu_rows = await self.menu_repository.list_items_for_date(
            user_id=user_id,
            target_date=payload.date,
        )
        if not menu_rows:
            return _no_menu_response(payload, targets, consumed, remaining)

        profile = await self.user_repository.get_profile(user_id)
        prefs = parse_dietary_preferences(profile.dietary_preferences if profile else None)

        candidates = [
            score_menu_item(item=_to_recommended_item(row), remaining=remaining, prefs=prefs)
            for row in menu_rows
        ]
        candidates.sort(key=lambda candidate: (-candidate.score, candidate.item.name))

        top = candidates[0]
        alternatives = [candidate.item for candidate in candidates[1 : 1 + MAX_ALTERNATIVES]]
        uncertainty, uncertainty_reason = _uncertainty(top)

        return StructuredCoachResponse(
            date=payload.date,
            meal_type=payload.meal_type,
            targets=targets,
            consumed=consumed,
            remaining=remaining,
            recommendation=top.item,
            alternatives=alternatives,
            reason=_build_reason(top, remaining),
            uncertainty=uncertainty,
            uncertainty_reason=uncertainty_reason,
            suggested_action=(
                f"Log {top.item.name} for {payload.meal_type} to stay on track "
                "with today's targets."
            ),
        )

    async def _targets(self, user_id: str) -> MacroTotals:
        target = await self.user_repository.get_nutrition_target(user_id)
        if target is None:
            return DEFAULT_TARGETS
        return MacroTotals(
            calories=target.calories,
            protein_g=target.protein_g,
            carbs_g=target.carbs_g,
            fat_g=target.fat_g,
        )


def _to_recommended_item(row) -> RecommendedItem:
    return RecommendedItem(
        menu_item_id=row.id,
        name=row.name,
        calories=row.estimated_calories,
        protein_g=row.estimated_protein_g,
        carbs_g=row.estimated_carbs_g,
        fat_g=row.estimated_fat_g,
        confidence=row.confidence,
    )


def _uncertainty(candidate: ScoredCandidate) -> tuple[bool, str | None]:
    if candidate.item.confidence < CONFIDENCE_THRESHOLD:
        return True, (
            f"Nutrition values for {candidate.item.name} were extracted with low "
            f"confidence ({candidate.item.confidence:.0%}). Confirm values before logging."
        )
    return False, None


def _build_reason(candidate: ScoredCandidate, remaining: MacroTotals) -> str:
    headline = (
        f"You have {remaining.calories} kcal and {remaining.protein_g} g protein "
        "remaining for the day."
    )
    return headline + " " + " ".join(candidate.reasons)


def _at_target_response(
    payload: RecommendationRequest,
    targets: MacroTotals,
    consumed: MacroTotals,
    remaining: MacroTotals,
) -> StructuredCoachResponse:
    return StructuredCoachResponse(
        date=payload.date,
        meal_type=payload.meal_type,
        targets=targets,
        consumed=consumed,
        remaining=remaining,
        reason=(
            f"You have already met or exceeded today's calorie target "
            f"({consumed.calories} of {targets.calories} kcal). "
            "A full meal is not needed."
        ),
        uncertainty=True,
        uncertainty_reason="No calories remain within today's targets.",
        suggested_action="Log only a light, high-protein snack if you are still hungry.",
    )


def _no_menu_response(
    payload: RecommendationRequest,
    targets: MacroTotals,
    consumed: MacroTotals,
    remaining: MacroTotals,
) -> StructuredCoachResponse:
    return StructuredCoachResponse(
        date=payload.date,
        meal_type=payload.meal_type,
        targets=targets,
        consumed=consumed,
        remaining=remaining,
        reason=(
            "No office menu is available for this day yet. "
            "Recommendations are grounded in your available menu, so add or confirm "
            "today's menu first."
        ),
        uncertainty=True,
        uncertainty_reason="No available menu items were found for the requested day.",
        suggested_action="Upload or confirm today's menu, then ask again.",
    )
