from __future__ import annotations

import argparse
import os
from datetime import date, time
from decimal import Decimal, InvalidOperation


def to_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(Decimal(value.strip()))


def to_decimal(value: str | None) -> Decimal | None:
    if value is None or value.strip() == "":
        return None
    try:
        return Decimal(value.strip().replace(",", "."))
    except InvalidOperation:
        return None


def to_date(value: str | None) -> date | None:
    if value is None:
        return None
    raw = value.strip()
    if len(raw) != 8:
        return None
    return date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))


def to_time(value: str | None) -> time | None:
    if value is None:
        return None
    raw = value.strip().zfill(6)
    if len(raw) != 6:
        return None
    return time(int(raw[0:2]), int(raw[2:4]), int(raw[4:6]))


def transform_empresas(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE empresas RESTART IDENTITY CASCADE")
        cur.execute(
            """
            SELECT
                "t000_Empresa_ID",
                "t000_Id_Proton",
                "t000_Fantasia",
                "t000_Cnpj",
                "t000_Ativa"
            FROM legacy.t000_empresas
            """
        )
        rows = cur.fetchall()
        cur.executemany(
            """
            INSERT INTO empresas (id, legacy_empresa_id, proton_id, fantasia, cnpj, ativa)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    to_int(row[0]),
                    to_int(row[0]),
                    to_int(row[1]),
                    row[2] or "Sem nome",
                    row[3] or None,
                    (row[4] or "1").strip() not in {"0", "False", "false"},
                )
                for row in rows
            ],
        )


def transform_formas_pagamento(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE formas_pagamento RESTART IDENTITY CASCADE")
        cur.execute(
            """
            SELECT
                "T010_FormaPag_ID",
                "t010_Forma",
                "t010_percDesc",
                "t010_Tipo"
            FROM legacy.t010_formapagamento
            """
        )
        rows = cur.fetchall()
        cur.executemany(
            """
            INSERT INTO formas_pagamento
                (id, legacy_forma_pagamento_id, nome, percentual_desconto, tipo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (
                    to_int(row[0]),
                    to_int(row[0]),
                    row[1] or "Sem nome",
                    row[2] or None,
                    row[3] or None,
                )
                for row in rows
            ],
        )


def transform_reservas(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE reservas RESTART IDENTITY CASCADE")
        cur.execute(
            """
            SELECT
                "T020_ReservaProduto_ID",
                "T000_Empresa_ID",
                "T020_Data",
                "T020_Hora",
                "T020_vend_id",
                "T020_vendedor",
                "T020_Status",
                "T010_FormaPag_ID",
                "T020_VlrTot",
                "T020_VlrDes",
                "T020_VlrLiq",
                "T020_TotalPago",
                "T020_Troco",
                "T020_Obrs"
            FROM legacy.t020_reservaprodutos
            """
        )
        rows = cur.fetchall()
        cur.executemany(
            """
            INSERT INTO reservas (
                id, legacy_reserva_id, empresa_id, data, hora, vendedor_id, vendedor_nome,
                status, forma_pagamento_id, valor_total, valor_desconto, valor_liquido,
                total_pago, troco, observacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    to_int(row[0]),
                    to_int(row[0]),
                    to_int(row[1]),
                    to_date(row[2]),
                    to_time(row[3]),
                    to_int(row[4]),
                    (row[5] or "").strip() or None,
                    row[6] or None,
                    to_int(row[7]),
                    to_decimal(row[8]),
                    to_decimal(row[9]),
                    to_decimal(row[10]),
                    to_decimal(row[11]),
                    to_decimal(row[12]),
                    row[13] or None,
                )
                for row in rows
            ],
        )


def transform_reserva_itens(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE reserva_itens RESTART IDENTITY")
        cur.execute(
            """
            SELECT
                "T021_ItensReserva_ID",
                "T020_ReservaProduto_ID",
                "T021_CodProd",
                "T021_NomProd",
                "T021_VlrProd",
                "T021_Qtd",
                "T021_Total",
                "T021_PercDesc",
                "T021_VlrDesc",
                "T021_VlrFinal",
                "T021_GrupoMerc",
                "T021_DscGrupo",
                "T021_Tamanho"
            FROM legacy.t021_itesreserva
            """
        )
        rows = cur.fetchall()
        cur.executemany(
            """
            INSERT INTO reserva_itens (
                id, legacy_item_id, reserva_id, produto_codigo, produto_nome, valor_unitario,
                quantidade, valor_total, percentual_desconto, valor_desconto, valor_final,
                grupo_codigo, grupo_descricao, tamanho
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    to_int(row[0]),
                    to_int(row[0]),
                    to_int(row[1]),
                    row[2] or None,
                    row[3] or None,
                    to_decimal(row[4]),
                    to_decimal(row[5]),
                    to_decimal(row[6]),
                    to_decimal(row[7]),
                    to_decimal(row[8]),
                    to_decimal(row[9]),
                    row[10] or None,
                    row[11] or None,
                    row[12] or None,
                )
                for row in rows
            ],
        )


def main() -> None:
    import psycopg

    parser = argparse.ArgumentParser(description="Transforma tabelas legacy para o modelo inicial.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("LEGACY_DATABASE_URL", "postgresql://eletron:eletron_dev@127.0.0.1:5432/eletron"),
    )
    args = parser.parse_args()

    with psycopg.connect(args.database_url) as conn:
        transform_empresas(conn)
        print("empresas transformadas")
        transform_formas_pagamento(conn)
        print("formas_pagamento transformadas")
        transform_reservas(conn)
        print("reservas transformadas")
        transform_reserva_itens(conn)
        print("reserva_itens transformados")

    print("Transformacao inicial concluida.")


if __name__ == "__main__":
    main()
