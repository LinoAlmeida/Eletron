from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.financeiro.service import get_empresa_ativa_id
from app.modules.reservas.repository import ReservaRepository
from app.modules.reservas.schemas import (
    ReservaCaixaOut,
    ReservaDetalheOut,
    ReservaListResponse,
    ReservaOut,
    ReservaTituloOut,
    ReservaTotaisOut,
)


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

    def detalhe(self, *, reserva_id: int, usuario: Usuario) -> ReservaDetalheOut:
        empresa_id = get_empresa_ativa_id(self.db, usuario)
        reserva = self.repository.get(reserva_id=reserva_id, empresa_id=empresa_id)
        if reserva is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva nao encontrada para a empresa ativa.",
            )

        itens = self.repository.list_itens(reserva_id=reserva.id)
        titulos = self.repository.list_titulos(reserva_id=reserva.id, empresa_id=empresa_id)
        caixa_ids = {titulo.caixa_id for titulo in titulos if titulo.caixa_id is not None}
        caixas = self.repository.list_caixas_by_titulos(caixa_ids=caixa_ids)

        valor_liquido = reserva.valor_liquido or Decimal("0")
        soma_itens = sum((item.valor_final or Decimal("0") for item in itens), Decimal("0"))
        soma_titulos = sum((titulo.valor or Decimal("0") for titulo in titulos), Decimal("0"))

        return ReservaDetalheOut(
            reserva=ReservaOut.model_validate(reserva),
            itens=itens,
            titulos=[
                ReservaTituloOut(
                    id=titulo.id,
                    legacy_titulo_id=titulo.legacy_titulo_id,
                    caixa_id=titulo.caixa_id,
                    forma_pagamento_id=titulo.forma_pagamento_id,
                    valor=titulo.valor,
                    status=titulo.status,
                    data=titulo.data,
                    hora=titulo.hora,
                )
                for titulo in titulos
            ],
            caixas=[
                ReservaCaixaOut(
                    id=caixa.id,
                    status=caixa.status,
                    data_abertura=caixa.data_abertura,
                    hora_abertura=caixa.hora_abertura,
                    data_fechamento=caixa.data_fechamento,
                    hora_fechamento=caixa.hora_fechamento,
                    total_dinheiro=caixa.total_dinheiro,
                    total_pix=caixa.total_pix,
                    total_credito=caixa.total_credito,
                    total_debito=caixa.total_debito,
                )
                for caixa in caixas
            ],
            totais=ReservaTotaisOut(
                soma_itens=soma_itens,
                soma_titulos=soma_titulos,
                diferenca_itens_liquido=soma_itens - valor_liquido,
                diferenca_titulos_liquido=soma_titulos - valor_liquido,
            ),
        )
