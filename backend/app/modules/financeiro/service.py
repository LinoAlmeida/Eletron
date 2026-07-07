from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.financeiro.repository import FinanceiroRepository
from app.modules.financeiro.schemas import CaixaListResponse, TituloListResponse


def get_empresa_ativa_id(db: Session, usuario: Usuario) -> int | None:
    if usuario.empresa_padrao_id is not None:
        return usuario.empresa_padrao_id
    empresas = AuthRepository(db).list_empresas_usuario(usuario.id)
    return empresas[0].id if empresas else None


class FinanceiroService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = FinanceiroRepository(db)

    def titulos_da_reserva(self, *, reserva_id: int, usuario: Usuario) -> TituloListResponse:
        empresa_id = get_empresa_ativa_id(self.db, usuario)
        return TituloListResponse(
            total=self.repository.count_titulos_by_reserva(
                reserva_id=reserva_id,
                empresa_id=empresa_id,
            ),
            items=self.repository.list_titulos_by_reserva(
                reserva_id=reserva_id,
                empresa_id=empresa_id,
            ),
        )

    def listar_caixas(self, *, usuario: Usuario, limit: int, offset: int) -> CaixaListResponse:
        empresa_id = get_empresa_ativa_id(self.db, usuario)
        return CaixaListResponse(
            total=self.repository.count_caixas(empresa_id=empresa_id),
            items=self.repository.list_caixas(empresa_id=empresa_id, limit=limit, offset=offset),
        )
