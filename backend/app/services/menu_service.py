from __future__ import annotations

from datetime import date

from app.core.object_storage import ObjectStorage, SecureUploadValidator
from app.repositories.food_repository import FoodRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas.food import FoodEntryWithFoodCreate
from app.schemas.menu import (
    MenuImageCreate,
    MenuImageDetailResponse,
    MenuImageItemCreate,
    MenuImageItemResponse,
    MenuImageProcessResponse,
    MenuImageResponse,
    MenuItemConfirmCreate,
)
from app.services.food_service import FoodService


class MenuService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = MenuRepository(session)
        self.food_repository = FoodRepository(session)
        self.food_service = FoodService(session)

    async def create_menu_image(self, *, user_id: str, payload: MenuImageCreate) -> MenuImageResponse:
        row = await self.repository.create_menu_image(
            user_id=user_id,
            source=payload.source,
            status=payload.status,
            image_url=payload.image_url,
        )
        return self._to_image_response(row)

    async def get_menu_image_detail(self, *, user_id: str, menu_image_id: str) -> MenuImageDetailResponse:
        row = await self.repository.get_menu_image(menu_image_id=menu_image_id)
        if row is None or row.user_id != user_id:
            raise ValueError("Menu image not found")
        items = await self.repository.list_items_for_image(menu_image_id=menu_image_id)
        return MenuImageDetailResponse(
            **self._to_image_response(row).model_dump(),
            items=[self._to_item_response(item) for item in items],
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
        return self._to_item_response(row)

    async def upload_menu_image(
        self,
        *,
        user_id: str,
        source: str,
        content_type: str,
        data: bytes,
        storage: ObjectStorage,
        validator: SecureUploadValidator,
    ) -> MenuImageResponse:
        """Persist an uploaded menu photo to object storage and create a
        pending menu image record. The caller is responsible for
        committing the session."""
        validator.validate(content_type=content_type, data=data)
        key = storage.save(data=data, content_type=content_type)
        row = await self.repository.create_menu_image(
            user_id=user_id,
            source=source,
            status="pending",
            image_url=storage.url(key=key),
        )
        return self._to_image_response(row)

    async def process_menu_image(
        self,
        *,
        user_id: str,
        menu_image_id: str,
        storage: ObjectStorage,
        extract_items,
    ) -> MenuImageProcessResponse:
        """Run vision extraction over a stored menu image and persist the
        extracted items. Sets status to 'extracted' on success."""
        row = await self.repository.get_menu_image(menu_image_id=menu_image_id)
        if row is None or row.user_id != user_id:
            raise ValueError("Menu image not found")
        if row.status not in {"pending", "failed"}:
            raise ValueError(f"Cannot process menu image in state: {row.status}")

        await self.repository.update_menu_image_status(menu_image_id=menu_image_id, status="processing")
        await self.session.flush()

        try:
            key = row.image_url.removeprefix("/uploads/")
            image_bytes = storage.open(key=key)
            items = await extract_items(image_bytes, content_type=_content_type_for_key(key))
            for item in items:
                await self.repository.create_item(
                    menu_image_id=menu_image_id,
                    name=item.name,
                    estimated_calories=item.estimated_calories,
                    estimated_protein_g=item.estimated_protein_g,
                    estimated_carbs_g=item.estimated_carbs_g,
                    estimated_fat_g=item.estimated_fat_g,
                    confidence=item.confidence,
                )
            await self.repository.update_menu_image_status(menu_image_id=menu_image_id, status="extracted")
        except Exception:
            await self.repository.update_menu_image_status(menu_image_id=menu_image_id, status="failed")
            raise

        persisted = await self.repository.list_items_for_image(menu_image_id=menu_image_id)
        return MenuImageProcessResponse(
            id=menu_image_id,
            status="extracted",
            items=[self._to_item_response(item) for item in persisted],
        )

    async def confirm_menu_item(self, *, user_id: str, menu_item_id: str, payload: MenuItemConfirmCreate) -> object:
        """Confirm an extracted menu item and log it as a food entry.

        Repeated-food detection: if the user already has a food with the
        same normalized name, its trusted nutrition is reused and the
        uncertain extracted values are NOT overwritten. Otherwise a new
        food is created from the extracted estimates."""
        item = await self.repository.get_item(menu_item_id=menu_item_id)
        if item is None:
            raise ValueError("Menu item not found")

        existing = await self.food_repository.get_food_by_name(user_id=user_id, name=item.name)
        if existing is not None:
            return await self._log_entry_from_food(
                user_id=user_id,
                food_id=existing.id,
                payload=payload,
            )

        food = await self.food_repository.create_food(
            user_id=user_id,
            name=item.name,
            serving_size_g=100.0,
            calories=item.estimated_calories,
            protein_g=item.estimated_protein_g,
            carbs_g=item.estimated_carbs_g,
            fat_g=item.estimated_fat_g,
        )
        return await self._log_entry_from_food(
            user_id=user_id,
            food_id=food.id,
            payload=payload,
        )

    async def _log_entry_from_food(self, *, user_id: str, food_id: str, payload: MenuItemConfirmCreate) -> object:
        entry_payload = FoodEntryWithFoodCreate(
            food_id=food_id,
            date=payload.date,
            meal_type=payload.meal_type,
            quantity_g=payload.quantity_g,
            notes=payload.notes,
        )
        return await self.food_service.create_entry_from_food(user_id=user_id, payload=entry_payload)

    async def list_items_for_date(self, *, user_id: str, target_date: date) -> list[MenuImageItemResponse]:
        rows = await self.repository.list_items_for_date(user_id=user_id, target_date=target_date)
        return [self._to_item_response(row) for row in rows]

    def _to_image_response(self, row) -> MenuImageResponse:
        return MenuImageResponse(
            id=row.id,
            user_id=row.user_id,
            source=row.source,
            status=row.status,
            image_url=row.image_url,
        )

    def _to_item_response(self, row) -> MenuImageItemResponse:
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


_CONTENT_TYPE_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _content_type_for_key(key: str) -> str:
    suffix = key.rsplit(".", 1)[-1].lower() if "." in key else ""
    return _CONTENT_TYPE_BY_EXTENSION.get(f".{suffix}", "image/jpeg")
