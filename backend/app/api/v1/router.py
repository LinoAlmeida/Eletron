from fastapi import APIRouter

from app.modules.health.controller import router as health_router
from app.modules.reservas.controller import router as reservas_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(reservas_router, prefix="/reservas", tags=["reservas"])
