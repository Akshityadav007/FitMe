from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol


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
