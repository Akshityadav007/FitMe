from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coach import CoachConversation, CoachMessage, CoachRecommendation


class CoachRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_conversation(self, *, user_id: str, title: str | None = None) -> CoachConversation:
        conversation = CoachConversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_conversation(self, *, conversation_id: str) -> CoachConversation | None:
        result = await self.session.execute(
            select(CoachConversation).where(CoachConversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_messages(self, *, conversation_id: str, limit: int = 20) -> list[CoachMessage]:
        result = await self.session.execute(
            select(CoachMessage)
            .where(CoachMessage.conversation_id == conversation_id)
            .order_by(CoachMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_message(self, *, conversation_id: str, role: str, content: str) -> CoachMessage:
        message = CoachMessage(conversation_id=conversation_id, role=role, content=content)
        self.session.add(message)
        await self.session.flush()
        return message

    async def create_recommendation(
        self,
        *,
        user_id: str,
        date,
        meal_type: str,
        recommendation: str,
        reason: str,
        remaining_calories: int,
        remaining_protein_g: int,
        uncertainty: bool,
        suggested_action: str,
    ) -> CoachRecommendation:
        row = CoachRecommendation(
            user_id=user_id,
            date=date,
            meal_type=meal_type,
            recommendation=recommendation,
            reason=reason,
            remaining_calories=remaining_calories,
            remaining_protein_g=remaining_protein_g,
            uncertainty=uncertainty,
            suggested_action=suggested_action,
        )
        self.session.add(row)
        await self.session.flush()
        return row
