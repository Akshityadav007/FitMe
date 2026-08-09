from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profile import get_current_user_id
from app.core.object_storage import SecureUploadValidator, get_object_storage
from app.db.session import get_db_session
from app.schemas.food import FoodEntryWithFoodResponse
from app.schemas.menu import (
    MenuImageCreate,
    MenuImageDetailResponse,
    MenuImageItemCreate,
    MenuImageItemResponse,
    MenuImageProcessResponse,
    MenuImageResponse,
    MenuItemConfirmCreate,
)
from app.services.menu_service import MenuService

router = APIRouter(tags=["menu-images"])


def get_vision_extractor():
    """Return the vision extraction callback used by the menu service.

    Overridable in tests via app.dependency_overrides to avoid live API
    calls in CI."""
    from app.ai.vision import OpenAIVisionClient
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vision extraction is not configured.",
        )
    client = OpenAIVisionClient(api_key=settings.openai_api_key, model=settings.openai_vision_model)
    return client.extract_menu_items


async def get_menu_service(
    db: AsyncSession = Depends(get_db_session),
) -> MenuService:
    return MenuService(db)


def _upload_validator() -> SecureUploadValidator:
    from app.core.config import get_settings

    return SecureUploadValidator(get_settings().max_upload_bytes)


@router.post("/menu-images", response_model=MenuImageResponse)
async def create_menu_image(
    payload: MenuImageCreate,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> MenuImageResponse:
    response = await service.create_menu_image(user_id=user_id, payload=payload)
    await service.session.commit()
    return response


@router.post("/menu-images/upload", response_model=MenuImageResponse)
async def upload_menu_image(
    request: Request,
    source: str = Query(default="camera"),
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
    storage=Depends(get_object_storage),
    validator: SecureUploadValidator = Depends(_upload_validator),
) -> MenuImageResponse:
    data = await request.body()
    content_type = request.headers.get("content-type", "")
    try:
        response = await service.upload_menu_image(
            user_id=user_id,
            source=source,
            content_type=content_type,
            data=data,
            storage=storage,
            validator=validator,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    await service.session.commit()
    return response


@router.post("/menu-images/{menu_image_id}/process", response_model=MenuImageProcessResponse)
async def process_menu_image(
    menu_image_id: str,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
    storage=Depends(get_object_storage),
    extract_items=Depends(get_vision_extractor),
) -> MenuImageProcessResponse:
    try:
        response = await service.process_menu_image(
            user_id=user_id,
            menu_image_id=menu_image_id,
            storage=storage,
            extract_items=extract_items,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await service.session.commit()
    return response


@router.get("/menu-images/{menu_image_id}", response_model=MenuImageDetailResponse)
async def get_menu_image_detail(
    menu_image_id: str,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> MenuImageDetailResponse:
    try:
        return await service.get_menu_image_detail(user_id=user_id, menu_image_id=menu_image_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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


@router.post("/menu-items/{menu_item_id}/confirm", response_model=FoodEntryWithFoodResponse)
async def confirm_menu_item(
    menu_item_id: str,
    payload: MenuItemConfirmCreate,
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> FoodEntryWithFoodResponse:
    try:
        response = await service.confirm_menu_item(user_id=user_id, menu_item_id=menu_item_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await service.session.commit()
    return response


@router.get("/menu-items", response_model=list[MenuImageItemResponse])
async def list_menu_items(
    date: date = Query(..., alias="date"),
    user_id: str = Depends(get_current_user_id),
    service: MenuService = Depends(get_menu_service),
) -> list[MenuImageItemResponse]:
    return await service.list_items_for_date(user_id=user_id, target_date=date)
