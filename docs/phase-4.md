# Phase 4 Office Menu Capture

Phase 4 turns a photographed office menu into structured, confirmable
menu items that can be logged as food entries.

## Backend

### Object storage

- `app/core/object_storage.py` — `ObjectStorage` protocol and a local
  filesystem implementation (`LocalObjectStorage`). Keys are random
  UUIDs with an extension derived from the content type. Files are
  served under `/uploads` (mounted in `app/main.py`).
- `SecureUploadValidator` — rejects unsupported content types
  (`image/jpeg`, `image/png`, `image/webp` allowed), empty payloads,
  and uploads over `FITME_MAX_UPLOAD_BYTES` (default 10 MB).

### Vision extraction

- `app/ai/vision.py` — `VisionClient` protocol and a pure
  `parse_vision_response` helper. Output is validated and clamped so
  garbage model output cannot produce negative macros or confidence
  outside [0, 1]. The provider-backed vision implementation lives in
  `app/ai/provider.py` (`OpenAIProvider` / `OpenRouterFreeProvider`).
- `app/ai/prompts.py` — versioned vision prompt
  (`VISION_PROMPT_VERSION = "1"`). Extraction is mocked in tests via
  `app.dependency_overrides[get_vision_extractor]`.

### Endpoints

- `POST /api/v1/menu-images/upload` — accepts the raw image body with a
  `Content-Type` header, validates it, stores it, and creates a menu
  image record with status `pending`.
- `POST /api/v1/menu-images/{id}/process` — runs vision extraction and
  persists extracted items, setting status to `extracted` (or `failed`
  on error).
- `GET /api/v1/menu-images/{id}` — menu image detail with its items.
- `POST /api/v1/menu-items/{item_id}/confirm` — confirms an extracted
  item and logs it as a food entry for a given date/meal/quantity.
- Existing endpoints remain: `POST /menu-images`,
  `POST /menu-images/{id}/items`, `GET /menu-items?date=`.

### Food normalization & repeated-food detection

When an extracted item is confirmed, `MenuService.confirm_menu_item`
looks up the user's existing foods by a case-insensitive name match.
If a food already exists with trusted nutrition, that trusted data is
reused and the uncertain extracted values are never overwritten.
Otherwise a new food is created from the extracted estimates.

## Mobile

- `lib/features/menu_capture/` — models, repository, providers, and the
  capture screen.
- The screen uses `image_picker` for camera/gallery selection, uploads
  the bytes, processes them, shows extracted items, and lets the user
  confirm each one (logged as today's lunch).
- State machine in `MenuCaptureController`: idle → uploading →
  processing → done/error, with explicit loading and error views.

## Configuration

- `FITME_UPLOAD_DIR` — local upload directory (default `./data/uploads`)
- `FITME_MAX_UPLOAD_BYTES` — upload size limit (default 10 MB)
- `FITME_OPENAI_API_KEY` + `FITME_OPENAI_VISION_MODEL`, or
  `FITME_OPENROUTER_API_KEY` + `FITME_OPENROUTER_VISION_MODEL` — live
  vision provider
- `FITME_AI_VISION_PROVIDER` — `"auto"` or a specific provider name

## Tests

`backend/tests/test_phase4_menu.py` covers upload validation, the full
upload → process → confirm flow, repeated-food detection, and vision
output parsing — all with a mocked vision extractor (no live model).
