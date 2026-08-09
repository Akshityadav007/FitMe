# Phase 9 Mobile Client

Phase 9 delivers the Flutter application shell and feature screens that
consume the Phases 0–8 backend APIs.

## What was added

- `lib/core/network/api_client.dart` — `authToken` support on
  `getJson`/`postJson`/`putJson`, `getJsonList` for array responses,
  `postJsonList`, and `postBytes` for raw image uploads.
- `lib/features/auth/` — `auth_screen.dart` (login/register form),
  `profile_screen.dart` (profile editing + sign out),
  `nutrition_targets_screen.dart` (target editing), `auth_repository.dart`,
  `auth_providers.dart`, `session_storage.dart`. `apiClientProvider` and
  `appConfigProvider` live here and are shared by all features.
- `lib/features/home/home_shell.dart` — auth-gated shell with an
  8-tab `NavigationBar`: Today, Suggest, Coach, Progress, Menu, Alerts,
  Profile, Targets.
- `lib/features/daily/` — typed models, repository, Riverpod providers,
  and `daily_screen.dart` (summary cards, quick logging for water, food,
  steps, sleep, workout, and weight).
- `lib/features/recommendation/` — models, repository, providers, and
  screen rendering the structured recommendation.
- `lib/features/coach/` — chat models, repository, providers, and
  `coach_screen.dart`.
- `lib/features/progress/` — weekly aggregate models, repository,
  providers, and screen with adherence breakdown.
- `lib/features/menu_capture/` — models, repository, providers, and
  `menu_capture_screen.dart` (camera/gallery → upload → extraction →
  confirmation).
- `lib/features/notifications/` — preference models, repository,
  providers, and screen with a manual "check now" action and mark-read.
- `lib/app.dart` — now mounts `HomeShell` under `ProviderScope`.

## Architecture notes

- State management is Riverpod throughout (`StateNotifierProvider` for
  conversation state, `FutureProvider`/`AsyncNotifier` for loaded data).
- Widgets stay presentation-only; networking lives in repositories,
  which receive the shared `ApiClient` through providers.
- All API models are typed and handle loading/success/empty/error
  states explicitly.
- The shell is auth-gated: `HomeShell` watches `authTokenProvider` and
  renders `AuthScreen` when no session is present.

## Tests

- `test/widget_test.dart` — pumps `FitMeApp` with an overridden
  `authTokenProvider` (avoids the secure-storage MethodChannel) and
  asserts the shell renders.
- `test/health_repository_test.dart` — health contract parsing.
- `test/daily_repository_test.dart` — daily summary and recommendation
  contract parsing against a `MockClient` (`package:http/testing`).
- `test/logging_repository_test.dart` — food/sleep/workout logging and
  notification check contracts.
- `test/menu_capture_repository_test.dart` — upload/process/confirm
  contracts.

`flutter analyze` reports no issues and all mobile tests pass.

## Known limitations

- No live backend in widget tests; HTTP is mocked.
- `authTokenProvider` must be overridden in tests because
  `flutter_secure_storage` has no test implementation.
- `image_picker` requires a device/emulator; camera capture is not
  exercised in widget tests.
- Screen-level integration with a running backend was not exercised;
  validate on-device with `FITME_API_BASE_URL` set.
