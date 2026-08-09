# FitMe Codex Engineering Rules

## 1. Read the specification first

Before modifying code, read:

-   README.md
-   PRODUCT_SPEC.md
-   ARCHITECTURE.md
-   DEVELOPMENT_PLAN.md

These documents define the product and architectural constraints.

## 2. General rule

Prefer the simplest correct implementation.

Do not over-engineer.

Do not introduce a dependency merely because it is popular.

Do not introduce microservices for a problem a modular monolith solves.

## 3. AI boundary

The LLM is not the database.

The LLM is not the calculator.

The LLM is not the authorization layer.

The LLM is not allowed unrestricted access to infrastructure.

Use the AI for interpretation and coaching.

Use deterministic application services for facts and calculations.

## 4. Security

Never:

-   Commit API keys
-   Put OpenAI secrets in Flutter
-   Log secrets
-   Log authorization tokens
-   Expose private object-storage credentials
-   Trust model-generated database identifiers without validation

All AI tool calls must be validated by backend code.

## 5. Backend rules

Use:

-   Thin FastAPI routers
-   Pydantic schemas
-   SQLAlchemy models
-   Service-layer business logic
-   Repository/data-access separation where useful
-   Alembic migrations
-   Explicit transaction handling

Do not put business logic in routers.

Do not return raw ORM objects as the public API contract.

## 6. Database rules

Use migrations for schema changes.

Never manually edit production schema.

Use timezone-aware timestamps.

Use the user's local date when calculating daily summaries.

Add indexes based on actual query patterns.

Do not create speculative indexes or tables without reason.

## 7. Nutrition rules

Nutrition calculations must be deterministic.

Never ask the LLM to calculate totals if the backend can calculate them.

Every nutrition quantity must have a clear serving basis.

If nutrition information is uncertain, preserve uncertainty rather than
inventing precision.

## 8. Image processing rules

Uploaded images should be stored in object storage.

Do not store large binary image data directly in PostgreSQL.

Validate:

-   File type
-   File size
-   Upload status

Vision extraction must produce structured data.

Never silently overwrite trusted nutrition information with uncertain
extracted data.

## 9. Flutter rules

Keep UI widgets focused on presentation.

Do not put networking/business calculations inside widgets.

Use a consistent state-management approach throughout the application.

Keep API models typed.

Handle:

-   Loading
-   Success
-   Empty
-   Error

states explicitly.

## 10. API rules

Use versioned APIs where appropriate.

Return consistent error structures.

Validate all user input.

Use pagination for potentially large collections.

Do not return unnecessary fields.

## 11. Testing rules

Every deterministic nutrition/progress calculation must have unit tests.

Critical API flows need integration/API tests.

OpenAI calls must be mocked in automated tests.

Do not make CI dependent on a live model API.

## 12. AI prompt rules

Prompts should be centralized and versioned.

Do not construct huge prompts in route handlers.

Use structured context.

Avoid sending irrelevant personal data.

The AI should state uncertainty when information is incomplete.

## 13. AI response rules

Prefer structured output internally.

A coach response should distinguish, where useful:

-   Recommendation
-   Reason
-   Relevant remaining targets
-   Uncertainty
-   Suggested action

The final UI may render this in a friendly conversational format.

## 14. Product boundary

The application is a nutrition/recovery/adherence coach.

The user has a real human trainer.

Do not replace the trainer's workout program.

Do not invent exercise prescriptions.

## 15. Notifications

Notifications must be:

-   Useful
-   Configurable
-   Respectful of quiet hours
-   Non-spammy

Do not send a reminder for every trivial event.

## 16. Code quality

Prefer:

-   Clear names
-   Small cohesive functions
-   Explicit types
-   Simple control flow
-   Useful comments only where reasoning is non-obvious

Avoid:

-   Clever abstractions without need
-   Giant classes
-   Giant functions
-   Magic constants
-   Dead code
-   Copy-paste implementations
-   Premature generic frameworks

## 17. Dependency policy

Before adding a dependency:

1.  Check whether the standard library/framework already solves the
    problem.
2.  Check whether an existing dependency already provides the
    capability.
3.  Consider maintenance and security.
4.  Add the smallest appropriate dependency.

## 18. Git discipline

Keep commits logically grouped.

Prefer small coherent changes.

Do not mix:

-   Formatting-only changes
-   Refactors
-   New features
-   Unrelated fixes

unless necessary.

## 19. Completion behavior

When implementing a task:

1.  Inspect.
2.  Plan.
3.  Implement.
4.  Test.
5.  Fix.
6.  Report what changed.
7.  Report tests run.
8.  Report known limitations.

Do not claim something is implemented if it is only scaffolded.

## 20. When requirements conflict

Priority:

1.  Security
2.  Correctness
3.  Existing working behavior
4.  Product specification
5.  Maintainability
6.  Performance
7.  Convenience

If a requested shortcut conflicts with correctness or security, reject
the shortcut and implement the correct approach.
