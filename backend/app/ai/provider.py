"""AI provider abstraction and capability routing.

Layered like:

    AIProvider (interface)
    ├── OpenAICompatibleProvider  (shared implementation for OpenAI-style APIs)
    │   ├── OpenAIProvider
    │   └── OpenRouterFreeProvider
    └── OtherProvider             (future providers extend the interface)

Each provider advertises the capabilities it can serve (coach chat,
vision extraction). A ``ProviderRegistry`` holds every configured
provider and resolves the right one per capability, so the application
can route vision work to a model that is strong at images and coaching
work to a model that is strong at reasoning. Add a new provider by
subclassing ``AIProvider`` (or ``OpenAICompatibleProvider``) and
registering it in :func:`build_provider_registry`.
"""

from __future__ import annotations

import base64
import json
from abc import ABC, abstractmethod
from enum import Enum

import openai

from app.ai.client import LLMResult, ToolCall
from app.ai.prompts import VISION_SYSTEM_PROMPT
from app.ai.vision import VisionMenuItem, parse_vision_response


class AICapability(Enum):
    COACH = "coach"
    VISION = "vision"


class AIProvider(ABC):
    """Contract every model provider must implement."""

    name: str

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[AICapability]:
        """Capabilities this provider can serve."""

    @abstractmethod
    async def complete(
        self,
        *,
        messages: list[dict],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
    ) -> LLMResult:
        """Chat completion (coach capability)."""

    @abstractmethod
    async def extract_menu_items(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[VisionMenuItem]:
        """Vision extraction (menu capability)."""


class OpenAICompatibleProvider(AIProvider):
    """Shared implementation for OpenAI and OpenAI-compatible chat APIs.

    ``base_url`` defaults to the official OpenAI endpoint; OpenRouter and
    other compatible gateways pass their own base URL. The model used is
    selected per capability so a single provider can route vision work
    and coach work to different models.
    """

    def __init__(
        self,
        *,
        name: str,
        api_key: str,
        coach_model: str,
        vision_model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.name = name
        self.model = coach_model
        self._coach_model = coach_model
        self._vision_model = vision_model
        self._client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    @property
    def capabilities(self) -> frozenset[AICapability]:
        caps = {AICapability.COACH}
        if self._vision_model:
            caps.add(AICapability.VISION)
        return frozenset(caps)

    async def complete(
        self,
        *,
        messages: list[dict],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
    ) -> LLMResult:
        kwargs: dict = {
            "model": self._coach_model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        if response_format:
            kwargs["response_format"] = response_format

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls: list[ToolCall] = []
        for call in choice.message.tool_calls or []:
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            if not isinstance(arguments, dict):
                arguments = {}
            tool_calls.append(ToolCall(id=call.id, name=call.function.name, arguments=arguments))

        return LLMResult(content=choice.message.content, tool_calls=tool_calls)

    async def extract_menu_items(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[VisionMenuItem]:
        if self._vision_model is None:
            raise NotImplementedError(f"Provider '{self.name}' does not support vision extraction.")

        mime_type = content_type.split(";")[0].strip() or "image/jpeg"
        base64_image = base64.b64encode(image_bytes).decode("ascii")

        response = await self._client.chat.completions.create(
            model=self._vision_model,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        return parse_vision_response(content)


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(
        self,
        *,
        api_key: str,
        coach_model: str,
        vision_model: str | None = None,
    ) -> None:
        super().__init__(
            name="openai",
            api_key=api_key,
            coach_model=coach_model,
            vision_model=vision_model,
        )


class OpenRouterFreeProvider(OpenAICompatibleProvider):
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        *,
        api_key: str,
        coach_model: str,
        vision_model: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        super().__init__(
            name="openrouter",
            api_key=api_key,
            coach_model=coach_model,
            vision_model=vision_model,
            base_url=base_url,
        )


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def get(
        self,
        capability: AICapability,
        *,
        preferred: str | None = None,
    ) -> AIProvider | None:
        """Resolve a provider for a capability.

        When ``preferred`` is a provider name it wins if it supports the
        capability; otherwise the first configured provider that supports
        the capability is returned.
        """
        if preferred:
            provider = self._providers.get(preferred)
            if provider is not None and capability in provider.capabilities:
                return provider
            return None
        for provider in self._providers.values():
            if capability in provider.capabilities:
                return provider
        return None


def build_provider_registry(settings) -> ProviderRegistry:
    """Build the registry from configured API keys.

    Only providers with an API key are registered, so an unset
    OpenRouter key does not shadow a configured OpenAI key and vice
    versa. ``getattr`` keeps partial test doubles working.
    """
    registry = ProviderRegistry()

    if getattr(settings, "openrouter_api_key", None):
        registry.register(
            OpenRouterFreeProvider(
                api_key=settings.openrouter_api_key,
                coach_model=settings.openrouter_coach_model,
                vision_model=getattr(settings, "openrouter_vision_model", None),
                base_url=getattr(settings, "openrouter_base_url", OpenRouterFreeProvider.DEFAULT_BASE_URL),
            )
        )

    if getattr(settings, "openai_api_key", None):
        registry.register(
            OpenAIProvider(
                api_key=settings.openai_api_key,
                coach_model=settings.openai_model,
                vision_model=getattr(settings, "openai_vision_model", None),
            )
        )

    return registry
