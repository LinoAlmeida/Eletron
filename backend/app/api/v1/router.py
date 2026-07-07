from fastapi import APIRouter

from app.modules.auth.controller import router as auth_router
from app.modules.financeiro.controller import router as financeiro_router
from app.modules.health.controller import router as health_router
from app.modules.reservas.controller import router as reservas_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(reservas_router, prefix="/reservas", tags=["reservas"])
api_router.include_router(financeiro_router, prefix="/financeiro", tags=["financeiro"])
