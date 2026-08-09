from types import SimpleNamespace

from app.ai.provider import (
    AICapability,
    OpenAIProvider,
    OpenRouterFreeProvider,
    ProviderRegistry,
    build_provider_registry,
)


def settings(**overrides) -> SimpleNamespace:
    base = {
        "openai_api_key": None,
        "openai_model": "gpt-4o-mini",
        "openai_vision_model": "gpt-4o-mini",
        "openrouter_api_key": None,
        "openrouter_base_url": "https://openrouter.ai/api/v1",
        "openrouter_coach_model": "openrouter/free",
        "openrouter_vision_model": None,
        "ai_coach_provider": "auto",
        "ai_vision_provider": "auto",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_openai_provider_capabilities() -> None:
    provider = OpenAIProvider(
        api_key="test-key",
        coach_model="gpt-4o-mini",
        vision_model="gpt-4o-mini",
    )
    assert provider.name == "openai"
    assert provider.model == "gpt-4o-mini"
    assert AICapability.COACH in provider.capabilities
    assert AICapability.VISION in provider.capabilities


def test_openrouter_provider_defaults_to_free_router() -> None:
    provider = OpenRouterFreeProvider(
        api_key="test-key",
        coach_model="openrouter/free",
        vision_model="qwen/qwen-2.5-vl-72b-instruct:free",
    )
    assert provider.name == "openrouter"
    assert provider.model == "openrouter/free"
    assert AICapability.COACH in provider.capabilities
    assert AICapability.VISION in provider.capabilities


def test_vision_only_provider_excludes_coach() -> None:
    provider = OpenAIProvider(api_key="key", coach_model="gpt-4o-mini", vision_model=None)
    assert AICapability.COACH in provider.capabilities
    assert AICapability.VISION not in provider.capabilities


def test_registry_auto_selects_first_supporting_provider() -> None:
    registry = ProviderRegistry()
    registry.register(OpenRouterFreeProvider(api_key="k", coach_model="m"))
    registry.register(OpenAIProvider(api_key="k", coach_model="m"))
    coach = registry.get(AICapability.COACH)
    assert coach is not None
    assert coach.name == "openrouter"


def test_registry_preferred_wins() -> None:
    registry = ProviderRegistry()
    registry.register(OpenRouterFreeProvider(api_key="k", coach_model="m"))
    registry.register(OpenAIProvider(api_key="k", coach_model="m"))
    coach = registry.get(AICapability.COACH, preferred="openai")
    assert coach is not None
    assert coach.name == "openai"


def test_registry_preferred_missing_returns_none() -> None:
    registry = ProviderRegistry()
    registry.register(OpenAIProvider(api_key="k", coach_model="m"))
    assert registry.get(AICapability.COACH, preferred="unknown") is None


def test_registry_capability_not_supported_returns_none() -> None:
    registry = ProviderRegistry()
    registry.register(OpenAIProvider(api_key="k", coach_model="m", vision_model=None))
    assert registry.get(AICapability.VISION) is None
    assert registry.get(AICapability.COACH) is not None


def test_build_registry_prefers_openrouter_for_vision_when_configured() -> None:
    registry = build_provider_registry(
        settings(
            openrouter_api_key="or-key",
            openrouter_vision_model="qwen/qwen-2.5-vl-72b-instruct:free",
            openai_api_key="oa-key",
        )
    )
    coach = registry.get(AICapability.COACH)
    vision = registry.get(AICapability.VISION)
    assert coach is not None and coach.name == "openrouter"
    assert vision is not None and vision.name == "openrouter"


def test_build_registry_skips_unconfigured_providers() -> None:
    registry = build_provider_registry(settings(openai_api_key="oa-key"))
    coach = registry.get(AICapability.COACH)
    assert coach is not None
    assert coach.name == "openai"
    assert registry.get(AICapability.VISION) is not None
    assert registry.get(AICapability.VISION).name == "openai"


def test_build_registry_empty_without_keys() -> None:
    registry = build_provider_registry(settings())
    assert registry.get(AICapability.COACH) is None
    assert registry.get(AICapability.VISION) is None
