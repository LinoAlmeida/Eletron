from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.proton.models import VendedorFilial

_oracle_client_initialized = False


def init_oracle_client_if_needed() -> None:
    global _oracle_client_initialized
    if _oracle_client_initialized or not settings.oracle_client_lib_dir:
        return

    import oracledb

    oracledb.init_oracle_client(lib_dir=settings.oracle_client_lib_dir)
    _oracle_client_initialized = True


@dataclass(frozen=True)
class VendedorFilialDTO:
    vendedor_proton_id: int
    nome: str | None
    nome_abreviado: str | None
    cpf_cnpj: str | None
    filial_proton_id: int
    ativo: bool


class ProtonService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def sincronizar_vendedores_filiais(self) -> int:
        if not settings.oracle_user or not settings.oracle_password or not settings.oracle_dsn:
            return 0

        import oracledb
        init_oracle_client_if_needed()

        query = """
            select
                a.tvnd_vendedor_pk,
                a.tvnd_nome,
                a.tvnd_nome_abreviado,
                a.tvnd_cpf_cnpj,
                b.tlnk_unidade_fk_pk,
                b.tlnk_ativo
            from tvnd_vendedor a, TLNK_VENDEDOR_UNIDADE b
            where a.tvnd_vendedor_pk = b.tlnk_vendedor_fk_pk
              and b.tlnk_ativo = 'S'
        """

        with oracledb.connect(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.oracle_dsn,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        dados = [
            VendedorFilialDTO(
                vendedor_proton_id=int(row[0]),
                nome=row[1],
                nome_abreviado=row[2],
                cpf_cnpj=row[3],
                filial_proton_id=int(row[4]),
                ativo=(row[5] == "S"),
            )
            for row in rows
        ]
        self.upsert_vendedores_filiais(dados)
        return len(dados)

    def buscar_produto(self, *, cod_fil: int, codprod: str) -> dict | None:
        if not settings.oracle_user or not settings.oracle_password or not settings.oracle_dsn:
            return None

        import oracledb
        init_oracle_client_if_needed()

        query = """
            select
                a.tmer_codigo_pri_pk,
                a.tmer_nome,
                a.tmer_referencia,
                a.tmer_codigo_barras_ukn,
                b.tmer_preco_venda
            from TMER_MERCADORIA a, tmer_estoque b
            where a.tmer_codigo_pri_pk = b.tmer_codigo_pri_fk_pk
              and b.tmer_unidade_fk_pk = :cod_fil
              and (a.tmer_codigo_pri_pk = :codprod or a.tmer_codigo_barras_ukn = :codprod)
        """

        with oracledb.connect(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.oracle_dsn,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, cod_fil=cod_fil, codprod=codprod)
                row = cursor.fetchone()

        if row is None:
            return None

        return {
            "codigo": int(row[0]),
            "nome": row[1],
            "referencia": row[2],
            "codigo_barras": row[3],
            "preco_venda": Decimal(str(row[4] or "0")),
        }

    def upsert_vendedores_filiais(self, dados: list[VendedorFilialDTO]) -> None:
        if not dados:
            return

        values = [
            {
                "vendedor_proton_id": item.vendedor_proton_id,
                "nome": item.nome,
                "nome_abreviado": item.nome_abreviado,
                "cpf_cnpj": item.cpf_cnpj,
                "filial_proton_id": item.filial_proton_id,
                "ativo": item.ativo,
            }
            for item in dados
        ]
        statement = insert(VendedorFilial).values(values)
        statement = statement.on_conflict_do_update(
            constraint="uq_vendedores_filiais_vend_filial",
            set_={
                "nome": statement.excluded.nome,
                "nome_abreviado": statement.excluded.nome_abreviado,
                "cpf_cnpj": statement.excluded.cpf_cnpj,
                "ativo": statement.excluded.ativo,
            },
        )
        self.db.execute(statement)
