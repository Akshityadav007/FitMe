from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profile import get_current_user_id
from app.db.session import get_db_session
from app.schemas.menu import MenuImageCreate, MenuImageItemCreate, MenuImageItemResponse, MenuImageResponse
from app.services.menu_service import MenuService

router = APIRouter(tags=["menu-images"])


async def get_menu_service(
    db: AsyncSession = Depends(get_db_session),
) -> MenuService:
    return MenuService(db)


@router.post("/menu-images", response_model=MenuImageResponse)
async def create_menu_image(
    payload: MenuImageCreate,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> MenuImageResponse:
    response = await service.create_menu_image(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/menu-images/{menu_image_id}/items", response_model=MenuImageItemResponse)
async def create_menu_item(
    menu_image_id: str,
    payload: MenuImageItemCreate,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> MenuImageItemResponse:
    response = await service.create_item(menu_image_id=menu_image_id, payload=payload)
    await service.session.commit()
    return response


@router.get("/menu-items", response_model=list[MenuImageItemResponse])
async def list_menu_items(
    date: date = Query(..., alias="date"),
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> list[MenuImageItemResponse]:
    return await service.list_items_for_date(user_id=user_id, target_date=date)
