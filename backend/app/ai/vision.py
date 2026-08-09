from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Protocol

import openai

from app.ai.prompts import VISION_SYSTEM_PROMPT


@dataclass(frozen=True)
class VisionMenuItem:
    name: str
    estimated_calories: int
    estimated_protein_g: int
    estimated_carbs_g: int
    estimated_fat_g: int
    confidence: float


class VisionClient(Protocol):
    async def extract_menu_items(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[VisionMenuItem]: ...


class OpenAIVisionClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model

    async def extract_menu_items(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[VisionMenuItem]:
        mime_type = content_type.split(";")[0].strip() or "image/jpeg"
        base64_image = base64.b64encode(image_bytes).decode("ascii")

        response = await self._client.chat.completions.create(
            model=self._model,
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


def parse_vision_response(content: str) -> list[VisionMenuItem]:
    """Parse the vision model's JSON into validated menu items.

    All values are clamped to safe ranges so garbage model output cannot
    produce negative macros or confidence outside [0, 1]."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return []

    raw_items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(raw_items, list):
        return []

    items: list[VisionMenuItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        if not name:
            continue
        items.append(
            VisionMenuItem(
                name=name,
                estimated_calories=max(0, int(raw.get("estimated_calories") or 0)),
                estimated_protein_g=max(0, int(raw.get("estimated_protein_g") or 0)),
                estimated_carbs_g=max(0, int(raw.get("estimated_carbs_g") or 0)),
                estimated_fat_g=max(0, int(raw.get("estimated_fat_g") or 0)),
                confidence=min(1.0, max(0.0, float(raw.get("confidence") or 0.0))),
            )
        )
    return items
