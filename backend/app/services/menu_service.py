from __future__ import annotations

from datetime import date

from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuImageCreate, MenuImageItemCreate, MenuImageItemResponse, MenuImageResponse


class MenuService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = MenuRepository(session)

    async def create_menu_image(self, *, user_id: str, payload: MenuImageCreate) -> MenuImageResponse:
        row = await self.repository.create_menu_image(
            user_id=user_id,
            source=payload.source,
            status=payload.status,
            image_url=payload.image_url,
        )
        return MenuImageResponse(
            id=row.id,
            user_id=row.user_id,
            source=row.source,
            status=row.status,
            image_url=row.image_url,
        )

    async def create_item(self, *, menu_image_id: str, payload: MenuImageItemCreate) -> MenuImageItemResponse:
        row = await self.repository.create_item(
            menu_image_id=menu_image_id,
            name=payload.name,
            estimated_calories=payload.estimated_calories,
            estimated_protein_g=payload.estimated_protein_g,
            estimated_carbs_g=payload.estimated_carbs_g,
            estimated_fat_g=payload.estimated_fat_g,
            confidence=payload.confidence,
        )
        return MenuImageItemResponse(
            id=row.id,
            menu_image_id=row.menu_image_id,
            name=row.name,
            estimated_calories=row.estimated_calories,
            estimated_protein_g=row.estimated_protein_g,
            estimated_carbs_g=row.estimated_carbs_g,
            estimated_fat_g=row.estimated_fat_g,
            confidence=row.confidence,
        )

    async def list_items_for_date(self, *, user_id: str, target_date: date) -> list[MenuImageItemResponse]:
        rows = await self.repository.list_items_for_date(user_id=user_id, target_date=target_date)
        return [
            MenuImageItemResponse(
                id=row.id,
                menu_image_id=row.menu_image_id,
                name=row.name,
                estimated_calories=row.estimated_calories,
                estimated_protein_g=row.estimated_protein_g,
                estimated_carbs_g=row.estimated_carbs_g,
                estimated_fat_g=row.estimated_fat_g,
                confidence=row.confidence,
            )
            for row in rows
        ]
