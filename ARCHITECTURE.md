# FitMe Architecture

## 1. High-level architecture

``` text
Flutter Mobile App
        |
        | HTTPS / JSON
        v
FastAPI Backend
        |
        +------------------+
        |                  |
        v                  v
   PostgreSQL           Redis
        |
        v
 Object Storage
        |
        v
 AI Coach Service
        |
        v
 AI Provider Abstraction
        |
        +----------------+
        |                |
        v                v
 OpenAI Provider  OpenRouter Free Provider
 (and other providers, future)
```

The architecture should remain modular without prematurely becoming
microservices.

Use a modular monolith for the backend initially.

## 2. Technology choices

### Mobile

-   Flutter
-   Dart
-   Use a maintainable state-management approach.
-   Prefer a clear feature-oriented folder structure.
-   Use typed API models.
-   Centralize API client and authentication handling.

### Backend

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy
-   Alembic
-   PostgreSQL
-   Redis
-   Background job mechanism where needed

### Storage

Use S3-compatible object storage for uploaded images.

The implementation may use a local filesystem or local object-storage
emulator for development, but production code must use an object-storage
abstraction.

### AI

Use model providers through a dedicated backend service and provider
abstraction (`app/ai/provider.py`).

The mobile application must never call a model provider directly with
the secret API key.

Providers advertise the capabilities they serve (coach chat, vision
extraction). A `ProviderRegistry` resolves the right provider per
capability based on configuration, so different models can be used for
image processing vs. reasoning without touching the rest of the app:

``` text
AIProvider (interface)
├── OpenAICompatibleProvider  (shared implementation)
│   ├── OpenAIProvider
│   └── OpenRouterFreeProvider
└── OtherProvider  (future)
```

Selection is controlled by `FITME_AI_COACH_PROVIDER` /
`FITME_AI_VISION_PROVIDER` (`"auto"` picks the first configured provider
that supports the capability). Providers without an API key are not
registered.

## 3. Repository structure

Recommended:

``` text
fitme/
├── README.md
├── PRODUCT_SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT_PLAN.md
├── AGENTS.md
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── ai/
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
│
├── mobile/
│   ├── lib/
│   │   ├── core/
│   │   ├── features/
│   │   ├── shared/
│   │   └── main.dart
│   └── pubspec.yaml
│
└── docs/
```

The exact structure may be adjusted if Codex has a strong reason, but
responsibilities must remain separated.

## 4. Backend layering

Use:

``` text
API Router
    ↓
Application Service
    ↓
Repository / Domain Logic
    ↓
Database
```

Routers should remain thin.

Do not place complex business logic inside FastAPI route functions.

## 5. Core backend modules

### Authentication

-   Registration
-   Login
-   Token refresh if needed
-   Password handling
-   Authenticated user context

### Profile

Stores:

-   Personal information
-   Body composition
-   Goal
-   Dietary preferences
-   Activity level
-   Nutrition targets
-   User settings

### Nutrition

Responsible for:

-   Foods
-   Nutrition values
-   Food entries
-   Meal grouping
-   Daily totals
-   Remaining targets

### Office menu

Responsible for:

-   Menu uploads
-   Images
-   Extracted menu items
-   Nutrition metadata
-   Food matching
-   Duplicate detection
-   User confirmation

### Hydration

Responsible for:

-   Water entries
-   Daily totals
-   Hydration targets

### Workout

Responsible for:

-   Workout sessions
-   Exercise records
-   Cardio
-   Duration
-   Notes

Do not prescribe workouts.

### Sleep

Responsible for:

-   Sleep entries
-   Source
-   Bedtime
-   Wake time
-   Duration
-   Quality

Source enum should allow future integrations.

### Progress

Responsible for:

-   Weight history
-   Trend calculations
-   Weekly summaries
-   Adherence metrics

### AI

Responsible for:

-   Coach context construction
-   Prompt management
-   Provider abstraction and capability routing
-   Tool definitions
-   Tool execution orchestration
-   Response validation
-   Conversation history

Provider integration lives in `app/ai/provider.py`. Callers depend on
the `AIProvider` interface or capability-specific protocols, never on a
specific vendor class.

