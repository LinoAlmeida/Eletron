from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.financeiro.models import Caixa
from app.modules.financeiro.repository import FinanceiroRepository
from app.modules.financeiro.schemas import (
    AbrirTurnoResponse,
    CaixaListResponse,
    TurnoAtualResponse,
    TituloListResponse,
)


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

    def turno_atual(self, *, usuario: Usuario) -> TurnoAtualResponse:
        requerido = usuario.perfil_id == 1
        empresa_id = get_empresa_ativa_id(self.db, usuario)
        if not requerido or empresa_id is None:
            return TurnoAtualResponse(requerido=requerido, aberto=True, caixa=None)

        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        caixa = self.repository.get_turno_aberto(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            data_abertura=agora.date(),
        )
        return TurnoAtualResponse(requerido=True, aberto=caixa is not None, caixa=caixa)

    def abrir_turno(self, *, usuario: Usuario, valor_inicial: Decimal) -> AbrirTurnoResponse:
        if usuario.perfil_id != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Abertura de turno e necessaria apenas para operadores.",
            )

        empresa_id = get_empresa_ativa_id(self.db, usuario)
        if empresa_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario sem empresa ativa.",
            )

        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        caixa_aberto = self.repository.get_turno_aberto(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            data_abertura=agora.date(),
        )
        if caixa_aberto is not None:
            return AbrirTurnoResponse(caixa=caixa_aberto)

        caixa = Caixa(
            id=self.repository.next_caixa_id(),
            legacy_caixa_id=None,
            empresa_id=empresa_id,
            filial_proton=usuario.filial,
            usuario_id=usuario.id,
            usuario_nome=usuario.nome,
            cod_proton_usuario=usuario.cod_proton,
            data_abertura=agora.date(),
            hora_abertura=agora.time().replace(microsecond=0),
            status="1",
            valor_inicial=valor_inicial,
            valor_final=Decimal("0"),
            total_dinheiro=Decimal("0"),
            total_pix=Decimal("0"),
            total_credito=Decimal("0"),
            total_debito=Decimal("0"),
            total_sangria=Decimal("0"),
            total_link=Decimal("0"),
        )
        caixa = self.repository.add_caixa(caixa)
        self.db.commit()
        return AbrirTurnoResponse(caixa=caixa)
