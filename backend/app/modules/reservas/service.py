from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.financeiro.service import get_empresa_ativa_id
from app.modules.reservas.repository import ReservaRepository
from app.modules.reservas.schemas import ReservaListResponse


class ReservaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ReservaRepository(db)

    def listar(self, *, limit: int, offset: int, usuario: Usuario) -> ReservaListResponse:
        empresa_id = get_empresa_ativa_id(self.db, usuario)
        return ReservaListResponse(
            total=self.repository.count(empresa_id=empresa_id),
            items=self.repository.list(limit=limit, offset=offset, empresa_id=empresa_id),
        )
