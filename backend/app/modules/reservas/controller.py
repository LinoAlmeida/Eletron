from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import Usuario
from app.modules.auth.service import get_current_user
from app.modules.reservas.schemas import ReservaDetalheOut, ReservaListResponse
from app.modules.reservas.service import ReservaService

router = APIRouter()


@router.get("", response_model=ReservaListResponse)
def listar_reservas(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> ReservaListResponse:
    service = ReservaService(db)
    return service.listar(limit=limit, offset=offset, usuario=usuario)


@router.get("/{reserva_id}", response_model=ReservaDetalheOut)
def detalhe_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> ReservaDetalheOut:
    service = ReservaService(db)
    return service.detalhe(reserva_id=reserva_id, usuario=usuario)
