from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.auth.repository import AuthRepository
from app.modules.proton.models import VendedorFilial
from app.modules.shared.models import Empresa


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
