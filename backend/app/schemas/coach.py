from __future__ import annotations

from pydantic import BaseModel, Field


class CoachChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class CoachMessageResponse(BaseModel):
    role: str
    content: str


class CoachChatResponse(BaseModel):
    conversation_id: str
    reply: str
    recommendation: str | None = None
    reason: str | None = None
    remaining_calories: int | None = None
    remaining_protein_g: int | None = None
    uncertainty: bool = False
    uncertainty_reason: str | None = None
    suggested_action: str | None = None
    messages: list[CoachMessageResponse] = Field(default_factory=list)
