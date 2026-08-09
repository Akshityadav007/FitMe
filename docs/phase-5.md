# Phase 5 Office Meal Recommendations

Phase 5 adds deterministic, server-side meal recommendations grounded in
the current database state.

## What was added

- `RecommendationService` — deterministic scoring and selection of menu
  items using today's targets, logged food entries, available menu
  items, and dietary preferences.
- `POST /api/v1/recommendations` — structured coaching response
- `GET /api/v1/menu-items?date=YYYY-MM-DD` — available menu context for
  the requested day
- Deterministic dietary-preference parsing (e.g. "Eggetarian + chicken;
  Spicy food not preferred")
- Uncertainty handling for low-confidence extracted menu items

## Recommendation endpoint

`POST /api/v1/recommendations` (authenticated)

``` json
{
  "date": "2026-08-09",
  "meal_type": "lunch"
}
```

The service computes consumed totals from that day's food entries,
remaining totals from the user's nutrition targets, and scores each
available menu item deterministically. The response distinguishes:

- `recommendation` — best-scoring item
- `alternatives` — up to three next-best items
- `reason` — explanation tied to remaining targets
- `remaining` — remaining calories/protein/carbs/fat
- `uncertainty` / `uncertainty_reason` — set when the top item was
  extracted with low confidence or no menu is available
- `suggested_action` — a concrete next step

## Edge cases

- No menu available for the requested day → `recommendation: null`,
  `uncertainty: true`.
- Calorie target already met or exceeded → `recommendation: null`,
  `uncertainty: true`.

## Notes

Recommendation logic is deterministic and server-side. No LLM call is
made in this phase; Phase 6 adds the conversational AI coach on top of
this deterministic core.

Menu items are scoped to the requested local date using UTC day
boundaries. The user timezone is not yet stored in the profile, so the
day boundary is UTC until a timezone field is introduced.

## Tests

`backend/tests/test_phase5_recommendations.py` covers the deterministic
scoring rules, preference parsing, and end-to-end API behavior against
PostgreSQL.
