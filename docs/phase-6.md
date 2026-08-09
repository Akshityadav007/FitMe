# Phase 6 AI Coach

Phase 6 adds the conversational AI coach on top of the deterministic
recommendation core from Phase 5.

## What was added

- `app/ai/client.py` — `LLMClient` protocol, `OpenAIClient`, `ToolCall`,
  and `LLMResult` dataclasses.
- `app/ai/prompts.py` — versioned system prompt
  (`SYSTEM_PROMPT_VERSION = "1"`), coach prompt, and weekly review
  prompt.
- `app/ai/coach_context.py` — `build_coach_context`: a compact,
  deterministic snapshot (profile, targets, today's consumed totals,
  remaining targets, menu, recent weight/sleep/training). The LLM never
  sees the entire database.
- `app/ai/tools.py` — 13 tool definitions with server-side Pydantic
  argument validation.
- `app/services/coach_service.py` — `CoachService` tool-calling loop,
  tool dispatch, argument validation, conversation history, and error
  mapping.
- `app/repositories/coach_repository.py` — conversations, messages, and
  coach-generated recommendations.
- `app/models/coach.py` — `CoachConversation`, `CoachMessage`,
  `CoachRecommendation`.
- `POST /api/v1/coach/chat` — authenticated chat endpoint.

## Coach chat endpoint

`POST /api/v1/coach/chat` (authenticated)

``` json
{
  "message": "What should I eat for lunch?",
  "conversation_id": "optional-existing-conversation"
}
```

The service builds the system prompt with today's deterministic context,
loads recent conversation history (up to 20 messages), runs the
tool-calling loop (up to 6 rounds), then persists the user and assistant
messages. If the model returns a recommendation, it is persisted as a
`coach_recommendation`.

## Tools

- `get_user_profile`
- `get_today_summary`
- `get_remaining_targets`
- `get_today_menu`
- `get_recent_weight_trend`
- `get_recent_training`
- `get_recent_sleep`
- `log_food`
- `log_water`
- `log_weight`
- `log_sleep`
- `log_workout`
- `recommend_meal`

Every tool call is validated against a Pydantic model before any
repository or service method runs. Logging tools are guarded by the
prompt: the coach only logs when the user has explicitly stated exact
values.

## Error handling

- No `FITME_OPENAI_API_KEY` configured → `503`
- OpenAI authentication failure → `503`
- Rate limit → `429`
- Other OpenAI errors → `502`
- Tool loop exceeds `MAX_TOOL_ROUNDS` → `502`
- Unknown conversation → `404`
- Conversation owned by another user → `403`

## Configuration

- `FITME_OPENAI_API_KEY` — required for live chat
- `FITME_OPENAI_MODEL` — model name, default `gpt-4o-mini`

## Tests

`backend/tests/test_phase6_coach.py` covers the tool loop, argument
validation, message and recommendation persistence, ownership checks,
the max-rounds guard, and weekly review — all against a mocked
`LLMClient` (no live model calls in CI).
