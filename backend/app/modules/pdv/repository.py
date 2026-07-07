from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.modules.auth.repository import AuthRepository
from app.modules.financeiro.models import Titulo
from app.modules.proton.models import VendedorFilial
from app.modules.reservas.models import Reserva, ReservaItem
from app.modules.shared.models import Empresa, FormaPagamento


class PdvRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_estoques_usuario(self, usuario_id: int) -> list[Empresa]:
        return AuthRepository(self.db).list_empresas_usuario(usuario_id)

    def list_vendedores_filial(self, filial_proton_id: int) -> list[VendedorFilial]:
        statement = (
            self.db.query(VendedorFilial)
            .filter(
                VendedorFilial.filial_proton_id == filial_proton_id,
                VendedorFilial.ativo.is_(True),
            )
            .order_by(VendedorFilial.nome_abreviado, VendedorFilial.nome)
        )
        return list(statement)

    def get_estoque_usuario(self, *, usuario_id: int, estoque_id: int) -> Empresa | None:
        empresas = self.list_estoques_usuario(usuario_id)
        return next((empresa for empresa in empresas if empresa.id == estoque_id), None)

    def get_vendedor_filial(self, vendedor_filial_id: int) -> VendedorFilial | None:
        statement = select(VendedorFilial).where(
            VendedorFilial.id == vendedor_filial_id,
            VendedorFilial.ativo.is_(True),
        )
        return self.db.scalar(statement)

    def get_reserva(self, reserva_id: int) -> Reserva | None:
        return self.db.scalar(select(Reserva).where(Reserva.id == reserva_id))

    def get_item_by_produto(self, *, reserva_id: int, produto_codigo: str) -> ReservaItem | None:
        statement = select(ReservaItem).where(
            ReservaItem.reserva_id == reserva_id,
            ReservaItem.produto_codigo == produto_codigo,
        )
        return self.db.scalar(statement)

    def next_reserva_id(self) -> int:
        return int(self.db.scalar(select(func.coalesce(func.max(Reserva.id), 0) + 1)) or 1)

    def next_reserva_item_id(self) -> int:
        return int(self.db.scalar(select(func.coalesce(func.max(ReservaItem.id), 0) + 1)) or 1)

    def add_reserva(self, reserva: Reserva) -> Reserva:
        self.db.add(reserva)
        self.db.flush()
        self.db.refresh(reserva)
        return reserva

    def add_item(self, item: ReservaItem) -> ReservaItem:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def list_itens_reserva(self, reserva_id: int) -> list[ReservaItem]:
        statement = select(ReservaItem).where(ReservaItem.reserva_id == reserva_id)
        return list(self.db.scalars(statement))

    def next_titulo_id(self) -> int:
        return int(self.db.scalar(select(func.coalesce(func.max(Titulo.id), 0) + 1)) or 1)

    def add_titulo(self, titulo: Titulo) -> Titulo:
        self.db.add(titulo)
        self.db.flush()
        self.db.refresh(titulo)
        return titulo

    def get_forma_pagamento_pdv(self, forma: str, parcelas: int | None = None) -> FormaPagamento | None:
        forma_upper = forma.upper()
        tipo_por_forma = {
            "DINHEIRO": "DN",
            "PIX": "PX",
            "CARTAO": "CT",
            "LINK": "LK",
        }
        tipo = tipo_por_forma.get(forma_upper)
        if tipo is None:
            return None

        if forma_upper == "CARTAO":
            parcelas_cartao = parcelas or 1
            parcela_label = f"{parcelas_cartao:02d} X"
            statement = (
                select(FormaPagamento)
                .where(FormaPagamento.tipo == tipo, FormaPagamento.nome.ilike(f"%{parcela_label}%"))
                .order_by(FormaPagamento.id)
                .limit(1)
            )
            return self.db.scalar(statement)

        statement = (
            select(FormaPagamento)
            .where(FormaPagamento.tipo == tipo)
            .order_by(FormaPagamento.id)
            .limit(1)
        )
        return self.db.scalar(statement)

    def buscar_produto_legacy(self, codprod: str) -> dict | None:
        statement = text(
            """
            select
                "T061_CodProton" as codigo,
                "T061_Descricao" as nome,
                coalesce(nullif("t064_referencia", ''), nullif("t061_refSpls", '')) as referencia,
                nullif("t061_CodBarras", '') as codigo_barras,
                "T061_VlrProton" as preco_venda
            from legacy.t061_produtos
            where "T061_CodProton" = :codprod
               or "t061_CodBarras" = :codprod
            limit 1
            """
        )
        row = self.db.execute(statement, {"codprod": codprod}).mappings().first()
        if row is None:
            return None

        preco_raw = str(row["preco_venda"] or "0").replace(",", ".")
        return {
            "codigo": int(row["codigo"]),
            "nome": row["nome"],
            "referencia": row["referencia"],
            "codigo_barras": row["codigo_barras"],
            "preco_venda": Decimal(preco_raw or "0"),
        }
