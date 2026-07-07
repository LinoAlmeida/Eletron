from __future__ import annotations

import argparse
import os
import re
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


def normalize_username(nome: str, usuario_id: int) -> str:
    base = re.sub(r"[^a-z0-9]+", ".", nome.strip().lower()).strip(".")
    return base or f"usuario.{usuario_id}"


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


def transform_caixas(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE caixas RESTART IDENTITY CASCADE")
        cur.execute("SELECT id FROM empresas")
        empresa_ids = {row[0] for row in cur.fetchall()}
        cur.execute("SELECT id FROM usuarios")
        usuario_ids = {row[0] for row in cur.fetchall()}

        cur.execute(
            """
            SELECT
                "T030_CaixaID",
                "T030_FilialPro",
                "T030_DataAb",
                "T030_HorAb",
                "T030_Usuario",
                "T030_VlrInicial",
                "T030_VlrFinal",
                "T030_Status",
                "T030_TotRS",
                "T030_TotPix",
                "T030_TotCre",
                "T030_TotDeb",
                "T030_DataFe",
                "T030_HoraFe",
                "T000_Empresa_ID",
                "T005_Usuarios_ID",
                "T005_CodPronton",
                "T030_TotSangria",
                "T030_TotLink"
            FROM legacy.t030_caixa
            """
        )
        rows = cur.fetchall()
        caixas = []
        for row in rows:
            caixa_id = to_int(row[0])
            if caixa_id is None:
                continue

            empresa_id = to_int(row[14])
            usuario_id = to_int(row[15])
            caixas.append(
                (
                    caixa_id,
                    caixa_id,
                    empresa_id if empresa_id in empresa_ids else None,
                    to_int(row[1]),
                    usuario_id if usuario_id in usuario_ids else None,
                    row[4] or None,
                    to_int(row[16]),
                    to_date(row[2]),
                    to_time(row[3]),
                    to_date(row[12]),
                    to_time(row[13]),
                    row[7] or None,
                    to_decimal(row[5]),
                    to_decimal(row[6]),
                    to_decimal(row[8]),
                    to_decimal(row[9]),
                    to_decimal(row[10]),
                    to_decimal(row[11]),
                    to_decimal(row[17]),
                    to_decimal(row[18]),
                )
            )

        cur.executemany(
            """
            INSERT INTO caixas (
                id, legacy_caixa_id, empresa_id, filial_proton, usuario_id, usuario_nome,
                cod_proton_usuario, data_abertura, hora_abertura, data_fechamento,
                hora_fechamento, status, valor_inicial, valor_final, total_dinheiro,
                total_pix, total_credito, total_debito, total_sangria, total_link
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            caixas,
        )


def transform_titulos(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE titulos RESTART IDENTITY")
        cur.execute("SELECT id FROM caixas")
        caixa_ids = {row[0] for row in cur.fetchall()}
        cur.execute("SELECT id FROM empresas")
        empresa_ids = {row[0] for row in cur.fetchall()}
        cur.execute("SELECT id FROM reservas")
        reserva_ids = {row[0] for row in cur.fetchall()}
        cur.execute("SELECT id FROM formas_pagamento")
        forma_pagamento_ids = {row[0] for row in cur.fetchall()}

        cur.execute(
            """
            SELECT
                "T030_Titulo_ID",
                "T030_CaixaID",
                "t000_Empresa_ID",
                "T020_ReservaProduto_ID",
                "T010_FormaPag_ID",
                "t030_Valor",
                "t030_qrcodeid",
                "t030_qrcode",
                "T030_Status",
                "t030_Hora",
                "T030_Data",
                "T030_DataCanc",
                "T030_HoraCanc",
                "T030_DataAprov",
                "T030_HoraAprov",
                "t030_LVOrderPay",
                "t030_LVidAsaas",
                "t030_LVurl",
                "t030_LVTipo",
                "t030_CodAut",
                "t030_CodAutPix"
            FROM legacy.t030_titulo
            """
        )
        rows = cur.fetchall()
        titulos = []
        for row in rows:
            titulo_id = to_int(row[0])
            if titulo_id is None:
                continue

            caixa_id = to_int(row[1])
            empresa_id = to_int(row[2])
            reserva_id = to_int(row[3])
            forma_pagamento_id = to_int(row[4])
            titulos.append(
                (
                    titulo_id,
                    titulo_id,
                    caixa_id if caixa_id in caixa_ids else None,
                    empresa_id if empresa_id in empresa_ids else None,
                    reserva_id if reserva_id in reserva_ids else None,
                    forma_pagamento_id if forma_pagamento_id in forma_pagamento_ids else None,
                    to_decimal(row[5]),
                    row[8] or None,
                    to_date(row[10]),
                    to_time(row[9]),
                    to_date(row[11]),
                    to_time(row[12]),
                    to_date(row[13]),
                    to_time(row[14]),
                    row[6] or None,
                    row[7] or None,
                    row[15] or None,
                    row[16] or None,
                    row[17] or None,
                    row[18] or None,
                    row[19] or None,
                    row[20] or None,
                )
            )

        cur.executemany(
            """
            INSERT INTO titulos (
                id, legacy_titulo_id, caixa_id, empresa_id, reserva_id, forma_pagamento_id,
                valor, status, data, hora, data_cancelamento, hora_cancelamento,
                data_aprovacao, hora_aprovacao, qrcode_id, qrcode, order_pay, asaas_id,
                url, tipo_live, cod_autorizacao, cod_autorizacao_pix
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            titulos,
        )


def transform_vendedores_filiais(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE vendedores_filiais RESTART IDENTITY")
        cur.execute(
            """
            SELECT
                "T048_VendedoresXFilial_ID",
                "t048_Pk_Proton",
                "t048_nome",
                "t048_nomAbrev",
                "t048_CpfVend",
                "t048_lnkFilial",
                "t048_Ativo"
            FROM legacy.t048_vendedoresxfilial
            """
        )
        rows = cur.fetchall()
        vendedores = []
        seen = set()
        for row in rows:
            vendedor_id = to_int(row[1])
            filial_id = to_int(row[5])
            if vendedor_id is None or filial_id is None:
                continue
            key = (vendedor_id, filial_id)
            if key in seen:
                continue
            seen.add(key)
            vendedores.append(
                (
                    to_int(row[0]),
                    to_int(row[0]),
                    vendedor_id,
                    row[2] or None,
                    row[3] or None,
                    row[4] or None,
                    filial_id,
                    (row[6] or "S") == "S",
                )
            )

        cur.executemany(
            """
            INSERT INTO vendedores_filiais (
                id, legacy_vendedor_filial_id, vendedor_proton_id, nome, nome_abreviado,
                cpf_cnpj, filial_proton_id, ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            vendedores,
        )


def transform_auth(conn: psycopg.Connection) -> None:
    from app.core.security import get_password_hash

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT legacy_usuario_id, senha_hash, senha_deve_alterar
            FROM usuarios
            WHERE legacy_usuario_id IS NOT NULL
            """
        )
        senhas_existentes = {
            row[0]: (row[1], row[2])
            for row in cur.fetchall()
        }

        cur.execute("TRUNCATE usuarios_empresas RESTART IDENTITY")
        cur.execute("TRUNCATE usuarios RESTART IDENTITY CASCADE")
        cur.execute("TRUNCATE perfis RESTART IDENTITY CASCADE")

        cur.execute('SELECT id FROM empresas')
        empresa_ids = {row[0] for row in cur.fetchall()}
        empresa_padrao_geral = min(empresa_ids) if empresa_ids else None

        cur.execute(
            """
            SELECT DISTINCT "T005_Tipo"
            FROM legacy.t005_usuarios
            WHERE COALESCE("T005_Tipo", '') <> ''
            ORDER BY "T005_Tipo"
            """
        )
        tipo_rows = cur.fetchall()
        perfis = [
            (to_int(row[0]), to_int(row[0]), f"Nivel {to_int(row[0])}")
            for row in tipo_rows
            if to_int(row[0]) is not None
        ]
        if not perfis:
            perfis = [(1, 1, "Usuario")]

        cur.executemany(
            """
            INSERT INTO perfis (id, legacy_nivel_id, nome)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            perfis,
        )

        perfil_ids = {perfil[0] for perfil in perfis}

        cur.execute(
            """
            SELECT
                "T005_Usuarios_ID",
                "T005_Nome",
                "T005_email",
                "T005_Cpf",
                "T005_Senha",
                "T005_CodPronton",
                "T005_Tipo",
                "T005_Filial",
                "T000_Empresa_ID"
            FROM legacy.t005_usuarios
            """
        )
        rows = cur.fetchall()
        usuarios = []
        usernames = set()
        for row in rows:
            usuario_id = to_int(row[0])
            if usuario_id is None:
                continue

            nome = (row[1] or f"Usuario {usuario_id}").strip()
            username = normalize_username(nome, usuario_id)
            if username in usernames:
                username = f"{username}.{usuario_id}"
            usernames.add(username)
            email = (row[2] or "").strip().lower() or None
            cpf = (row[3] or "").strip() or None
            legacy_senha = (row[4] or "").strip() or "alterar"
            perfil_id = to_int(row[6])
            empresa_padrao_id = to_int(row[8])
            if perfil_id not in perfil_ids:
                perfil_id = None
            if empresa_padrao_id not in empresa_ids:
                empresa_padrao_id = empresa_padrao_geral
            senha_existente = senhas_existentes.get(usuario_id)
            if senha_existente and senha_existente[1] is False:
                senha_hash = senha_existente[0]
                senha_deve_alterar = False
            else:
                senha_hash = get_password_hash(legacy_senha)
                senha_deve_alterar = True

            usuarios.append(
                (
                    usuario_id,
                    usuario_id,
                    nome,
                    username,
                    email,
                    cpf,
                    senha_hash,
                    to_int(row[5]),
                    perfil_id,
                    to_int(row[7]),
                    empresa_padrao_id,
                    True,
                    senha_deve_alterar,
                )
            )

        cur.executemany(
            """
            INSERT INTO usuarios (
                id, legacy_usuario_id, nome, username, email, cpf, senha_hash, cod_proton,
                perfil_id, filial, empresa_padrao_id, ativo, senha_deve_alterar
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            usuarios,
        )

        usuario_ids = {usuario[0] for usuario in usuarios}

        cur.execute(
            """
            SELECT
                "T009_UsuarioXEmpresaID",
                "T000_Empresa_ID",
                "T005_Usuarios_ID"
            FROM legacy.t009_usuariosxempresas
            """
        )
        rows = cur.fetchall()
        vinculos = []
        seen = set()
        next_vinculo_id = 1
        for row in rows:
            vinculo_id = to_int(row[0])
            empresa_id = to_int(row[1])
            usuario_id = to_int(row[2])
            key = (usuario_id, empresa_id)
            if (
                vinculo_id is None
                or usuario_id not in usuario_ids
                or empresa_id not in empresa_ids
                or key in seen
            ):
                continue
            seen.add(key)
            next_vinculo_id = max(next_vinculo_id, vinculo_id + 1)
            vinculos.append((vinculo_id, vinculo_id, usuario_id, empresa_id))

        for usuario in usuarios:
            usuario_id = usuario[0]
            empresa_id = usuario[10]
            key = (usuario_id, empresa_id)
            if empresa_id in empresa_ids and key not in seen:
                seen.add(key)
                vinculos.append((next_vinculo_id, None, usuario_id, empresa_id))
                next_vinculo_id += 1

        cur.executemany(
            """
            INSERT INTO usuarios_empresas
                (id, legacy_usuario_empresa_id, usuario_id, empresa_id)
            VALUES (%s, %s, %s, %s)
            """,
            vinculos,
        )


def main() -> None:
    import psycopg

    parser = argparse.ArgumentParser(description="Transforma tabelas legacy para o modelo inicial.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("LEGACY_DATABASE_URL", "postgresql://eletron:eletron_dev@127.0.0.1:5433/eletron"),
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
        transform_auth(conn)
        print("usuarios, perfis e vinculos transformados")
        transform_caixas(conn)
        print("caixas transformados")
        transform_titulos(conn)
        print("titulos transformados")
        transform_vendedores_filiais(conn)
        print("vendedores x filial transformados")

    print("Transformacao inicial concluida.")


if __name__ == "__main__":
    main()
