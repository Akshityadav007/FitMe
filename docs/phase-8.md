# Phase 8 Weekly Progress

Phase 8 adds deterministic weekly aggregates and an AI-interpreted
weekly review.

## What was added

- `app/schemas/progress.py` — weekly progress response schemas.
- `app/services/progress_service.py` — `WeeklyProgressService`
  aggregates a 7-day window (end date inclusive) across all daily
  domains.
- `app/api/v1/progress.py` — weekly progress and review endpoints.
- `GET /api/v1/progress/weekly?end_date=YYYY-MM-DD`
- `POST /api/v1/progress/weekly/review` — AI-written review grounded in
  deterministic aggregates.
- Repository range queries (`*_between`) for weight, water, steps,
  sleep, workouts, and food entries.

## Weekly aggregates

- **Weight** — entries, 7-day average, trend, and weekly rate of change.
- **Nutrition** — logged days, average calories, average protein,
  protein adherence percent.
- **Hydration** — logged days, average water, adherence percent.
- **Steps** — logged days, average steps.
- **Sleep** — logged days, average sleep minutes.
- **Training** — workout days and adherence percent.

Adherence is capped at 100% and computed deterministically server-side.

## Weekly review

`POST /api/v1/progress/weekly/review` passes only the deterministic
aggregates to the AI, never raw user data. The model returns plain
conversational text (not JSON) with a 200-word limit.

## Tests

`backend/tests/test_phase8_progress.py` seeds a week of logged data and
verifies every aggregate numerically against PostgreSQL, including the
empty-week case.
