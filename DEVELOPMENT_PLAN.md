# FitMe Development Plan

## Instructions to Codex

Implement the project incrementally.

Do not attempt to generate the entire application in one uncontrolled
pass.

Before each major phase:

1.  Inspect the existing repository.
2.  Read README.md, PRODUCT_SPEC.md, ARCHITECTURE.md, and AGENTS.md.
3.  Identify what already exists.
4.  Implement only the requested phase.
5.  Run tests.
6.  Fix failures.
7.  Update documentation.
8.  Do not rewrite working code unnecessarily.

If an architectural ambiguity materially affects correctness, document
the ambiguity and choose the simplest maintainable solution.

## Phase 0 --- Repository and architecture

Deliver:

-   Repository structure
-   Flutter application skeleton
-   FastAPI application skeleton
-   PostgreSQL
-   Docker Compose
-   Environment configuration
-   Basic health endpoint
-   Basic CI/test setup
-   Documentation

Acceptance:

-   Backend starts locally.
-   Database starts locally.
-   Flutter app starts.
-   Basic connectivity works.

## Phase 1 --- Authentication and profile

Implement:

-   Registration
-   Login
-   Authenticated sessions
-   User profile
-   Fitness baseline
-   Dietary preferences
-   Nutrition targets
-   Settings

Profile fields must support the current user's data from README.

Acceptance:

-   User can create/login.
-   User can edit profile.
-   Targets are persisted.
-   No nutrition values are hardcoded into the frontend.

## Phase 2 --- Daily logging

Implement:

-   Weight logging
-   Water logging
-   Food logging
-   Meal categorization
-   Sleep logging
-   Workout session logging
-   Steps logging
-   Daily summary

Acceptance:

-   User can log all major daily events.
-   Daily totals are deterministic.
-   Daily summary correctly reflects entries.

## Phase 3 --- Nutrition engine

Implement:

-   Food database
-   Nutrition model
-   Food entry model
-   Daily macro calculations
-   Remaining target calculations
-   Unit tests

Acceptance:

Given known food quantities, the backend produces deterministic totals.

Example:

``` text
Target = 2350 kcal
Consumed = 1420 kcal
Remaining = 930 kcal
```

The LLM must not perform this calculation.

## Phase 4 --- Office menu capture

Implement:

-   Camera/gallery selection
-   Image upload
-   Object storage abstraction
-   Menu processing state
-   AI vision extraction
-   Structured food/nutrition extraction
-   User confirmation
-   Food normalization
-   Repeated food detection

Acceptance:

A photographed menu can be turned into structured menu items.

If a food already exists with trusted nutrition data, reuse it rather
than blindly overwriting it.

## Phase 5 --- Office meal recommendations

Implement:

-   Current-day context
-   Available menu context
-   Recommendation service
-   AI coach endpoint
-   Structured coach response

Example request:

> What should I eat for lunch?

The coach should consider:

-   Remaining calories
-   Remaining protein
-   Remaining macros
-   Current meal
-   Available menu
-   User dietary preferences

Acceptance:

Recommendations are grounded in current database state.

## Phase 6 --- AI coach

Implement:

-   Dedicated AI service
-   Versioned system prompt
-   CoachContext builder
-   Tool/function definitions
-   Tool execution
-   Validation
-   Conversation history
-   Error handling
-   AI response schema

Minimum tools:

``` text
get_user_profile
get_today_summary
get_remaining_targets
get_today_menu
get_recent_weight_trend
get_recent_training
get_recent_sleep
log_food
log_water
log_weight
log_sleep
log_workout
recommend_meal
```

Acceptance:

The model can answer contextual questions without receiving the entire
database.

## Phase 7 --- Proactive coaching

Implement:

-   Hydration reminders
-   Meal reminders where useful
-   Protein status
-   End-of-day summary
-   Notification preferences
-   Quiet hours

Acceptance:

Notifications are useful and configurable.

Do not spam the user.

## Phase 8 --- Weekly progress

Implement:

-   Weight chart
-   7-day average
-   Weight trend
-   Average calories
-   Protein adherence
-   Water adherence
-   Steps
-   Sleep
-   Training adherence
-   Weekly AI review

Acceptance:

Weekly review uses deterministic aggregates and AI interpretation.

## Phase 9 --- Polish

Improve:

-   Loading states
-   Error states
-   Empty states
-   Offline-friendly behavior where practical
-   Accessibility
-   Navigation
-   Visual hierarchy
-   Performance
-   Image upload UX
-   Notification UX

## Phase 10 --- Future integrations

Do not implement until the core product is stable.

Potential integrations:

-   Google Health Connect
-   Apple Health
-   Wearables
-   Automatic steps
-   Automatic sleep
-   Heart-rate/recovery metrics

Design the domain now so these can be added without replacing manual
entries.

## Definition of done

A phase is complete only when:

-   Feature works end-to-end.
-   Tests exist for important business logic.
-   Error paths are handled.
-   API contracts are documented.
-   Database migrations work from a clean database.
-   No secrets are committed.
-   No obvious TODO placeholders remain in the implemented feature.
-   Existing functionality still works.

## Priority rule

If scope becomes too large, prioritize:

1.  Correct data model
2.  Deterministic calculations
3.  Reliable logging
4.  AI context/tool architecture
5.  Core UX
6.  Notifications
7.  Analytics
8.  Integrations
9.  Nice-to-have features

Do not sacrifice architecture correctness to add flashy AI features.
