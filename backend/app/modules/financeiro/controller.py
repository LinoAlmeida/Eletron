from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import Usuario
from app.modules.auth.service import get_current_user
from app.modules.financeiro.schemas import CaixaListResponse, TituloListResponse
from app.modules.financeiro.service import FinanceiroService

router = APIRouter()


@router.get("/caixas", response_model=CaixaListResponse)
def listar_caixas(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> CaixaListResponse:
    return FinanceiroService(db).listar_caixas(usuario=usuario, limit=limit, offset=offset)


@router.get("/reservas/{reserva_id}/titulos", response_model=TituloListResponse)
def titulos_da_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> TituloListResponse:
    return FinanceiroService(db).titulos_da_reserva(reserva_id=reserva_id, usuario=usuario)
