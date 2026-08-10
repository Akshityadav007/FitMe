# FitMe

> AI-assisted personal nutrition, hydration, recovery, and fitness
> adherence coach.

FitMe is a Flutter mobile application backed by FastAPI and PostgreSQL.
It combines structured fitness data with an AI coaching layer to help
users make better day-to-day nutrition and recovery decisions.

## Why FitMe?

Most AI fitness apps are essentially chat interfaces with a prompt.

FitMe takes a different approach:

> The application owns facts and deterministic calculations.
> The AI interprets those facts and coaches the user.

This means calories, macros, hydration, weight trends, and other
deterministic metrics are calculated by the backend rather than guessed
by an LLM.

## Architecture

```text
Flutter
   │
   ▼
FastAPI
   │
   ├── PostgreSQL
   ├── Object Storage
   │
   └── AI Coach
          │
          ▼
      OpenAI API
```

## Core Features
- Daily nutrition tracking
- AI-powered meal recommendations
- Office menu/food photo recognition
- Calorie and macro tracking
- Hydration tracking
- Weight tracking
- Sleep tracking
- Workout logging
- Daily coaching
- Weekly progress analysis
- Proactive reminders
- Future wearable/health-platform integrations

## Tech Stack

### Mobile
- Flutter
- Dart
- Riverpod

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

### AI
- OpenAI API
- OpenRouter (free model routing)
- Provider abstraction with per-capability selection (coach vs. vision)
- Vision-based food/menu extraction
- Structured AI tool calling

## Infrastructure
- Docker
- Object storage
- GitHub Actions

## Engineering Principles
- Deterministic calculations stay deterministic.
- The LLM is not the source of truth.
- The LLM does not have unrestricted database access.
- Business logic belongs in the backend.
- Mobile UI does not contain business logic.
- AI responses are grounded in structured application state.
- Security and validation happen outside the model.

## Development Status

### Completed phases

### Phase 0 — Foundation ✅

- FastAPI foundation
- PostgreSQL
- SQLAlchemy
- Alembic
- Flutter application shell
- API client boundary
- Health endpoint
- Automated tests
- Docker development environment
- GitHub Actions CI for backend and mobile

### Phase 1 — Authentication and profile ✅

- Registration and login
- Authenticated sessions with JWT
- User profile and fitness baseline storage
- Dietary preferences
- Nutrition targets
- Protected API routes for profile access and updates

### Phase 2 — Daily logging ✅

- Weight logging
- Water logging
- Daily summary aggregation
- Food entry logging for meals

### Phase 3 — Nutrition engine ✅

- Food database and nutrition records
- Food-entry model and calculation logic
- Deterministic macro totals for entries and daily summaries

### Phase 4 — Office menu capture ✅

- Camera/gallery selection
- Image upload with object-storage abstraction (local filesystem backend)
- File type, size, and status validation
- Menu processing state (pending → processing → extracted → failed)
- AI vision extraction to structured items
- Versioned vision prompt (`VISION_PROMPT_VERSION`)
- User confirmation of extracted items → food entries
- Food normalization and repeated-food detection (trusted nutrition wins)

### Phase 5 — Office meal recommendations ✅

- Current-day context built from logged entries and targets
- Available menu context for the requested day
- Deterministic server-side recommendation service
- Structured coaching endpoint (`POST /api/v1/recommendations`)
- Recommendations grounded in remaining calories, protein, macros,
  dietary preferences, meal context, and available menu data
- Uncertainty preserved for low-confidence extracted menu items

### Phase 6 — AI coach ✅

- Dedicated AI service with mocked-LLM testability
- Versioned system prompt (`SYSTEM_PROMPT_VERSION`)
- Deterministic `CoachContext` snapshot (never the whole database)
- 13 validated AI tools with server-side Pydantic argument validation
- Tool-calling loop with conversation history and persistence
- Chat endpoint (`POST /api/v1/coach/chat`)
- Structured AI response schema and error mapping (503/429/502/404/403)

### Phase 7 — Proactive coaching ✅