## 6. Suggested database entities

Initial entities:

``` text
User
UserProfile
NutritionTarget
Food
FoodNutrition
FoodEntry
Meal
OfficeMenu
OfficeMenuItem
FoodImage
WaterEntry
WorkoutSession
WorkoutExercise
SleepEntry
WeightEntry
DailySummary
CoachConversation
CoachMessage
CoachRecommendation
Notification
```

Do not create every possible table before a feature requires it.

## 7. Event/time handling

All persisted timestamps should be timezone-aware.

Store timestamps consistently in UTC.

Store the user's timezone in the profile/settings.

Convert to local time at the API/UI boundaries.

Daily summaries must use the user's local calendar date.

## 8. Food nutrition model

Nutrition data should support at least:

-   Calories
-   Protein
-   Carbohydrates
-   Fat

Optionally:

-   Fiber
-   Sugar
-   Sodium

The data model should identify the basis:

-   Per 100g
-   Per serving
-   Per item
-   Office-provided serving

This is critical because "250 kcal" is meaningless without knowing the
serving basis.

## 9. Image processing pipeline

``` text
Mobile camera
     ↓
Upload
     ↓
Object storage
     ↓
Processing job
     ↓
OpenAI vision/OCR
     ↓
Structured extraction
     ↓
Validation
     ↓
Normalization
     ↓
Matching
     ↓
Persist menu
     ↓
Mobile confirmation
```

If processing is asynchronous, return a processing status to the mobile
application.

## 10. AI context architecture

Do not pass the entire database to the LLM.

Build a `CoachContext` object from deterministic backend queries.

The context should include only relevant information.

Potential sections:

``` text
user
targets
today_summary
remaining_targets
today_meals
today_menu
recent_weight_trend
recent_training
recent_sleep
recent_coaching_notes
```

## 11. AI prompt management

Prompts should be:

-   Versioned
-   Stored in code/configuration
-   Tested
-   Separated into system instructions and runtime context

Do not scatter prompts across route handlers.

## 12. AI tool execution

The model may request an application action.

Flow:

``` text
User
 ↓
Coach endpoint
 ↓
Build CoachContext
 ↓
OpenAI
 ↓
Tool call
 ↓
Backend validates arguments
 ↓
Application service executes action
 ↓
Result returned to model
 ↓
Final coach response
```

Never allow arbitrary SQL, filesystem access, or arbitrary backend
execution through the model.

## 13. Deterministic calculations

Create dedicated services for:

-   Daily nutrition totals
-   Remaining nutrition targets
-   Hydration totals
-   BMI
-   7-day weight average
-   Weight trend
-   Rate of weight change
-   Weekly adherence

Unit-test these heavily.

## 14. Authentication/security

Requirements:

-   Passwords hashed using a strong password hashing algorithm.
-   JWT/access tokens handled securely.
-   Secrets only through environment/configuration.
-   OpenAI API key only on backend.
-   Uploaded image URLs must not expose private objects permanently.
-   Validate upload type and size.
-   Rate-limit AI endpoints.
-   Never log secrets or sensitive payloads.

## 15. Observability

MVP should have:

-   Structured application logs
-   Request IDs
-   Error logging
-   AI request metadata without sensitive content
-   Basic health endpoint

Track AI usage/cost metadata where practical.

Never log the user's entire private conversation or food photos by
default.

## 16. Testing

Backend:

-   Unit tests for calculations
-   API tests for critical flows
-   Database integration tests
-   AI orchestration tests with mocked OpenAI responses

Flutter:

-   Unit tests for state/business logic
-   Widget tests for critical flows

Do not make the test suite dependent on live OpenAI calls.

## 17. Architecture anti-patterns

Avoid:

-   Microservices
-   Vector database without demonstrated need
-   LLM-driven arithmetic
-   Direct mobile-to-OpenAI calls
-   Database access from Flutter
-   Business logic inside UI widgets
-   Giant route functions
-   Giant prompts containing the entire database
-   Storing images directly in PostgreSQL
-   Hardcoded user nutrition targets
-   Autonomous AI modifications without validation
