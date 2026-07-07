from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.financeiro.service import FinanceiroService
from app.modules.financeiro.models import Titulo
from app.modules.pdv.repository import PdvRepository
from app.modules.pdv.schemas import (
    EstoqueOut,
    PdvAdicionarItemRequest,
    PdvAdicionarItemResponse,
    PdvFinalizarRequest,
    PdvFinalizarResponse,
    PdvItemOut,
    PdvTituloOut,
    ProdutoBuscaOut,
    VendedorOut,
)
from app.modules.proton.service import ProtonService
from app.modules.reservas.models import Reserva, ReservaItem


class PdvService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PdvRepository(db)

    def listar_estoques(self, usuario: Usuario) -> list[EstoqueOut]:
        empresas = self.repository.list_estoques_usuario(usuario.id)
        return [EstoqueOut.model_validate(empresa) for empresa in empresas]

    def listar_vendedores(self, filial_proton_id: int) -> list[VendedorOut]:
        vendedores = self.repository.list_vendedores_filial(filial_proton_id)
        return [VendedorOut.model_validate(vendedor) for vendedor in vendedores]

    def buscar_produto(self, *, cod_fil: int, codprod: str) -> ProdutoBuscaOut:
        codigo = codprod.strip()
        if not codigo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe o codigo do produto.")

        produto = None
        oracle_error: Exception | None = None
        try:
            produto = ProtonService(self.db).buscar_produto(cod_fil=cod_fil, codprod=codigo)
        except Exception as exc:
            oracle_error = exc
            produto = None

        if produto is None:
            try:
                produto = self.repository.buscar_produto_legacy(codigo)
            except SQLAlchemyError:
                produto = None

        if produto is None:
            if oracle_error is not None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Nao foi possivel consultar o Proton/Oracle. "
                        f"{oracle_error.__class__.__name__}: {oracle_error}"
                    ),
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado.")

        return ProdutoBuscaOut(**produto)

    def adicionar_item(
        self,
        *,
        usuario: Usuario,
        payload: PdvAdicionarItemRequest,
    ) -> PdvAdicionarItemResponse:
        turno = FinanceiroService(self.db).turno_atual(usuario=usuario)
        if turno.requerido and not turno.aberto:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turno aberto e obrigatorio.")

        estoque = self.repository.get_estoque_usuario(
            usuario_id=usuario.id,
            estoque_id=payload.estoque_id,
        )
        if estoque is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estoque invalido.")

        vendedor = self.repository.get_vendedor_filial(payload.vendedor_filial_id)
        if vendedor is None or vendedor.filial_proton_id != estoque.proton_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vendedor invalido para o estoque.")

        if payload.percentual_desconto > Decimal("5") and not (payload.motivo_desconto or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe o motivo para descontos acima de 5%.",
            )

        reserva = self._get_or_create_reserva(usuario=usuario, payload=payload, vendedor_nome=vendedor.nome)
        item = self._upsert_item(reserva=reserva, payload=payload)
        self._recalcular_totais(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        self.db.refresh(item)

        return PdvAdicionarItemResponse(
            reserva_id=reserva.id,
            item=PdvItemOut.model_validate(item),
            valor_total=reserva.valor_total or Decimal("0"),
            valor_desconto=reserva.valor_desconto or Decimal("0"),
            valor_liquido=reserva.valor_liquido or Decimal("0"),
        )

    def finalizar(
        self,
        *,
        usuario: Usuario,
        payload: PdvFinalizarRequest,
    ) -> PdvFinalizarResponse:
        turno = FinanceiroService(self.db).turno_atual(usuario=usuario)
        if turno.requerido and not turno.aberto:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turno aberto e obrigatorio.")
        if turno.caixa is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Caixa nao encontrado.")

        reserva = self.repository.get_reserva(payload.reserva_id)
        if reserva is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva nao encontrada.")

        itens = self.repository.list_itens_reserva(reserva.id)
        if not itens:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inclua ao menos um produto.")

        self._recalcular_totais(reserva)
        valor_liquido = reserva.valor_liquido or Decimal("0")
        total_pago = sum((pagamento.valor for pagamento in payload.pagamentos), Decimal("0"))
        if total_pago < valor_liquido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pagamento menor que o valor liquido.")

        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        titulos: list[Titulo] = []
        next_titulo_id = self.repository.next_titulo_id()
        for pagamento in payload.pagamentos:
            if pagamento.valor <= 0:
                continue

            if pagamento.forma.upper() == "CARTAO" and (
                pagamento.parcelas is None or pagamento.parcelas < 1
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe a quantidade de parcelas do cartao.",
                )

            forma_pagamento = self.repository.get_forma_pagamento_pdv(
                pagamento.forma,
                parcelas=pagamento.parcelas,
            )
            if forma_pagamento is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Forma de pagamento invalida: {pagamento.forma}",
                )

            titulo = Titulo(
                id=next_titulo_id,
                legacy_titulo_id=None,
                caixa_id=turno.caixa.id,
                empresa_id=reserva.empresa_id,
                reserva_id=reserva.id,
                forma_pagamento_id=forma_pagamento.id,
                valor=pagamento.valor,
                status="Finalizado",
                data=agora.date(),
                hora=agora.time().replace(microsecond=0),
            )
            titulos.append(self.repository.add_titulo(titulo))
            next_titulo_id += 1

        if not titulos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe ao menos um pagamento.")

        reserva.status = "FINALIZADA"
        reserva.total_pago = total_pago
        reserva.troco = total_pago - valor_liquido
        reserva.forma_pagamento_id = titulos[0].forma_pagamento_id

        self.db.commit()
        self.db.refresh(reserva)
        for titulo in titulos:
            self.db.refresh(titulo)

        return PdvFinalizarResponse(
            reserva_id=reserva.id,
            status=reserva.status or "FINALIZADA",
            valor_total=reserva.valor_total or Decimal("0"),
            valor_desconto=reserva.valor_desconto or Decimal("0"),
            valor_liquido=reserva.valor_liquido or Decimal("0"),
            total_pago=reserva.total_pago or Decimal("0"),
            troco=reserva.troco or Decimal("0"),
            titulos=[
                PdvTituloOut(
                    id=titulo.id,
                    forma_pagamento_id=titulo.forma_pagamento_id,
                    valor=titulo.valor,
                    status=titulo.status,
                )
                for titulo in titulos
            ],
        )

    def _get_or_create_reserva(
        self,
        *,
        usuario: Usuario,
        payload: PdvAdicionarItemRequest,
        vendedor_nome: str | None,
    ) -> Reserva:
        if payload.reserva_id is not None:
            reserva = self.repository.get_reserva(payload.reserva_id)
            if reserva is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva nao encontrada.")
            return reserva

        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        observacoes = []
        if payload.mezanino:
            observacoes.append("Mezanino: S")

        reserva = Reserva(
            id=self.repository.next_reserva_id(),
            legacy_reserva_id=None,
            empresa_id=payload.estoque_id,
            data=agora.date(),
            hora=agora.time().replace(microsecond=0),
            vendedor_id=payload.vendedor_filial_id,
            vendedor_nome=vendedor_nome,
            status="ABERTA",
            forma_pagamento_id=None,
            valor_total=Decimal("0"),
            valor_desconto=Decimal("0"),
            valor_liquido=Decimal("0"),
            total_pago=Decimal("0"),
            troco=Decimal("0"),
            observacao="; ".join(observacoes) or None,
        )
        return self.repository.add_reserva(reserva)

    def _upsert_item(self, *, reserva: Reserva, payload: PdvAdicionarItemRequest) -> ReservaItem:
        produto_codigo = str(payload.produto_codigo)
        quantidade = payload.quantidade or Decimal("1")
        valor_unitario = payload.valor_unitario
        percentual_desconto = payload.percentual_desconto or Decimal("0")

        item = self.repository.get_item_by_produto(
            reserva_id=reserva.id,
            produto_codigo=produto_codigo,
        )
        if item is None:
            item = ReservaItem(
                id=self.repository.next_reserva_item_id(),
                legacy_item_id=None,
                reserva_id=reserva.id,
                produto_codigo=produto_codigo,
                produto_nome=payload.produto_nome,
                valor_unitario=valor_unitario,
                quantidade=quantidade,
                percentual_desconto=percentual_desconto,
                grupo_codigo=None,
                grupo_descricao=None,
                tamanho=payload.referencia,
            )
            self._atualizar_totais_item(item)
            return self.repository.add_item(item)

        item.quantidade = (item.quantidade or Decimal("0")) + quantidade
        item.valor_unitario = valor_unitario
        item.percentual_desconto = percentual_desconto
        self._atualizar_totais_item(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def _atualizar_totais_item(self, item: ReservaItem) -> None:
        valor_total = (item.valor_unitario or Decimal("0")) * (item.quantidade or Decimal("0"))
        valor_desconto = valor_total * ((item.percentual_desconto or Decimal("0")) / Decimal("100"))
        item.valor_total = valor_total
        item.valor_desconto = valor_desconto
        item.valor_final = valor_total - valor_desconto

    def _recalcular_totais(self, reserva: Reserva) -> None:
        itens = self.repository.list_itens_reserva(reserva.id)
        reserva.valor_total = sum((item.valor_total or Decimal("0") for item in itens), Decimal("0"))
        reserva.valor_desconto = sum((item.valor_desconto or Decimal("0") for item in itens), Decimal("0"))
        reserva.valor_liquido = sum((item.valor_final or Decimal("0") for item in itens), Decimal("0"))