- Hydration reminders
- Protein status
- Meal reminders
- End-of-day summary
- Configurable notification preferences
- Quiet hours (default 22:00–07:00)
- Per-day, per-category deduplication (no spam)

### Phase 8 — Weekly progress ✅

- Weight chart data, 7-day average, trend, and rate of change
- Average calories and protein adherence
- Water, steps, sleep, and training adherence
- Deterministic weekly aggregates
- Weekly AI review (`POST /api/v1/progress/weekly/review`)

### Phase 9 — Mobile client & polish ✅

- Auth-gated app shell with login/register and JWT session storage
- 8-tab navigation: Today, Suggest, Coach, Progress, Menu, Alerts,
  Profile, Targets
- Daily summary screen with quick logging (water, food, steps, sleep,
  workout, weight)
- Menu recommendation screen grounded in remaining targets
- Conversational AI coach screen with structured reply rendering
- Menu capture screen (camera/gallery → upload → extraction → confirm)
- Weekly progress screen with adherence breakdown
- Notification preferences + list + manual check + mark-read
- Profile editing and nutrition targets editing
- Loading, empty, and error states on every screen
- `flutter analyze` clean; unit tests pass with a mocked HTTP client

### Upcoming

- Phase 10 — Future integrations

### Current repository state

The backend implements Phases 0–8 of the roadmap: auth/profile, daily
logging (food, water, weight, steps, sleep, workouts), the nutrition
engine, office menu capture (upload, vision extraction, confirmation,
repeated-food detection), deterministic meal recommendations, the
conversational AI coach, proactive notifications, and weekly progress.
All 45 backend tests pass against PostgreSQL, and the schema is managed
through Alembic migrations. The AI layer is fully mockable so CI never
depends on a live model API; set `FITME_OPENAI_API_KEY` and/or
`FITME_OPENROUTER_API_KEY` to enable live coaching. Model providers are
plugged in through a provider abstraction (`app/ai/provider.py`) with
per-capability routing (coach vs. vision), so OpenAI, OpenRouter, and
future providers can be swapped or mixed without touching callers. The
Flutter client implements the Phase 9 screens end to end, with `flutter
analyze` clean and passing widget/repository tests. Phase 10
(wearables/health-platform integrations) is deferred by design until the
core product is stable on device.

Continuous integration runs the backend test suite (with a mockable AI
layer and a PostgreSQL service container) and the Flutter analyze/test
suite on every push and pull request.



## Product Context

FitMe is initially being developed as a personal fitness coaching
application, with the architecture designed so that user-specific
fitness data is stored in the application rather than embedded in
source code.

The system supports configurable:

- Body metrics
- Fitness goals
- Dietary preferences
- Nutrition targets
- Activity levels
- Training schedules
- Hydration targets
- Sleep data
- Weight history

Initial development uses a synthetic/local development profile.
Real user data is never committed to the repository.

## Primary user experience

The user should be able to:

1.  Start the day and see current targets.
2.  Log pre-workout intake.
3.  Log workout activity.
4.  Upload photographs of office food/menu information.
5.  Have the system extract food and nutrition information.
6.  Receive recommendations about what to eat from the available
    options.
7.  Log consumed food.
8.  Log water.
9.  Log weight.
10. Log sleep manually.
11. Log steps manually initially.
12. Log dinner manually or by photograph.
13. Ask the AI coach questions about the current day.
14. Receive proactive coaching and reminders.
15. Review daily and weekly progress.

## Project Structure

```text
fitme/
├── backend/
├── mobile/
├── docs/
├── AGENTS.md
├── ARCHITECTURE.md
├── PRODUCT_SPEC.md
└── DEVELOPMENT_PLAN.md
```

## Development

See ARCHITECTURE.md for the system design and
DEVELOPMENT_PLAN.md for the implementation roadmap.

## Important product boundary

FitMe is a nutrition/recovery/adherence coach.

It is NOT a replacement for the user's real trainer.

The AI must not invent, modify, or prescribe the user's
resistance-training program unless the user explicitly asks for general
information and the response is clearly framed as informational. The
existing trainer's workout plan remains authoritative.