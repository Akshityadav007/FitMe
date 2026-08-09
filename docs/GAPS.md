# FitMe Gap Tracker

This file is the handoff point for future work. When a new model (or a
fresh session) needs to continue this project, start here instead of
scanning the whole repository. Read `README.md`, `PRODUCT_SPEC.md`,
`ARCHITECTURE.md`, and `DEVELOPMENT_PLAN.md` for full context, then pick
up an item below.

Status legend: `[ ]` open, `[x]` done, `[~]` partially done.

## Repository map (where things live)

- `backend/app/ai/` — AI layer: prompts, tools, context, provider
  abstraction.
- `backend/app/services/` — business logic (thin routers elsewhere).
- `backend/app/api/v1/` — FastAPI routers.
- `backend/app/repositories/` — data access.
- `backend/app/models/` — SQLAlchemy models.
- `backend/app/schemas/` — Pydantic schemas.
- `mobile/lib/features/` — Flutter feature modules.
- `docs/phase-*.md` — per-phase implementation notes.
- `.github/workflows/` — CI (backend + mobile).

## Test / verification commands

- Backend: `backend\.venv\Scripts\python.exe -m pytest -q` from
  `backend/` (needs local Postgres at the DSN in `app/core/config.py`).
- Backend lint: ruff (a ruff env exists at
  `C:\Users\Benak\AppData\Local\Temp\opencode\ruffenv\Scripts\ruff.exe`).
- Mobile: `flutter analyze` and `flutter test` from `mobile/`.

## Current state (last verified)

- Backend: Phases 0–8 complete, **45 tests pass**. Schema managed by
  Alembic; migration head is applied (`alembic current` shows the head).
- Mobile: Phase 9 screens implemented, `flutter analyze` clean, **10
  tests pass**.
- CI workflows exist for backend and mobile but have not been run on
  GitHub yet (no repo push since they were added).
- Phase 10 (wearables/health-platform integrations) is deliberately
  deferred by design.

## Open gaps

### Documentation / CI

- [ ] Push to GitHub and confirm both CI workflows
      (`.github/workflows/backend.yml`, `.github/workflows/mobile.yml`)
      actually go green end to end.
- [ ] Confirm `openrouter/free` is still the desired free model; free
      models on OpenRouter change frequently. The value lives in
      `FITME_OPENROUTER_COACH_MODEL` / `FITME_OPENROUTER_VISION_MODEL`.
- [ ] Decide whether to add a `FITME_OPENROUTER_HTTP_REFERER` /
      `FITME_OPENROUTER_SITE_TITLE` header setting (OpenRouter
      recommends identifying your app; not implemented).

### Backend

- [ ] Add a `GET /api/v1/ai/providers` status endpoint that reports
      which providers/capabilities are configured and active. Useful for
      ops and for the mobile app to show AI availability.
- [ ] Consider per-capability model fallback: if the preferred provider
      for a capability is down, the registry currently returns `None`
      rather than failing over to the next configured provider. Decide
      whether failover is desirable (and how to surface it).
- [ ] `VisionMenuItem` has no serving-size field. The menu confirmation
      flow scales by `quantity_g` on confirm; consider extracting a
      serving basis from vision output.
- [ ] Rate limiting on AI endpoints (OpenRouter free tier is limited to
      20 requests/minute). If the coach is hit from multiple users,
      add throttling.
- [ ] Secrets are read via `FITME_*` env vars only. There is no secret
      manager / vault integration; fine for local but note for prod.

### Mobile

- [ ] Menu capture has not been validated on a real device (camera +
      live backend). The `image_picker` dependency needs a device; the
      flow is untested on-device.
- [ ] AI provider selection is a backend concern only. The mobile app
      does not surface which provider/model answered. Decide if that is
      needed.
- [ ] Notifications: quiet-hours defaults and frequency caps are
      backend-side; the UI has toggles but no "test notification" flow.

### AI provider abstraction (implemented, extend later)

Implemented in `backend/app/ai/provider.py`:

```
AIProvider (interface)
├── OpenAICompatibleProvider  (shared implementation)
│   ├── OpenAIProvider
│   └── OpenRouterFreeProvider
└── OtherProvider  (future)
```

- [x] Capability routing: each provider advertises which capabilities it
      supports (`AICapability.COACH`, `AICapability.VISION`).
- [x] `ProviderRegistry` resolves the provider per capability, honoring
      `FITME_AI_COACH_PROVIDER` / `FITME_AI_VISION_PROVIDER`
      (`"auto"` selects the first configured provider that supports the
      capability).
- [x] Only providers with an API key are registered, so an unset key
      does not shadow a configured one.
- [ ] Future work: add providers for Anthropic, Gemini, local models,
      or a chained "vision model → coach model" pipeline. Register them
      in `build_provider_registry`.

### Phase 10 (deferred by design)

- [ ] Wearable / health-platform integrations (Apple HealthKit, Google
      Fit, Garmin, etc.) — intentionally deferred until the core product
      is stable on device. Do not start without revisiting
      `DEVELOPMENT_PLAN.md`.

## Known conventions / gotchas

- Do not run `pip`; the backend venv is uv-managed.
- Tests drop/recreate all tables from `Base.metadata`, not via Alembic.
- Pydantic: a model field named `date` shadows the type; use
  `from datetime import date as date_type`.
- Ruff config in `backend/pyproject.toml` intentionally ignores `B008`
  (FastAPI `Depends` defaults) and `DTZ011` (`date.today()` in tests).
- AI tests must not call a live model API (mocked in CI).
