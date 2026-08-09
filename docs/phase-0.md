# Phase 0 Local Development

Phase 0 contains only the project foundation:

- FastAPI application setup
- environment-based configuration
- PostgreSQL and Redis containers
- SQLAlchemy 2.x async session foundation
- Alembic foundation
- `GET /api/v1/health`
- Flutter application shell with a typed health API client

It intentionally does not include authentication, profile, nutrition,
food logging, image processing, OpenAI integration, notifications, or
domain database tables.

## Backend

From `backend/`:

``` powershell
..\.codex-tools\bin\uv.exe sync
..\.codex-tools\bin\uv.exe run uvicorn app.main:app --reload
```

Health endpoint:

``` text
GET http://localhost:8000/api/v1/health
```

Run tests:

``` powershell
..\.codex-tools\bin\uv.exe run pytest
```

## Database

From the repository root:

``` powershell
docker compose up -d postgres redis
```

Alembic is configured against `FITME_DATABASE_URL`. Phase 0 has no domain
tables, so there are no migrations to apply yet.

## Flutter

From `mobile/`:

``` powershell
flutter pub get
flutter run --dart-define=FITME_API_BASE_URL=http://localhost:8000/api/v1
```

For Android emulator networking, use:

``` powershell
flutter run --dart-define=FITME_API_BASE_URL=http://10.0.2.2:8000/api/v1
```
