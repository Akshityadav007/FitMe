# Phase 7 Proactive Coaching

Phase 7 adds configurable, non-spammy notifications that respect quiet
hours and per-day deduplication.

## What was added

- `app/models/notification.py` — `Notification` and
  `NotificationPreference`.
- `app/repositories/notification_repository.py` — preferences upsert,
  notification creation, per-day dedupe, listing, mark-read.
- `app/services/notification_service.py` — rule evaluation and
  notification generation.
- `app/schemas/notification.py` — preferences and notification response
  schemas.
- `app/api/v1/notifications.py` — preferences and notification endpoints.

## Endpoints

- `GET /api/v1/notifications/preferences`
- `PUT /api/v1/notifications/preferences`
- `POST /api/v1/notifications/check` — generate due notifications now
- `GET /api/v1/notifications` — list recent notifications
- `POST /api/v1/notifications/{id}/read`

## Rules

- **Hydration** — during 08:00–21:00 when logged water is below target.
- **Protein status** — before 20:00 when at least 20 g of protein remain.
- **Meal reminder** — during 11:00–14:30 when calories remain and a menu
  is available.
- **End of day** — after 21:00 with a summary of calories, protein, and
  water.

## Anti-spam guarantees

- Quiet hours (default 22:00–07:00) suppress all notifications.
- Each category is sent at most once per day (`day_key`).
- Every category can be disabled independently.

## Defaults

All categories enabled, quiet hours `22:00`–`07:00`. Users can override
both timings and enabled flags.

## Tests

`backend/tests/test_phase7_notifications.py` covers default and updated
preferences, quiet-hour suppression, hydration generation and dedupe,
end-of-day generation, and mark-read behavior against PostgreSQL.
