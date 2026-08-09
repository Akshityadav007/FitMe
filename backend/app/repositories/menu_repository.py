from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu_image import MenuImage, MenuImageItem


class MenuRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_menu_image(self, *, user_id: str, **data: object) -> MenuImage:
        item = MenuImage(user_id=user_id, **data)
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_menu_image(self, *, menu_image_id: str) -> MenuImage | None:
        result = await self.session.execute(select(MenuImage).where(MenuImage.id == menu_image_id))
        return result.scalar_one_or_none()

    async def update_menu_image_status(self, *, menu_image_id: str, status: str) -> None:
        menu_image = await self.get_menu_image(menu_image_id=menu_image_id)
        if menu_image is not None:
            menu_image.status = status
            await self.session.flush()

    async def list_items_for_image(self, *, menu_image_id: str) -> list[MenuImageItem]:
        result = await self.session.execute(
            select(MenuImageItem)
            .where(MenuImageItem.menu_image_id == menu_image_id)
            .order_by(MenuImageItem.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_item(self, *, menu_item_id: str) -> MenuImageItem | None:
        result = await self.session.execute(
            select(MenuImageItem).where(MenuImageItem.id == menu_item_id)
        )
        return result.scalar_one_or_none()

    async def create_item(self, *, menu_image_id: str, **data: object) -> MenuImageItem:
        entry = MenuImageItem(menu_image_id=menu_image_id, **data)
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_items_for_date(self, *, user_id: str, target_date: date) -> list[MenuImageItem]:
        start = datetime.combine(target_date, time.min, tzinfo=UTC)
        end = start + timedelta(days=1)
        result = await self.session.execute(
            select(MenuImageItem)
            .join(MenuImage, MenuImageItem.menu_image_id == MenuImage.id)
            .where(
                MenuImage.user_id == user_id,
                MenuImage.created_at >= start,
                MenuImage.created_at < end,
            )
            .order_by(MenuImageItem.created_at.asc())
        )
        return list(result.scalars().all())
