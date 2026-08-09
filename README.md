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
   ├── Redis
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
- Redis

### AI
- OpenAI API
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

### Phase 0 — Foundation ✅

- FastAPI foundation
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Flutter application shell
- API client boundary
- Health endpoint
- Automated tests
- Docker development environment

### Upcoming

-  Authentication and user profile
-  Daily fitness logging
-  Nutrition engine
-  Office menu recognition
-  AI coaching
-  Proactive notifications
-  Weekly analytics
-  Health/wearable integrations



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