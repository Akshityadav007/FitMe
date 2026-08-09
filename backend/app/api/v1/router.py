from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.coach import router as coach_router
from app.api.v1.daily import router as daily_router
from app.api.v1.foods import router as foods_router
from app.api.v1.health import router as health_router
from app.api.v1.menu_images import router as menu_images_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.nutrition_targets import router as nutrition_targets_router
from app.api.v1.profile import router as profile_router
from app.api.v1.progress import router as progress_router
from app.api.v1.recommendations import router as recommendations_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(nutrition_targets_router)
api_router.include_router(daily_router)
api_router.include_router(foods_router)
api_router.include_router(menu_images_router)
api_router.include_router(recommendations_router)
api_router.include_router(coach_router)
api_router.include_router(notifications_router)
api_router.include_router(progress_router)
